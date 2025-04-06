import logging
import faiss
from IPython.utils.text import indent
from langchain_core.vectorstores import InMemoryVectorStore, FAISS


class VectorStoreFactory:
    """Factory class to provide vector stores based on configuration."""

    @staticmethod
    def get_vector_store_from_config(embedding, config):
        """
        Given a config, returns the corresponding vector store.
        """
        vectore_store_config = config.get("vector_store",{})
        vector_store_type = vectore_store_config.get("type", "in_memory")

        if vector_store_type == "in_memory":
            return VectorStoreFactory.get_in_memory_vector_store(embedding)

        elif vector_store_type == "faiss":
            file_name = vectore_store_config.get("file_name", None)
            if file_name is None:
                return VectorStoreFactory.initialize_vector_store(embedding)
            return VectorStoreFactory.load_vector_db_from_local_if_exist(file_name, embedding)

        else:
            logging.warning(f"Vector store type {vector_store_type} not recognized, defaulting to InMemory.")
            return VectorStoreFactory.get_in_memory_vector_store(embedding)

    @staticmethod
    def get_in_memory_vector_store(embedding):
        return InMemoryVectorStore(embedding)

    @staticmethod
    def load_vector_db_from_local_if_exist(file_name, embedding):
        try:
            return FAISS.load_local(file_name, embedding, allow_dangerous_deserialization=True)
        except Exception as e:
            logging.error(f"Failed to load vector DB from local file {file_name}: {str(e)}")
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
            logging.error(f"Failed to initialize vector store: {str(e)}")
            raise ValueError(f"Failed to initialize vector store: {str(e)}")

    @staticmethod
    def save_local(vector_store, config):
        """
        Saves the vector store to a local file.
        """
        vectore_store_config = config.get("vector_store", {})
        file = vectore_store_config.get("file")
        index_name = vectore_store_config.get("index_name")
        try:

            vector_store.save_local(file, index_name=index_name)
            logging.info(f"Vector store saved successfully to {file} with index name {index_name}.")
        except Exception as e:
            logging.error(f"Failed to save vector store to {file}: {str(e)}")
            raise ValueError(f"Failed to save vector store to {file}: {str(e)}")