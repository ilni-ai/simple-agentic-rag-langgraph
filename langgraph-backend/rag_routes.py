# === routes/rag_routes.py ===
import os
from flask import Blueprint, request, jsonify
from langchain_community.chat_message_histories.sql import SQLChatMessageHistory
from langchain_core.messages import AIMessage
from core.langgraph_runner import runnable_with_history
import dotenv

dotenv.load_dotenv()

rag_api = Blueprint("rag_api", __name__)

@rag_api.route("/agentic-rag", methods=["POST"])
def rag_handler():
    data = request.get_json()
    query = data.get("query", "")
    session_id = data.get("session_id", "default-session")

    try:
        result = runnable_with_history.invoke(
            {"query": query},
            config={"configurable": {"session_id": session_id}}
        )

        return jsonify({
            "query": result["query"],
            "facts": result["facts"],
            "response": result["output"],
            "suggestedQuestions": result.get("suggested_questions", [])
        })
    except Exception as e:
        print("LangGraph error:", str(e))
        return jsonify({"error": "Something went wrong"}), 500

@rag_api.route("/chat-history", methods=["GET"])
def get_chat_history():
    session_id = request.args.get("session_id", "default-session")

    try:
        history = SQLChatMessageHistory(
            session_id=session_id,
            connection="sqlite:///memory.db"
        )
        messages = history.messages

        chat = []
        for msg in messages:
            role = "AI" if isinstance(msg, AIMessage) else "User"
            chat.append({"role": role, "content": msg.content})

        return jsonify(chat)
    except Exception as e:
        print("History error:", str(e))
        return jsonify({"error": "Failed to load chat history."}), 500

@rag_api.route("/reset-session", methods=["DELETE"])
def reset_session():
    session_id = request.args.get("session_id", "default-session")
    try:
        history = SQLChatMessageHistory(
            session_id=session_id,
            connection="sqlite:///memory.db"
        )
        history.clear()
        return jsonify({"message": f"Session '{session_id}' cleared."})
    except Exception as e:
        print("Reset error:", str(e))
        return jsonify({"error": "Failed to reset session."}), 500
