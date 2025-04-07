from config import Config
from utils import get_logger

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

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    @staticmethod
    def get_openai_llm(model_name, config):
        return ChatOpenAI(
            model=model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    @staticmethod
    def get_ollama_llm(model_name, config):
        raise NotImplementedError("Ollama LLM integration is not implemented.")

