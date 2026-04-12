from flask import Blueprint, request, jsonify, Response, stream_with_context
from agent.customer_care import get_customer_care_chain
import json

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

@ai_bp.route("/chat", methods=["POST"])
def chat():
    """
    统一的 AI 客服入口。
    整合了 RAG 检索和业务上下文。
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400
    
    message = data.get("message", "")
    customer_chain = get_customer_care_chain()
    
    def generate():
        try:
            # 开启流式响应
            for chunk in customer_chain.stream({"input": message}):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    resp = Response(stream_with_context(generate()), mimetype="text/event-stream")
    # 防缓冲响应头
    resp.headers['X-Accel-Buffering'] = 'no'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

@ai_bp.route("/qa", methods=["POST"])
def qa():
    """
    为了兼容旧版前端，将 /qa 也映射到统一的客服 Chain。
    """
    return chat()

@ai_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "JiaJia AI Agent is active"})
