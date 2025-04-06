import yaml

class Config:
    def __init__(self, config_file: str):
        # Load YAML data from the config file
        with open(config_file, 'r') as file:
            config_data = yaml.safe_load(file)

        # General settings
        self.app_name = config_data.get('app_name', 'HuskyBot')
        self.version = config_data.get('version', '1.0')
        self.debug = config_data.get('debug', False)

        # LLM model settings
        self.llm_model = config_data.get('llm_model', {})
        self.llm_model_provider = self.llm_model.get('provider', 'openai')
        self.llm_model_name = self.llm_model.get('name', 'gpt-4')
        self.temperature = self.llm_model.get('temperature', 0.7)
        self.max_tokens = self.llm_model.get('max_tokens', 150)
        self.api_key = self.llm_model.get('api_key', None)
        self.endpoint_url = self.llm_model.get('endpoint_url', '')
        self.local_api_endpoint = self.llm_model.get('local_api_endpoint', '')

        # Embedding settings
        self.embedding = config_data.get('embedding', {})
        self.embedding_model_provider = self.embedding.get('model_provider', 'sentence_transformers')
        self.embedding_model_name = self.embedding.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_dim = self.embedding.get('embedding_dim', 768)
        self.normalize_embeddings = self.embedding.get('normalize_embeddings', True)
        self.local_embedding_path = self.embedding.get('local_embedding_path', '')

        # Knowledge Base settings
        self.knowledge_base = config_data.get('knowledge_base', {})
        self.kb_type = self.knowledge_base.get('type', 'faiss')
        self.kb_db_path = self.knowledge_base.get('db_path', '/path/to/knowledge_base')
        self.vector_search_limit = self.knowledge_base.get('vector_search_limit', 10)

        # Retriever settings
        self.retriever = config_data.get('retriever', {})
        self.retriever_type = self.retriever.get('type', 'cosine_similarity')
        self.batch_size = self.retriever.get('batch_size', 8)
        self.top_k = self.retriever.get('top_k', 5)

        # Context settings
        self.context_window = config_data.get('context_window', 3)
        self.max_input_length = config_data.get('max_input_length', 512)
        self.answer_format = config_data.get('answer_format', 'simple')

        # API settings
        self.api = config_data.get('api', {})
        self.api_host = self.api.get('host', '0.0.0.0')
        self.api_port = self.api.get('port', 5000)

        # Logging settings
        self.logging = config_data.get('logging', {})
        self.log_level = self.logging.get('level', 'INFO')
        self.log_file = self.logging.get('log_file', 'huskybot.log')

    def __str__(self):
        return f"App: {self.app_name}, Version: {self.version}, Debug: {self.debug}, Model: {self.llm_model_name}, Provider: {self.llm_model_provider}"

    @staticmethod
    def default_config():
        # Path to the default configuration file
        file = '../config/config.yaml'
        return Config(file)  # Path to the default config file

# Example usage
if __name__ == "__main__":
    config = Config('config.yaml')  # Path to your YAML config file
    print(config)
