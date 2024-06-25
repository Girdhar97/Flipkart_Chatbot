import pandas as pd
from langchain_core.documents import Document
from typing import List


class DataConverter:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def convert(self) -> List[Document]:
        df = pd.read_csv(self.file_path)[["product_title", "review"]]

        # Drop rows where review is missing or empty
        df = df.dropna(subset=["review"])
        df = df[df["review"].str.strip() != ""]

        docs = [
            Document(
                page_content=row["review"],
                metadata={"product_name": row["product_title"]},
            )
            for _, row in df.iterrows()
        ]

        return docs
