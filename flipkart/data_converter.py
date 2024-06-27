import pandas as pd
from langchain_core.documents import Document
from typing import List


class DataConverter:
    def __init__(
        self,
        file_path: str,
        title_col: str = "product_title",
        review_col: str = "review",
    ) -> None:
        self.file_path = file_path
        self.title_col = title_col
        self.review_col = review_col

    def convert(self) -> List[Document]:
        df = pd.read_csv(self.file_path)[[self.title_col, self.review_col]]

        docs = [
            Document(
                page_content=row[self.review_col],
                metadata={"product_name": row[self.title_col]},
            )
            for _, row in df.iterrows()
        ]

        return docs
