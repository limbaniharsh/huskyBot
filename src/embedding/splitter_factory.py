import logging
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from config import Config


class SplitterFactory:
    """Factory class to provide text splitters based on configuration."""

    @staticmethod
    def get_splitter_from_config(config=None):
        """
        Given a config, returns the corresponding text splitter.
        """
        if config is None:
            config = Config.default_config()

        splitter_type = config.splitter_type
        chunk_size = config.chunk_size
        chunk_overlap = config.chunk_overlap

        if splitter_type == "recursive":
            return SplitterFactory.get_recursive_splitter(chunk_size, chunk_overlap)

        elif splitter_type == "character":
            return SplitterFactory.get_character_splitter(chunk_size, chunk_overlap)

        else:
            logging.warning(f"Splitter type {splitter_type} not recognized, defaulting to Recursive.")
            return SplitterFactory.get_recursive_splitter(chunk_size, chunk_overlap)

    @staticmethod
    def get_recursive_splitter(chunk_size, chunk_overlap):
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True
        )

    @staticmethod
    def get_character_splitter(chunk_size, chunk_overlap):
        return CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,)



