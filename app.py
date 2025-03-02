import os
from typing import Any

from flask import Flask, render_template, request
from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static",
)

# 1) Build vector store (assume data already ingested)
ingestor = DataIngestor()
vector_store = ingestor.ingest(load_existing=True)

# 2) Build RAG agent
agent_builder = RAGAgentBuilder(vector_store)
agent = agent_builder.build_agent()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/get", methods=["POST"])
def get_bot_response() -> str:
    user_msg: str = request.form.get("msg", "").strip()

    if not user_msg:
        return "Please enter a message so I can help you."

    result: Any = agent.invoke({"messages": [("user", user_msg)]})
    bot_reply: str = result["messages"][-1].content

    return bot_reply


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
