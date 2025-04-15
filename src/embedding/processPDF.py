import tqdm
from utils import *
from embedding.embedder import PDFToVectorDB
from embedding.vector_store_factory import VectorStoreFactory
from embedding.embedding_factory import EmbeddingFactory
from config import Config
import json

logger = get_logger()

METADATA_KEYS = ['creationdate', 'source', 'total_pages', 'title', 'keywords']

def store_vector_ids(file_vector_ids, file_path):    
    logger.info(f"Storing vector IDs to {file_path}")
    try:
        with open(file_path, "w") as file:
            json.dump(file_vector_ids, file, indent=4)
        logger.debug("Vector IDs successfully stored.")
    except Exception as e:
        logger.error(f"Failed to store vector IDs: {e}")


def load_file_url_map(file_path):
    """
    Loads the file URL map from a CSV file and returns it as a dictionary.
    """
    logger.info(f"Loading file URL map from {file_path}")
    try:
        file_url_csv = read_file_url_mapper(file_path)
        file_url_map = {row["file"]: row["URL"] for row in file_url_csv}
        logger.debug(f"Loaded {len(file_url_map)} entries from URL map")
        return file_url_map
    except Exception as e:
        logger.error(f"Failed to load file URL map: {e}")
        raise e


def process_file(file, processor, file_url_map):
    """
    Processes a single PDF file by extracting metadata and storing vectors in the vector DB.
    """
    try:
        if file.stem in file_url_map:
            new_metadata = {
                "file_name": file.name,
                "url": file_url_map[file.stem]
                }
            # Process the PDF and store vectors in the vector DB
            ids = processor.process_pdf_and_store_in_vectorDB(
                file, mode="single", metadata_keys=METADATA_KEYS, new_metadata=new_metadata
            )
            return ids
        else:
            logger.warning(f"No URL mapping found for file: {file.name}")

    except Exception as e:
        logger.error(f"Exception while processing file {file.name}: {e}")
    return []


def process_pdfs(files, processor, file_url_map):
    """
    Processes multiple PDF files and stores their vectors in the vector database.
    """
    logger.info(f"Starting processing of {len(files)} PDF files...")

    file_vector_ids = {}
    total_ids = 0

    for file in tqdm.tqdm(files):
        if file.name not in file_vector_ids:
            ids = process_file(file, processor, file_url_map)
            if ids:
                file_vector_ids[file.name] = ids
                total_ids += len(ids)

    logger.info(f"Finished processing. Total files: {len(files)} | Total vectors added: {total_ids}")
    return file_vector_ids





def main_process_pdf(config=None):
    # Directories and file paths
    if config is None:
        config = Config.default_config()

    data_dir = config.default_data_path
    raw_data_dir = config.raw_data_path

    if not os.path.exists(raw_data_dir):
        logger.error(f"Raw data directory does not exist at {raw_data_dir}")
        return

    files = [f for f in raw_data_dir.iterdir()]
    logger.debug(f"Found {len(files)} files to process in {raw_data_dir}")

    file_url_mapper_path = data_dir / config.file_url_mapper_name
    vector_db_location = data_dir / config.vector_store_file_name

    # Load the file URL map
    file_url_map = load_file_url_map(file_url_mapper_path)

    # Initialize embedding and vector store
    embedding = EmbeddingFactory.get_embeddings_from_config()
    vector_store = VectorStoreFactory.initialize_vector_store(embedding)

    # Initialize processor
    processor = PDFToVectorDB(vector_store=vector_store, embedding=embedding)

    # Process the PDFs and save vectors
    file_vector_ids = process_pdfs(files, processor, file_url_map)
    store_vector_ids(file_vector_ids, data_dir / "vectorDB_ids.json")
    VectorStoreFactory.save_local(vector_store, config=config)
    logger.info("PDF processing and vector DB storage completed.")
