import os
import uuid
from typing import Any

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
from prometheus_client import Counter, generate_latest

from langchain_core.messages import HumanMessage

from flipkart.data_ingestion import DataIngestor
from flipkart.rag_agent import RAGAgentBuilder
from utils.logger import get_logger
from utils.custom_exception import CustomException


logger = get_logger(__name__)


# Load environment variables
try:
    logger.info("Loading environment variables")
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except Exception as e:
    logger.error(f"Error loading environment variables: {str(e)}")
    raise CustomException("Failed to load environment variables", e)


# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests")
PREDICTION_COUNT = Counter("model_predictions_total", "Total Model Predictions")


def create_app() -> Flask:
    try:
        logger.info("Creating Flask application")
        app = Flask(
            __name__,
            template_folder="frontend/templates",
            static_folder="frontend/static",
        )

        # Create a NEW thread for every app run (LangGraph memory)
        thread_id: str = str(uuid.uuid4())
        logger.info(f"New chat thread created: {thread_id}")

        # Load / ingest vector store
        logger.info("Loading vector store")
        vector_store = DataIngestor().ingest(load_existing=True)
        logger.info("Vector store loaded successfully")

        # Build RAG Agent (LangChain + LangGraph)
        logger.info("Building RAG agent")
        rag_agent = RAGAgentBuilder(vector_store).build_agent()
        logger.info("RAG agent built successfully")

        @app.route("/")
        def index() -> str:
            try:
                logger.info("Serving index.html")
                REQUEST_COUNT.inc()
                return render_template("index.html")
            except Exception as e:
                logger.error(f"Error serving index page: {str(e)}")
                raise CustomException("Failed to serve index page", e)

        @app.route("/get", methods=["POST"])
        def get_response() -> str:
            try:
                logger.info("Processing /get request")
                REQUEST_COUNT.inc()

                user_input_raw: str = request.form.get("msg", "")

                # Guard: ignore empty / whitespace-only input
                user_input = user_input_raw.strip()
                if not user_input:
                    logger.warning("Empty user input received")
                    return "Please enter a message so I can help you."

                logger.info(f"Invoking RAG agent with query: {user_input[:50]}...")
                
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
                logger.info("RAG agent response generated successfully")

                if not response.get("messages"):
                    logger.warning("No messages in agent response")
                    return "Sorry, I couldn't find relevant product information."

                # Return latest assistant message
                bot_response = response["messages"][-1].content
                logger.info(f"RAG response sent: {len(bot_response)} chars")
                return bot_response
            except Exception as e:
                logger.error(f"Error processing /get request: {str(e)}")
                raise CustomException("Failed to process user query", e)

        @app.route("/health")
        def health() -> tuple[dict, int]:
            try:
                logger.info("Health check requested")
                return jsonify({"status": "healthy"}), 200
            except Exception as e:
                logger.error(f"Error in health endpoint: {str(e)}")
                raise CustomException("Health check failed", e)

        @app.route("/metrics")
        def metrics() -> Response:
            try:
                logger.debug("Metrics endpoint accessed")
                return Response(generate_latest(), mimetype="text/plain")
            except Exception as e:
                logger.error(f"Error serving metrics: {str(e)}")
                raise CustomException("Failed to serve Prometheus metrics", e)

        logger.info("Flask app factory completed successfully")
        return app
    except Exception as e:
        logger.error(f"Error in create_app factory: {str(e)}")
        raise CustomException("Failed to create Flask application", e)


if __name__ == "__main__":
    try:
        logger.info("Starting Flask application")
        app = create_app()
        port = int(os.getenv("APP_PORT", "5000"))
        logger.info(f"Flask app starting on port {port}")
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        logger.error(f"Error starting Flask app: {str(e)}")
        raise CustomException("Flask application startup failed", e)
