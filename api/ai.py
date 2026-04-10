from flask import Blueprint, request, jsonify, Response, stream_with_context
from services.ai_service import chain
import json

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

@ai_bp.route("/chat", methods=["POST"])
def chat():
    """
    Handle POST request for AI chat.
    Supports streaming response via Server-Sent Events (SSE).
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400
    
    message = data.get("message", "")
    
    def generate():
        try:
            for chunk in chain.stream({"input": message}):
                # Format for SSE: data: {"content": "..."}\n\n
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), 
                    mimetype="text/event-stream")

@ai_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "AI service is running"})
