import os
import glob
import logging
from unittest import loader
from dotenv import load_dotenv

load_dotenv(override=True)

# Document Loaders and Splitters
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Azure Vector Store & Embeddings
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

# 1. Setup Logging & Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("indexer")

def index_docs():
    """
    Reads PDFs from backend/data, chunks them, and uploads vectors to Azure AI Search.
    """
    # 2. Define Paths
    # We look for the 'data' folder relative to this script's location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, "../../backend/data")
    
    # 3. Debug: Check Environment Variables
    logger.info("=" * 60)
    logger.info("Environment Configuration Check:")
    logger.info(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"Embedding Deployment: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 
                                                   'text-embedding-3-small')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT: {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("=" * 60)
    
    # 4. Validate Required Environment Variables
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all variables are set.")
        return
    
    # 5. Initialize Embedding Model (The "Translator")
    # This turns text into numbers (vectors).
    # MUST match the model you deployed in Azure AI Foundry ("text-embedding-3-small")
    try:
        logger.info("Initializing Azure OpenAI Embeddings...")
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-08-07"),
        )
        logger.info("✓ Embeddings model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings: {e}")
        logger.error("Please verify your Azure OpenAI deployment name and endpoint.")
        return

    # Initialize the azure search
    try:
        logger.info("Initializing Azure AI Search vector store...")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=index_name,
            embedding_function=embeddings.embed_query
        )
        logger.info(f"Vector store initialized for index: {index_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Search: {e}")
        logger.error("Please verify your Azure Search endpoint, API key, and index name.")
        return

    # Find the pdfs files

    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {data_folder}. Please add PDfs files")
    logger.info(f"Found {len(pdf_files)} PDFs to process : {[os.path.basename(f) for f in pdf_files]}")

    all_splits = []

    # process each PDF file
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading:{os.path.basename(pdf_path )}...")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            # Chunking
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 200
            )
            splits = text_splitter.split_documents(raw_docs)
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)
            
            all_splits.extend(splits)
            logger.info(f"Split into {len(splits)} chunks.")

        except Exception as e:
            logger.error(f"Failed to process {pdf_path} : {e}")

        # Upload to Azure AI Search
        # Azure search accepts batches automatically vai this method
        if all_splits:
            logger.info(f"Uploading {len(all_splits)} chunks to Azure AI Search Index {index_name}...")

            try:
                vector_store.add_documents(documemnts = all_splits)
                logger.info("=" *60)
                logger.info(f"Indexing is complete knowledge is ready)")
                logger.info(f"Total chunks indexed: {len(all_splits)}")
                logger.info("=" *60)
            except Exception as e:
                logger.error(f"Failed to upload documents to Azure Search: {e}")
                logger.error("Please verify your Azure Search index configuration and API key.")
        else:
            logger.warning("No document were processed.")

if __name__ == "__main__":
    index_docs()