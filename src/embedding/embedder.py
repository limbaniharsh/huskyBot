from langchain_text_splitters import RecursiveCharacterTextSplitter
from doc_loader import PDFDocLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
import pathlib


def get_default_embeddings(model_name="sentence-transformers/all-mpnet-base-v2"):
    """Return the default embedding model."""
    return HuggingFaceEmbeddings(model_name=model_name)

def get_default_splitter(**kwargs):
    """Return the default text splitter."""
    return RecursiveCharacterTextSplitter(chunk_size=kwargs.get("chunk_size"), chunk_overlap=kwargs.get("chunk_overlap"), add_start_index=True)

def get_default_vector_store(embedding):
    """Return the default vector store."""
    return InMemoryVectorStore(embedding)


class PDFToVectorDB:
    def __init__(self, embedding=None, splitter=None, vector_store=None, **kwargs):
        self.kwargs = kwargs

        if embedding is None:
            embedding = get_default_embeddings()
        self.embedding = embedding

        if splitter is None:
            chunk_size = self.kwargs.get("chunk_size", 1000)
            splitter = get_default_splitter(chunk_size=chunk_size,
                                            chunk_overlap=self.kwargs.get("chunk_overlap", int(chunk_size / 5)))
        self.splitter = splitter

        if vector_store is None:
            vector_store = get_default_vector_store(self.embedding)
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

    def save_local(self, file, index_name):
        self.vector_store.save_local(file, index_name=index_name)


