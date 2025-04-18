import os
from dotenv import load_dotenv
from utils.logger import get_logger
from utils.custom_exception import CustomException


logger = get_logger(__name__)


# hugging face gets automatically loaded 
try:
    logger.info("Loading environment variables from .env")
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except Exception as e:
    logger.error(f"Error loading dotenv: {str(e)}")
    raise CustomException("Failed to load .env configuration", e)


class Config:
    try:
        logger.info("Initializing Config class with environment variables")
        HF_TOKEN = os.getenv("HF_TOKEN")
        ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
        ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE")
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
        RAG_MODEL = "groq:qwen/qwen3-32b"
        
        # Validation logging
        logger.info("HF_TOKEN: present")
        logger.info("ASTRA_DB_API_ENDPOINT: present")
        logger.info("ASTRA_DB_APPLICATION_TOKEN: present")
        logger.info("ASTRA_DB_KEYSPACE: present")
        logger.info("GROQ_API_KEY: present")
        logger.info(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
        logger.info(f"RAG_MODEL: {RAG_MODEL}")
        logger.info("Config initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Config class: {str(e)}")
        raise CustomException("Failed to initialize configuration parameters", e)
