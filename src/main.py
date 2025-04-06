import os
import logging
import argparse
from pathlib import Path
from pdf_preprocessing import download_pdf, convert_pdf_to_text
from embedding import create_embeddings, load_embeddings
from retriever import load_retriever, save_faiss_index
from llm_model import initialize_llm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGOrchestrator:
    def __init__(self, config, scrape=False, query=None):
        self.config = config
        self.scrape = scrape
        self.query = query
        self.retriever = None
        self.llm = None

    def download_and_process_pdfs(self):
        """
        Download PDFs from URLs defined in the configuration and preprocess them.
        """
        logger.info("Starting PDF download and preprocessing...")

        pdf_urls = self.config.get("pdf_urls", [])
        if not pdf_urls:
            logger.warning("No PDF URLs provided in the configuration.")
            return

        # Step 1: Download PDFs and convert them to text (only if we haven't done it already)
        for url in pdf_urls:
            pdf_path = download_pdf(url)
            text = convert_pdf_to_text(pdf_path)
            self.process_text(text)

    def process_text(self, text):
        """
        Convert text into embeddings and store them in the retriever.
        """
        logger.info("Processing text extracted from PDF...")
        embeddings = create_embeddings(text)

        # Step 2: Store embeddings in retriever
        if self.retriever:
            self.retriever.store_embeddings(embeddings)
        else:
            logger.error("Retriever is not initialized. Embeddings cannot be stored.")

    def setup_retriever(self):
        """
        Setup the retriever to store and retrieve the document embeddings.
        """
        logger.info("Setting up the retriever...")
        # Check if the FAISS index already exists
        index_path = self.config.get("retriever_config", {}).get("index_path")

        # If the FAISS index exists, load it. Otherwise, initialize an empty retriever.
        if os.path.exists(index_path):
            self.retriever = load_retriever(index_path)
        else:
            logger.warning(f"Index file {index_path} not found. A new index will be created.")
            self.retriever = load_retriever(None)  # Initialize an empty retriever

    def initialize_llm(self):
        """
        Initialize the large language model (LLM) for question answering.
        """
        logger.info("Initializing the LLM...")
        self.llm = initialize_llm(self.config["llm_config"])

    def run(self):
        """
        Orchestrates the running of the entire RAG-based pipeline.
        """
        logger.info("Starting the RAG-based chatbot pipeline...")

        # Step 1: Check if the embeddings and FAISS index exist
        embeddings_path = self.config.get("embeddings_path")
        index_path = self.config.get("retriever_config", {}).get("index_path")

        if self.scrape and (not os.path.exists(embeddings_path) or not os.path.exists(index_path)):
            # If scraping is triggered or embeddings/index are missing, process PDFs
            self.download_and_process_pdfs()
            # Step 2: Save the FAISS index after processing
            save_faiss_index(self.retriever.index, index_path)

        # Step 3: Initialize the retriever (it will load the pre-processed embeddings)
        self.setup_retriever()

        # Step 4: Initialize the LLM
        self.initialize_llm()

        logger.info("RAG system initialized successfully. Ready for queries!")

        # If there's a query, pass it to the LLM for an answer
        if self.query:
            self.answer_query(self.query)

    def answer_query(self, query):
        """
        Answer a query using the LLM and the retriever.
        """
        query_embedding = create_embeddings(query)  # Assuming the query is a single string
        relevant_docs = self.retriever.retrieve(query_embedding)
        context = [doc['text'] for doc in relevant_docs]  # Adjust based on your document structure

        answer = self.llm(query, context)
        logger.info(f"Answer: {answer}")
        print(answer)


def main():
    parser = argparse.ArgumentParser(description="RAG-based Chatbot Pipeline")

    # CLI arguments
    parser.add_argument('--scrape', action='store_true', help="Scrape and process PDFs (download & embed)")
    parser.add_argument('--skip_scrape', action='store_true', help="Skip scraping and use pre-processed data")
    parser.add_argument('--load_embeddings', type=str, help="Path to load preprocessed embeddings")
    parser.add_argument('--query', type=str, help="Query to be answered by the chatbot")

    args = parser.parse_args()

    # Example configuration (can be loaded from a file or environment variables)
    config = {
        "pdf_urls": [
            "https://example.com/document1.pdf",
            "https://example.com/document2.pdf"
        ],
        "embeddings_path": "embeddings/embeddings.pkl",  # Path to save/load embeddings
        "retriever_config": {
            "type": "faiss",
            "index_path": "faiss_index.index"  # Path to the FAISS index
        },
        "llm_config": {
            "model_name": "gpt-4",
            "provider": "openai",
            "api_key": "your_openai_api_key"
        }
    }

    # Initialize and run the RAG system with arguments passed from the command line
    orchestrator = RAGOrchestrator(config, scrape=args.scrape, query=args.query)
    orchestrator.run()


if __name__ == "__main__":
    main()
