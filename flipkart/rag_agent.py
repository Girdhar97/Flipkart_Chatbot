from typing import Any

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool

from flipkart.config import Config
from utils.logger import get_logger
from utils.custom_exception import CustomException


logger = get_logger(__name__)


def build_flipkart_retriever_tool(retriever):
    try:
        logger.info("Building flipkart_retriever_tool")
        @tool
        def flipkart_retriever_tool(query: str) -> str:
            """
            Retrieve top product reviews related to the user query.
            """
            docs = retriever.invoke(query)
            return "\n\n".join(doc.page_content for doc in docs)

        logger.info("flipkart_retriever_tool created successfully")
        return flipkart_retriever_tool
    except Exception as e:
        logger.error(f"Error building flipkart_retriever_tool: {str(e)}")
        raise CustomException("Failed to build retriever tool", e)


class RAGAgentBuilder:
    def __init__(
        self,
        vector_store: Any,
        top_k: int = 3,
        summarize_every: int = 10,
        keep_messages: int = 4,
    ) -> None:
        try:
            logger.info(f"Initializing RAGAgentBuilder: top_k={top_k}, summarize_every={summarize_every}, keep_messages={keep_messages}")
            self.vector_store = vector_store
            self.top_k = top_k
            self.summarize_every = summarize_every
            self.keep_messages = keep_messages
            self.model = init_chat_model(Config.RAG_MODEL)
            logger.info("RAGAgentBuilder initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAGAgentBuilder: {str(e)}")
            raise CustomException("Failed to initialize RAGAgentBuilder", e)

    def build_agent(self) -> Any:
        try:
            logger.info("Starting agent build process")
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": self.top_k}
            )
            logger.info(f"Retriever created with top_k={self.top_k}")

            flipkart_tool = build_flipkart_retriever_tool(retriever)
            logger.info("Retriever tool created")

            agent = create_agent(
                model=self.model,
                tools=[flipkart_tool],
                system_prompt=(
                    "You're an e-commerce bot answering product-related queries "
                    "based on reviews and titles."
                ),
                checkpointer=InMemorySaver(),
                middleware=[
                    SummarizationMiddleware(
                        model=self.model,
                        trigger=("messages", self.summarize_every),
                        keep=("messages", self.keep_messages),
                    )
                ],
            )
            logger.info("RAG agent built successfully")
            return agent
        except Exception as e:
            logger.error(f"Error building RAG agent: {str(e)}")
            raise CustomException("Failed to build RAG agent", e)
