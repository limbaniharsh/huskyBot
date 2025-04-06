from doc_loader import PDFDocLoader
from embedding_factory import EmbeddingFactory
from vector_store_factory import VectorStoreFactory
from splitter_factory import SplitterFactory
import pathlib




class PDFToVectorDB:
    def __init__(self, embedding=None, splitter=None, vector_store=None, **kwargs):
        self.kwargs = kwargs

        if embedding is None:
            embedding = EmbeddingFactory.get_embeddings_from_config()
        self.embedding = embedding

        if splitter is None:
            chunk_size = self.kwargs.get("chunk_size", 1000)
            splitter = SplitterFactory.get_splitter_from_config()
        self.splitter = splitter

        if vector_store is None:
            vector_store = VectorStoreFactory.get_vector_store_from_config(self.embedding)
        self.vector_store = vector_store

    def process_pdf_and_store_in_vectorDB(self, file_path, loader=None, metadata_keys=None, new_metadata=None, mode="page"):
        """Process PDF file, split documents, and store in the vector DB."""
        if type(file_path) == type(""):
            file_path = pathlib.Path(file_path)
        file_name = file_path.name
        documents = self.load_pdf(file_path, loader=loader, metadata_keys=metadata_keys, new_metadata=new_metadata, mode=mode)
        if len(documents) !=0:
            split_documents = self.split_documents(documents)
            return self.add_documents_to_vector_store(split_documents, file_name)

    def load_pdf(self, file_path, loader=None, metadata_keys=None, new_metadata=None, mode="page"):
        """Load the PDF file using PDFDocLoader."""
        loader = PDFDocLoader(file_path, loader=loader, metadata_keys=metadata_keys, new_metadata=new_metadata, mode=mode)
        return loader.load()

    def split_documents(self, documents):
        """Split the loaded documents."""
        return self.splitter.split_documents(documents)

    def add_documents_to_vector_store(self, documents, file_name):
        """Add the split documents to the vector store."""
        ids = self.vector_store.add_documents(documents)
        return ids



