import pathlib
from embedder import PDFToVectorDB

metadata_keys = [
 'creationdate',
 'source',
 'total_pages',
 'title',
 'keywords']

new_metadata = {"file_name": "test.pdf","url":"example.com"}

vector_db_location = pathlib.Path("")
vector_db_index_name = "Test"

processor = PDFToVectorDB()
processor.process_pdf_and_store_in_vectorDB("example.pdf")