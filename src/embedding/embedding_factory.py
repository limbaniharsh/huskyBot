from config import Config
from utils import get_logger

logger = get_logger()

class EmbeddingFactory:
    """Factory class to provide embeddings based on configuration."""

    @staticmethod
    def get_embeddings_from_config(config=None):
        """
        Given a config, returns the corresponding embedding model.
        """
        if config is None:
            config = Config.default_config()
        
        model_name = config.embedding_model_name
        provider = config.embedding_provider

        logger.info(f"Embedding provider selected: {provider}")
        logger.info(f"Embedding model selected: {model_name}")

        if provider == "huggingface":
            return EmbeddingFactory.get_huggingface_embeddings(model_name)

        elif provider == "openai":
            return EmbeddingFactory.get_openai_embeddings(model_name)

        elif provider == "google-ai":
            return EmbeddingFactory.get_openai_embeddings(model_name)

        elif provider == "ollama":
            return EmbeddingFactory.get_openai_embeddings(model_name)

        else:
            logger.warning(f"Embedding type {provider} not recognized, defaulting to HuggingFace.")
            return EmbeddingFactory.get_huggingface_embeddings(model_name)

    @staticmethod
    def get_huggingface_embeddings(model_name):
        from langchain_huggingface import HuggingFaceEmbeddings

        logger.debug(f"Creating HuggingFace embeddings with model: {model_name}")
        return HuggingFaceEmbeddings(model_name=model_name)

    @staticmethod
    def get_openai_embeddings(model_name):
        from langchain_openai import OpenAIEmbeddings

        logger.debug(f"Creating OpenAI embeddings with model: {model_name}")
        return OpenAIEmbeddings(model_name=model_name)

    @staticmethod
    def get_google_embeddings(model_name):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        logger.debug(f"Creating Google AI embeddings with model: {model_name}")
        return GoogleGenerativeAIEmbeddings(model_name=model_name)

    @staticmethod
    def get_ollama_embeddings(model_name):
        from langchain_ollama import OllamaEmbeddings

        logger.debug(f"Creating Ollama embeddings with model: {model_name}")
        return OllamaEmbeddings(model_name=model_name)

