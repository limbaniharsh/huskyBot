import argparse
from config import Config
from utils import setup_logger
from embedding.processPDF import main_process_pdf
from embedding.vector_db_search import main_search_db
from scraper.scraper import main_scraper


def main():
    default_config = Config.default_config()
    logger = setup_logger(default_config)
    logger.info("HuskyBot: PDF Processor, Document Search, Scraper, and RAG-based Chatbot started.")

    # Argument parser setup
    parser = argparse.ArgumentParser(
        description="HuskyBot: PDF Processor, Document Search, Scraper, and RAG-based Chatbot")

    # Add argument flags for each task
    parser.add_argument('--processpdf', action='store_true', help="Trigger PDF processing")
    parser.add_argument('--searchdoc', action='store_true', help="Trigger document search")
    parser.add_argument('--scrapedoc', action='store_true', help="Trigger document scraping")
    parser.add_argument('--runchatbot', choices=['terminal', 'web'], help="Run the RAG-based chatbot in terminal or web mode")

    # Parse arguments
    args = parser.parse_args()
    if args.processpdf:
        logger.info("Starting Process PDF")
        try:
            main_process_pdf(default_config)
            logger.info("PDF processing completed successfully.")
        except Exception as e:
            logger.error(f"Error during PDF processing: {str(e)}")

    elif args.searchdoc:
        logger.info("Starting Document Search")
        try:
            main_search_db(default_config)
            logger.info("Document search completed successfully.")
        except Exception as e:
            logger.error(f"Error during document search: {str(e)}")

    elif args.scrapedoc:
        logger.info("Starting Document Scraping")
        try:
            main_scraper(default_config)
            logger.info("Document scraping completed successfully.")
        except Exception as e:
            logger.error(f"Error during document scraping: {str(e)}")

    # # If running the RAG-based chatbot
    # elif args.runchatbot:
    #     if args.runchatbot == 'terminal':
    #         run_terminal_chatbot()  # Call the function to run chatbot in terminal mode
    #     elif args.runchatbot == 'web':
    #         run_web_chatbot()  # Call the function to run chatbot in web mode

    else:
        logger.error("Error: No valid argument provided. Use --processpdf, --searchdoc, --scrapedoc, or --runchatbot.")
        print("Error: No valid argument provided. Use -processpdf, -searchdoc, -scrapedoc, or -runchatbot.")




if __name__ == "__main__":
    main()
