import faiss
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from utils import get_logger
from config import Config

logger = get_logger()

class VectorStoreFactory:
    """Factory class to provide vector stores based on configuration."""

    @staticmethod
    def get_vector_store_from_config(embedding, config=None):
        """
        Given a config, returns the corresponding vector store.
        """
        if config is None:
            config = Config.default_config()

        vector_store_type = config.vector_store_type

        if vector_store_type == "in_memory":
            return VectorStoreFactory.get_in_memory_vector_store(embedding)

        elif vector_store_type == "faiss":
            file_name = config.vector_store_file_name
            if file_name is None:
                return VectorStoreFactory.initialize_vector_store(embedding)
            file_path = config.default_data_path / file_name
            return VectorStoreFactory.load_vector_db_from_local_if_exist(file_path, embedding)

        else:
            logger.warning(f"Vector store type {vector_store_type} not recognized, defaulting to InMemory.")
            return VectorStoreFactory.get_in_memory_vector_store(embedding)

    @staticmethod
    def get_in_memory_vector_store(embedding):
        return InMemoryVectorStore(embedding)

    @staticmethod
    def load_vector_db_from_local_if_exist(file_name, embedding):
        try:
            return FAISS.load_local(file_name, embedding, allow_dangerous_deserialization=True)
        except Exception as e:
            logger.error(f"Failed to load vector DB from local file {file_name}: {str(e)}")
            print("Using new FAISS vector store\n")
            return VectorStoreFactory.initialize_vector_store(embedding)

    @staticmethod
    def initialize_vector_store(embedding):
        """Initializes the vector store using FAISS and the given embedding function."""
        try:
            embedding_dim = len(embedding.embed_query("hello world"))
            index = faiss.IndexFlatL2(embedding_dim)
            return FAISS(
                embedding_function=embedding,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise ValueError(f"Failed to initialize vector store: {str(e)}")

    @staticmethod
    def save_local(vector_store, config=None):
        """
        Saves the vector store to a local file.
        """
        if config is None:
            config = Config.default_config()

        file_path = config.default_data_path / config.vector_store_file_name
        index_name = config.vector_store_index_name
        try:

            vector_store.save_local(file_path, index_name=index_name)
            logger.info(f"Vector store saved successfully to {file_path} with index name {index_name}.")
        except Exception as e:
            logger.error(f"Failed to save vector store to {file_path}: {str(e)}")
            raise ValueError(f"Failed to save vector store to {file_path}: {str(e)}")