from typing import Optional

from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from flipkart.data_converter import DataConverter
from flipkart.config import Config
from utils.logger import get_logger
from utils.custom_exception import CustomException


logger = get_logger(__name__)


class DataIngestor:
    def __init__(
        self,
        data_path: str = "data/flipkart_product_review.csv",
    ) -> None:
        try:
            logger.info(f"Initializing DataIngestor with data_path: {data_path}")
            self.data_path = data_path

            self.embedding = HuggingFaceEndpointEmbeddings(
                model=Config.EMBEDDING_MODEL
            )
            logger.info(f"Embeddings initialized with model: {Config.EMBEDDING_MODEL}")

            self.vstore = AstraDBVectorStore(
                embedding=self.embedding,
                collection_name="flipkart_database",
                api_endpoint=Config.ASTRA_DB_API_ENDPOINT,
                token=Config.ASTRA_DB_APPLICATION_TOKEN,
                namespace=Config.ASTRA_DB_KEYSPACE,
            )
            logger.info("AstraDBVectorStore initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DataIngestor: {str(e)}")
            raise CustomException("Failed to initialize DataIngestor", e)

    def ingest(self, load_existing: bool = True) -> AstraDBVectorStore:
        try:
            logger.info(f"Starting ingest with load_existing: {load_existing}")
            if load_existing:
                logger.info("Returning existing vector store")
                return self.vstore

            docs = DataConverter(self.data_path).convert()
            logger.info(f"Converted {len(docs)} documents")
            
            self.vstore.add_documents(docs)
            logger.info("Documents added to AstraDB successfully")
            return self.vstore
        except Exception as e:
            logger.error(f"Error in DataIngestor.ingest(): {str(e)}")
            raise CustomException("Failed to ingest data to AstraDB", e)


if __name__ == "__main__":
    try:
        logger.info("Running DataIngestor from main")
        ingestor = DataIngestor()
        ingestor.ingest(load_existing=False)
        logger.info("Data ingestion completed successfully")
    except Exception as e:
        logger.error(f"Error running DataIngestor main: {str(e)}")
        raise CustomException("DataIngestor main execution failed", e)
