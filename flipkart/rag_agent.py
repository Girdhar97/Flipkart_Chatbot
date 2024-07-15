from typing import Any

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool

from flipkart.config import Config


SYSTEM_PROMPT = (
    "You're an e-commerce bot answering product-related queries "
    "based on reviews and titles.\n\n"
    "Always use flipkart_retriever_tool to search for relevant reviews.\n\n"
    "If you do not know an answer, politely say that you don't know and "
    "ask the user to contact our customer care at +97 98652365."
)


def build_flipkart_retriever_tool(retriever):
    @tool
    def flipkart_retriever_tool(query: str) -> str:
        docs = retriever.invoke(query)
        return "\n\n".join(doc.page_content for doc in docs)

    return flipkart_retriever_tool


class RAGAgentBuilder:
    def __init__(self, vector_store: Any) -> None:
        self.vector_store = vector_store
        self.model = init_chat_model(Config.RAG_MODEL)

    def build_agent(self) -> Any:
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        flipkart_tool = build_flipkart_retriever_tool(retriever)

        agent = create_agent(
            model=self.model,
            tools=[flipkart_tool],
            system_prompt=SYSTEM_PROMPT,
            checkpointer=InMemorySaver(),
            middleware=[
                SummarizationMiddleware(
                    model=self.model,
                    trigger=("messages", 10),
                    keep=("messages", 4),
                )
            ],
        )
        return agent
