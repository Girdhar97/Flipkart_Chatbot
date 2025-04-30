import uuid
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder
from utils.logger import get_logger
from utils.custom_exception import CustomException


logger = get_logger(__name__)


# Load environment variables
try:
    logger.info("Loading environment variables for Streamlit app")
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except Exception as e:
    logger.error(f"Error loading environment variables: {str(e)}")
    raise CustomException("Failed to load environment variables in Streamlit", e)


# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(
    page_title="Flipkart AI Chatbot",
    page_icon="🛒",
    layout="centered",
)


# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("🛍️ Flipkart RAG Chatbot")
st.sidebar.caption(
    "Powered by LangChain, LangGraph and AstraDB vector search.\n"
    "Uses Retrieval-Augmented Generation (RAG) over real product reviews."
)


try:
    if st.sidebar.button("🔄 New Chat"):
        logger.info("New chat session requested")
        st.session_state.clear()
        st.rerun()
except Exception as e:
    logger.error(f"Error handling new chat button: {str(e)}")
    st.error("Failed to start new chat")


# ---------------------------
# Session State Initialization
# ---------------------------
try:
    if "thread_id" not in st.session_state:
        logger.info("Initializing new Streamlit session state")
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []  
        st.session_state.request_count = 0  
        st.session_state.prediction_count = 0  
        logger.info(f"Session initialized with thread_id: {st.session_state.thread_id}")
except Exception as e:
    logger.error(f"Error initializing session state: {str(e)}")
    raise CustomException("Failed to initialize Streamlit session", e)


# ---------------------------
# Load Vector Store & Agent (Cached)
# ---------------------------
@st.cache_resource(show_spinner="🔍 Loading product knowledge base...")
def load_agent() -> Any:
    try:
        logger.info("Loading vector store and RAG agent")
        vector_store = DataIngestor().ingest(load_existing=True)
        agent = RAGAgentBuilder(vector_store).build_agent()
        logger.info("RAG agent loaded successfully in cache")
        return agent
    except Exception as e:
        logger.error(f"Error loading RAG agent: {str(e)}")
        raise CustomException("Failed to load RAG agent in Streamlit", e)


rag_agent = load_agent()


# ---------------------------
# Main Title
# ---------------------------
st.title("🛒 Flipkart AI Assistant")
st.caption(
    "RAG-powered chatbot that answers using Flipkart-style product data "
    "and customer reviews."
)


# Extra description above chat
st.write(
    "Type a question like *“Recommend a phone under 20k with good battery”* "
    "or *“Which laptop is best for coding and light gaming?”*"
)


# ---------------------------
# Display Chat History
# ---------------------------
try:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
except Exception as e:
    logger.error(f"Error displaying chat history: {str(e)}")
    st.error("Failed to display chat history")


# ---------------------------
# User Input
# ---------------------------
user_input_raw: str = st.chat_input("Ask me about Flipkart products...")


# Guard: ignore empty / whitespace-only input
user_input = user_input_raw.strip() if user_input_raw is not None else ""


if user_input:
    try:
        logger.info(f"Processing user input: {user_input[:50]}...")
        st.session_state.request_count += 1

        # Show user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        # Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                response: Dict[str, Any] = rag_agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_input,
                            }
                        ]
                    },
                    config={
                        "configurable": {
                            "thread_id": st.session_state.thread_id,
                        }
                    },
                )

            st.session_state.prediction_count += 1
            logger.info("RAG prediction completed")

            if not response.get("messages"):
                reply: str = (
                    "Sorry, I couldn't find relevant product information."
                )
                logger.warning("Empty agent response")
            else:
                reply = response["messages"][-1].content
                logger.info(f"Response length: {len(reply)} chars")

            st.markdown(reply)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": reply,
            }
        )
        logger.info("Chat message saved to session")
    except Exception as e:
        logger.error(f"Error processing user query: {str(e)}")
        st.error("Sorry, something went wrong processing your query")
        raise CustomException("Streamlit RAG processing failed", e)


# ---------------------------
# Footer Metrics
# ---------------------------
try:
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.metric("📥 Requests", st.session_state.request_count)

    with col2:
        st.metric("🤖 Predictions", st.session_state.prediction_count)
except Exception as e:
    logger.error(f"Error displaying metrics: {str(e)}")
