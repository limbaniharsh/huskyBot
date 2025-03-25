import pathlib
import tqdm
from embedder import *
from processPDF import load_vector_db_from_local
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS



def search_vector_db(query, vector_store, k=5, filter=None):
    """
    Perform a search in the vector database by querying for the most similar documents.

    Parameters:
    - query (str): The search query string for which similar documents are being sought.
    - vector_store (FAISS): The FAISS vector store that contains the document vectors to search against.
    - k (int, optional): The number of nearest neighbors (documents) to return. Default is 5.
    - filter (dict, optional): A filter to apply to the search (e.g., metadata filtering). Default is None.

    Returns:
    - list: A list of the top `k` most similar documents, along with their similarity scores.
    """
    # Perform the similarity search in the vector store using the provided query and filter (if any)
    documents = vector_store.similarity_search_with_score(query, k=k, filter=filter)

    return documents


def display_search_results(documents):
    """
    Display the search results (file names and their similarity scores).

    """
    for doc, score in documents:
        print(f"Document File: {doc.metadata["file_name"]}, Score: {score}\n")
        print(f"Document content: {doc.page_content}\n")


def main():
    # Load the vector database and embedding function
    data_dir = pathlib.Path("../../data")
    vector_db_location = data_dir / "faiss_index"
    embedding = get_default_embeddings()

    # Load the vector store from disk
    vector_store = load_vector_db_from_local(vector_db_location, embedding)

    # Query to search for
    query = "example search query"

    # Perform search in the vector store
    documents = search_vector_db(query, vector_store, k=3)

    # Display the results
    display_search_results(documents)


if __name__ == "__main__":
    main()
