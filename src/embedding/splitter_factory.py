import logging
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter


class SplitterFactory:
    """Factory class to provide text splitters based on configuration."""

    @staticmethod
    def get_splitter_from_config(config):
        """
        Given a config, returns the corresponding text splitter.
        """
        splitter_config = config.get("splitter",{})
        splitter_type = splitter_config.get("splitter_type", "recursive")
        chunk_size = splitter_config.get("chunk_size", 1000)
        chunk_overlap = splitter_config.get("chunk_overlap", 200)

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



