from config import Config
from utils import get_logger
import os

logger = get_logger()

class LLMFactory:
    """Factory class to provide LLMs based on configuration."""

    @staticmethod
    def get_llm_from_config(config=None):
        """
        Given a config, returns the corresponding LLM model.
        """
        if config is None:
            config = Config.default_config()

        model_name = config.llm_model_name
        provider = config.llm_model_provider

        # Dynamically selecting the provider for LLMs based on the config
        if provider == "google-ai":
            return LLMFactory.get_google_ai_llm(model_name, config)

        elif provider == "openai":
            return LLMFactory.get_openai_llm(model_name, config)

        elif provider == "ollama":
            return LLMFactory.get_ollama_llm(model_name, config)

        else:
            logger.warning(f"LLM provider {provider} not recognized, defaulting to OpenAI.")
            return LLMFactory.get_google_ai_llm(model_name, config)

    @staticmethod
    def get_google_ai_llm(model_name, config):
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        check_api_key("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    @staticmethod
    def get_openai_llm(model_name, config):
        from langchain_openai import ChatOpenAI

        check_api_key("OPENAI_API_KEY")
        return ChatOpenAI(
            model=model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    @staticmethod
    def get_ollama_llm(model_name, config):
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries
        )


def check_api_key(api_key_env_var):
    if not os.environ.get(api_key_env_var):
        logger.error(f"API key not found for {api_key_env_var}")
        raise Exception(f"API key not found for {api_key_env_var}")
