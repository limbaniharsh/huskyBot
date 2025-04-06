import tqdm
from utils import *
from embedding.embedder import PDFToVectorDB
from embedding.vector_store_factory import VectorStoreFactory
from embedding.embedding_factory import EmbeddingFactory
from config import Config

METADATA_KEYS = ['creationdate', 'source', 'total_pages', 'title', 'keywords']


def load_file_url_map(file_path):
    """
    Loads the file URL map from a CSV file and returns it as a dictionary.
    """
    file_url_csv = read_file_url_mapper(file_path)
    return {row["file"]: row["URL"] for row in file_url_csv}


def process_file(file, processor, file_url_map):
    """
    Processes a single PDF file by extracting metadata and storing vectors in the vector DB.
    """
    try:
        if file.stem in file_url_map:
            new_metadata = {"file_name": file.name, "url": file_url_map[file.stem]}
            # Process the PDF and store vectors in the vector DB
            ids = processor.process_pdf_and_store_in_vectorDB(
                file, mode="single", metadata_keys=METADATA_KEYS, new_metadata=new_metadata
            )
            return ids
    except Exception as e:
        print(f"Exception while processing file {file.name}: {e}")
    return []


def process_pdfs(files, processor, file_url_map):
    """
    Processes multiple PDF files and stores their vectors in the vector database.
    """
    file_vector_ids = {}
    total_ids = 0

    for file in tqdm.tqdm(files):
        if file.name not in file_vector_ids:
            ids = process_file(file, processor, file_url_map)
            if ids:
                file_vector_ids[file.name] = ids
                total_ids += len(ids)

    print(f"Processed {len(files)} files and added {total_ids} records to the vector DB.")
    return file_vector_ids





def main_process_pdf(config=None):
    # Directories and file paths
    if config is None:
        config = Config.default_config()

    data_dir = config.default_data_path
    raw_data_dir = config.raw_data_path

    files = [f for f in raw_data_dir.iterdir()]
    file_url_mapper_path = data_dir / config.file_url_mapper_name
    vector_db_location = data_dir / config.vector_store_file_name

    # Load the file URL map
    file_url_map = load_file_url_map(file_url_mapper_path)

    # Initialize embedding and vector store
    embedding = EmbeddingFactory.get_embeddings_from_config()
    vector_store = VectorStoreFactory.get_vector_store_from_config(embedding)

    # Initialize processor
    processor = PDFToVectorDB(vector_store=vector_store, embedding=embedding)

    # Process the PDFs and save vectors
    process_pdfs(files, processor, file_url_map)
    VectorStoreFactory.save_local(vector_db_location)
