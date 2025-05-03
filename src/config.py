import yaml
import pathlib

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
        self.llm_model_provider = self.llm_model.get('provider', 'google_ai')
        self.llm_model_name = self.llm_model.get('name', 'gemini-2.0-flash-001')
        self.temperature = self.llm_model.get('temperature', 0)
        self.max_tokens = self.llm_model.get('max_tokens', None)
        self.timeout = self.llm_model.get('timeout', None)
        self.max_retries = self.llm_model.get('max_tokens', 2)
        self.multi_turn = self.llm_model.get('multi_turn', True)


        # Embedding settings
        self.embedding = config_data.get('embedding', {})
        self.embedding_provider = self.embedding.get('provider', 'huggingface')
        self.embedding_model_name = self.embedding.get('model_name', 'sentence-transformers/all-mpnet-base-v2')

        # Splitter settings
        self.splitter = config_data.get('splitter', {})
        self.splitter_type = self.splitter.get('type', 'recursive')
        self.chunk_size = self.splitter.get('chunk_size', 1000)
        self.chunk_overlap = self.splitter.get('chunk_overlap', 200)

        # Vector store settings
        self.vector_store = config_data.get('vector_store', {})
        self.vector_store_type = self.vector_store.get('type', 'faiss')
        self.vector_store_file_name = self.vector_store.get('file_name', 'faiss_index')
        self.vector_store_index_name = self.vector_store.get('index_name', 'index')

        # Data file paths
        self.data_files = config_data.get('data_files', {})
        self.default_data_path = pathlib.Path(self.data_files.get('default_data_path', "../data"))
        self.raw_data_path = self.default_data_path / self.data_files.get('raw_data_folder', "raw")
        self.file_url_mapper_name = self.data_files.get('file_url_mapper', "FileURLMapper.csv")

        # Document search settings
        self.document_search = config_data.get('document_search', {})
        self.num_documents = self.document_search.get('num_documents', 5)  # Default to retrieving top 5 documents
        self.keep_with_score = self.document_search.get('keep_with_score', None)
        self.sim_search_type = self.document_search.get("search_type", "score")

        # Scraper settings
        self.scraper = config_data.get('scraper', {})
        self.base_url = self.scraper.get("base_url", "https://kb.uconn.edu")
        self.copy_scraper_data_to_data = self.scraper.get("copy_to_data", True)


        # Logging settings
        self.logging = config_data.get('logging', {})
        self.log_level = self.logging.get('level', 'INFO').upper()
        self.log_file = self.logging.get('log_file', 'huskybot.log')
        self.max_log_size = self.logging.get('max_log_size', '10MB')

    # def __str__(self):
    #     return (f"App: {self.app_name}, Version: {self.version}, Debug: {self.debug}, "
    #             f"Model: {self.llm_model_name}, Provider: {self.llm_model_provider}, "
    #             f"Embedding Model: {self.embedding_model_name}, Vector Store: {self.vector_store_type}")

    @staticmethod
    def default_config():
        # Path to the default configuration file
        file = '../config/config.yaml'
        return Config(file)  # Path to the default config file

# Example usage
if __name__ == "__main__":
    import pprint

    config = Config.default_config()  # Path to your YAML config file
    pprint.pprint(vars(config))
