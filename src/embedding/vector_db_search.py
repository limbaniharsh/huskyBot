from config import Config
from embedder import *



def search_vector_db(query, vector_store, k=5, min_search_score=None, filter=None, return_score=False):
    documents = vector_store.similarity_search_with_score(query, k=k, filter=filter)
    if min_search_score is None:
        if return_score:
            return documents
        return [ doc[0] for doc in documents]
    if return_score:
        return [doc for doc in documents if doc[1] >= min_search_score]
    return [doc[0] for doc in documents if doc[1] >= min_search_score]



def display_search_results(documents):
    """
    Display the search results (file names and their similarity scores).

    """
    for doc, score in documents:
        print(f"Document File: {doc.metadata["file_name"]}, Score: {score}\n")
        print(f"Document content: {doc.page_content}\n")


def main_search_db(config=None):
    # Load the vector database and embedding function

    if config is None:
        config = Config.default_config()

    embedding = EmbeddingFactory.get_embeddings_from_config(config)
    vector_store = VectorStoreFactory.get_vector_store_from_config(embedding, config)

    while True:
        query = input("Enter Query: - ")
        if query == "exit":
            break
        documents = search_vector_db(query, vector_store, k=config.num_documents, min_search_score=config.min_search_score, return_score=True)
        # Display the results
        display_search_results(documents)

