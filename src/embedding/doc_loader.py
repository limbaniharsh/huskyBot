from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from utils import get_logger

logger = get_logger()

def get_default_metadata_keys():
    metadata_keys = ['creationdate', 'keywords', 'source', 'title', 'total_pages']
    return metadata_keys


def get_defaultloader(file, mode):
    return PyMuPDFLoader(file, mode=mode)


class PDFDocLoader:

    def __init__(self, file_path, loader=None, metadata_keys=None, new_metadata=None, mode="page"):
        if new_metadata is None:
            new_metadata = dict()
        self.file_path = file_path
        self.metadata_keys = metadata_keys
        if loader is None:
            loader = get_defaultloader(file_path, mode)
        self.loader = loader
        self.new_metadata = new_metadata

    def load(self) -> list[Document]:
        logger.info(f"Loading documents from file: {self.file_path}")
        loader = self.loader
        docs = loader.load()
        for doc in docs:
            metadata = dict()
            if self.metadata_keys:
                metadata = {key: doc.metadata[key] for key in self.metadata_keys if key in doc.metadata}
            metadata.update(self.new_metadata)
            if len(metadata):
                doc.metadata = metadata
                
        logger.info("Document loading and metadata update completed")
        return docs

