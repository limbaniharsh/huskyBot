from config import Config
from embedding.vector_store_factory import VectorStoreFactory
from embedding.embedding_factory import EmbeddingFactory
from utils import get_logger

logger = get_logger()

def search_vector_db(query, vector_store, k=5, search_type="distance", keep_with_score=None, filter=None, return_score=False):
    logger.debug(f"Search query: {query}")
    logger.debug(f"Search parameters - k: {k}, search_type: {search_type}, keep_with_score: {keep_with_score}, filter: {filter}, return_score: {return_score}")
    try:
        if search_type.lower() == "distance":
            # Here, `keep_with_score` represents the distance between vectors, indicating the minimum vector distance.
            documents = vector_store.similarity_search_with_score(query, k=k, filter=filter)
            
            logger.debug(f"Found {len(documents)} documents based on distance metric.")
            if keep_with_score is None:
                if return_score:
                    return documents
                return [ doc[0] for doc in documents]
            
            filtered_documents = [doc for doc in documents if doc[1] <= keep_with_score]
            logger.debug(f"Filtered documents based on distance threshold: {len(filtered_documents)} found.")
            if return_score:
                return filtered_documents
            return [doc[0] for doc in filtered_documents]
        else:
            # Here, `keep_with_score` serves as a relevance score between vectors, indicating the minimum threshold of relevance for the vectors.
            documents = vector_store.similarity_search_with_relevance_scores(query, k=k, filter=filter)

            logger.debug(f"Found {len(documents)} documents based on relevance metric.")
            if keep_with_score is None:
                if return_score:
                    return documents
                return [ doc[0] for doc in documents]

            filtered_documents = [doc for doc in documents if doc[1] >= keep_with_score]
            logger.debug(f"Filtered documents based on relevance score threshold: {len(filtered_documents)} found.")
            if return_score:
                return filtered_documents
            return [doc[0] for doc in filtered_documents]
    except Exception as e:
        logger.error(f"Error during searching document from vectorDB: {str(e)}")
        raise e
    



def display_search_results(documents):
    """
    Display the search results (file names and their similarity scores).

    """
    for doc, score in documents:
        print(f"Document File: {doc.metadata["file_name"]}, Score: {score}\n")
        print(f"Document content: {doc.page_content}\n")
    
    print(f"SUMMARY - Number of Doc-{len(documents)}\n")
    for doc, score in documents:
        print(f"Doc name-{doc.metadata["file_name"]} and Score: {score}\n")


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
        documents = search_vector_db(query, vector_store, k=config.num_documents, search_type="relevance", keep_with_score=config.min_search_score, return_score=True)
        # Display the results
        display_search_results(documents)
        

