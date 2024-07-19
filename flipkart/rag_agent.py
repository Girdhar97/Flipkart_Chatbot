from typing import Any

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool

from flipkart.config import Config


def build_flipkart_retriever_tool(retriever):
    @tool
    def flipkart_retriever_tool(query: str) -> str:
        docs = retriever.invoke(query)
        return "\n\n".join(doc.page_content for doc in docs)

    return flipkart_retriever_tool


class RAGAgentBuilder:
    def __init__(
        self,
        vector_store: Any,
        top_k: int = 3,
        summarize_every: int = 10,
        keep_messages: int = 4,
    ) -> None:
        self.vector_store = vector_store
        self.top_k = top_k
        self.summarize_every = summarize_every
        self.keep_messages = keep_messages
        self.model = init_chat_model(Config.RAG_MODEL)

    def build_agent(self) -> Any:
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.top_k}
        )
        flipkart_tool = build_flipkart_retriever_tool(retriever)

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
        return agent
