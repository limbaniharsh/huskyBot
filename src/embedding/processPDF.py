import pathlib
import tqdm
from embedder import *
from utils import *
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from embedder import PDFToVectorDB


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


def save_vectors_to_disk(file_name, processor):
    """
    Saves the vector store to disk.
    """
    processor.vector_store.save_local(file_name)


def load_vector_db_from_local(file_name, embedding):
    """
    Loads the vector DB from a local file.
    """
    return FAISS.load_local(file_name, embedding, allow_dangerous_deserialization=True)


def initialize_vector_store(embedding):
    """
    Initializes the vector store using FAISS and the given embedding function.
    """
    embedding_dim = len(embedding.embed_query("hello world"))
    index = faiss.IndexFlatL2(embedding_dim)
    return FAISS(
        embedding_function=embedding,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )


def main():
    # Directories and file paths
    data_dir = pathlib.Path("../../data")
    raw_data_dir = data_dir / "raw"
    files = [f for f in raw_data_dir.iterdir()]
    file_url_mapper_path = data_dir / "FileURLMapper.csv"
    vector_db_location = data_dir / "faiss_index"

    # Load the file URL map
    file_url_map = load_file_url_map(file_url_mapper_path)

    # Initialize embedding and vector store
    embedding = get_default_embeddings()
    vector_store = initialize_vector_store(embedding)

    # Initialize processor
    processor = PDFToVectorDB(vector_store=vector_store, embedding=embedding)

    # Process the PDFs and save vectors
    process_pdfs(files, processor, file_url_map)
    save_vectors_to_disk(vector_db_location, processor)


if __name__ == "__main__":
    main()