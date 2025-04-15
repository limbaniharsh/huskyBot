from embedding.doc_loader import PDFDocLoader
from embedding.embedding_factory import EmbeddingFactory
from embedding.vector_store_factory import VectorStoreFactory
from embedding.splitter_factory import SplitterFactory
from utils import get_logger
import pathlib

logger = get_logger()


class PDFToVectorDB:
    def __init__(self, embedding=None, splitter=None, vector_store=None, **kwargs):
        logger.info("Initializing PDFToVectorDB")

        self.kwargs = kwargs

        if embedding is None:
            logger.debug("No embedding provided. Fetching from config.")
            embedding = EmbeddingFactory.get_embeddings_from_config()
        self.embedding = embedding

        if splitter is None:
            logger.debug(f"No splitter provided. Fetching from config.")
            splitter = SplitterFactory.get_splitter_from_config()
        self.splitter = splitter

        if vector_store is None:
            logger.debug("No vector store provided. Fetching from config.")
            vector_store = VectorStoreFactory.get_vector_store_from_config(self.embedding)
        self.vector_store = vector_store

    def process_pdf_and_store_in_vectorDB(self, file_path, loader=None, metadata_keys=None, new_metadata=None, mode="page"):
        """Process PDF file, split documents, and store in the vector DB."""
        logger.info(f"Processing PDF: {file_path}")

        if type(file_path) == type(""):
            file_path = pathlib.Path(file_path)
        file_name = file_path.name

        documents = self.load_pdf(file_path, loader=loader, metadata_keys=metadata_keys, new_metadata=new_metadata, mode=mode)
        if not documents:
            logger.warning(f"No documents found in {file_path}")
            return None

        logger.debug(f"Loaded {len(documents)} documents from {file_path}")
        split_documents = self.split_documents(documents)

        logger.debug(f"Split into {len(split_documents)} chunks")

        ids = self.add_documents_to_vector_store(split_documents, file_name)
        logger.info(f"Added {len(ids)} documents to vector store for file: {file_name}")
        return ids

    def load_pdf(self, file_path, loader=None, metadata_keys=None, new_metadata=None, mode="page"):
        """Load the PDF file using PDFDocLoader."""
        loader = PDFDocLoader(file_path, loader=loader, metadata_keys=metadata_keys, new_metadata=new_metadata, mode=mode)
        return loader.load()

    def split_documents(self, documents):
        """Split the loaded documents."""
        return self.splitter.split_documents(documents)

    def add_documents_to_vector_store(self, documents, file_name):
        """Add the split documents to the vector store."""
        
        logger.debug(f"Adding documents to vector store for file: {file_name}")
        ids = self.vector_store.add_documents(documents)
        logger.debug(f"Documents added with IDs: {ids}")
        return ids



