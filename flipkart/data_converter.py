import pandas as pd
from langchain_core.documents import Document
from typing import List
from utils.logger import get_logger  
from utils.custom_exception import CustomException  


logger = get_logger(__name__)  


class DataConverter:
    def __init__(
        self,
        file_path: str,
        title_col: str = "product_title",
        review_col: str = "review",
    ) -> None:
        try:  # WRAPPED
            logger.info(f"Initializing DataConverter with file: {file_path}, title_col: {title_col}, review_col: {review_col}")
            self.file_path = file_path
            self.title_col = title_col
            self.review_col = review_col
            logger.info("DataConverter initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DataConverter: {str(e)}")
            raise CustomException("Failed to initialize DataConverter", e)

    def convert(self) -> List[Document]:
        try:  # WRAPPED
            logger.info(f"Starting data conversion from file: {self.file_path}")
            df = pd.read_csv(self.file_path)[[self.title_col, self.review_col]]
            logger.info(f"Loaded DataFrame shape: {df.shape}")

            docs = [
                Document(
                    page_content=row[self.review_col],
                    metadata={"product_name": row[self.title_col]},
                )
                for _, row in df.iterrows()
            ]
            
            logger.info(f"Successfully created {len(docs)} Document objects")
            return docs
        except Exception as e:
            logger.error(f"Error in data_converter.convert(): {str(e)}")
            raise CustomException("Failed to convert CSV to Documents", e)
