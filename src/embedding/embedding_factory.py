import logging
from config import Config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings


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

        if provider == "huggingface":
            return EmbeddingFactory.get_huggingface_embeddings(model_name)

        elif provider == "openai":
            return EmbeddingFactory.get_openai_embeddings(model_name)

        elif provider == "google-ai":
            return EmbeddingFactory.get_openai_embeddings(model_name)

        elif provider == "ollama":
            return EmbeddingFactory.get_openai_embeddings(model_name)

        else:
            logging.warning(f"Embedding type {provider} not recognized, defaulting to HuggingFace.")
            return EmbeddingFactory.get_huggingface_embeddings(model_name)

    @staticmethod
    def get_huggingface_embeddings(model_name):
        return HuggingFaceEmbeddings(model_name=model_name)

    @staticmethod
    def get_openai_embeddings(model_name):
        return OpenAIEmbeddings(model_name=model_name)

    @staticmethod
    def get_google_embeddings(model_name):
        return GoogleGenerativeAIEmbeddings(model_name=model_name)

    @staticmethod
    def get_ollama_embeddings(model_name):
        return OllamaEmbeddings(model_name=model_name)

