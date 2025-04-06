import argparse
from config import Config
from embedding.processPDF import main_process_pdf
from embedding.vector_db_search import main_search_db
from scraper.scraper import main_scraper


def main():
    default_config = Config.default_config()

    # Argument parser setup
    parser = argparse.ArgumentParser(
        description="HuskyBot: PDF Processor, Document Search, Scraper, and RAG-based Chatbot")

    # Add argument flags for each task
    parser.add_argument('-processpdf', type=str, help="Path to the PDF file to process")
    parser.add_argument('-searchdoc', type=str, help="Search query for documents")
    parser.add_argument('-scrapedoc', type=str, help="URL to scrape document from")
    parser.add_argument('-runchatbot', choices=['terminal', 'web'],
                        help="Run the RAG-based chatbot in terminal or web mode")

    # Parse arguments
    args = parser.parse_args()

    if args.processpdf:
        main_process_pdf(default_config)

    elif args.searchdoc:
        main_search_db(default_config)

    elif args.scrapedoc:
        url = args.scrapedoc
        main_scraper(url)

    # # If running the RAG-based chatbot
    # elif args.runchatbot:
    #     if args.runchatbot == 'terminal':
    #         run_terminal_chatbot()  # Call the function to run chatbot in terminal mode
    #     elif args.runchatbot == 'web':
    #         run_web_chatbot()  # Call the function to run chatbot in web mode

    else:
        print("Error: No valid argument provided. Use -processpdf, -searchdoc, -scrapedoc, or -runchatbot.")




if __name__ == "__main__":
    main()
