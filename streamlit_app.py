import uuid
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder


# Load environment variables
load_dotenv()

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
st.sidebar.caption("LangChain + LangGraph + Vector DB")

if st.sidebar.button("🔄 New Chat"):
    st.session_state.clear()
    st.rerun()

# ---------------------------
# Session State Initialization
# ---------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages: List[Dict[str, str]] = []
    st.session_state.request_count: int = 0
    st.session_state.prediction_count: int = 0

# ---------------------------
# Load Vector Store & Agent (Cached)
# ---------------------------
@st.cache_resource(show_spinner="🔍 Loading product knowledge base...")
def load_agent() -> Any:
    vector_store = DataIngestor().ingest(load_existing=True)
    return RAGAgentBuilder(vector_store).build_agent()


rag_agent = load_agent()

# ---------------------------
# Main Title
# ---------------------------
st.title("🛒 Flipkart AI Assistant")
st.caption("Ask about products, prices, specifications & comparisons")

# ---------------------------
# Display Chat History
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# User Input
# ---------------------------
user_input: str = st.chat_input("Ask me about Flipkart products...")

if user_input:
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

        if not response.get("messages"):
            reply: str = (
                "Sorry, I couldn't find relevant product information."
            )
        else:
            reply = response["messages"][-1].content

        st.markdown(reply)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

# ---------------------------
# Footer Metrics
# ---------------------------
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.metric("📥 Requests", st.session_state.request_count)

with col2:
    st.metric("🤖 Predictions", st.session_state.prediction_count)
