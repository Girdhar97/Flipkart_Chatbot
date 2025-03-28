import os
import uuid
from typing import Any

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
from prometheus_client import Counter, generate_latest

from langchain_core.messages import HumanMessage

from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder

# Load environment variables
load_dotenv()

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
PREDICTION_COUNT = Counter("model_predictions_total", "Total Model Predictions")


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static",
    )

    # Create a NEW thread for every app run (LangGraph memory)
    thread_id: str = str(uuid.uuid4())
    print(f"[INFO] New chat thread created: {thread_id}")

    # Load / ingest vector store
    vector_store = DataIngestor().ingest(load_existing=True)

    # Build RAG Agent (LangChain + LangGraph)
    rag_agent = RAGAgentBuilder(vector_store).build_agent()

    @app.route("/")
    def index() -> str:
        REQUEST_COUNT.inc()
        return render_template("index.html")

    @app.route("/get", methods=["POST"])
    def get_response() -> str:
        REQUEST_COUNT.inc()

        user_input_raw: str = request.form.get("msg", "")

        # Guard: ignore empty / whitespace-only input
        user_input = user_input_raw.strip()
        if not user_input:
            return "Please enter a message so I can help you."

        # Invoke agent with LangGraph thread-based memory
        response: Any = rag_agent.invoke(
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
                    "thread_id": thread_id,
                }
            },
        )

        PREDICTION_COUNT.inc()

        if not response.get("messages"):
            return "Sorry, I couldn't find relevant product information."

        # Return latest assistant message
        return response["messages"][-1].content

    @app.route("/health")
    def health() -> tuple[dict, int]:
        return jsonify({"status": "healthy"}), 200

    @app.route("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(), mimetype="text/plain")

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
