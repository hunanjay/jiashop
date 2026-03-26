import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.oss_service import upload_base64_to_oss, get_signed_url

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

@upload_bp.route("", methods=["POST"])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True)
    
    if not data or "image" not in data:
        return jsonify({"error": "No image data provided. Provide base64 'image'"}), 400
    
    try:
        key = upload_base64_to_oss(data["image"], user_id=user_id)
        # 如果返回的是 base64 字符串本身，说明内部跳过了上传（配置缺失或格式不对）
        if key.startswith("data:"):
             return jsonify({"error": "Failed to upload image to OSS (check server logs/config)"}), 500
             
        signed_url = get_signed_url(key)
        return jsonify({
            "key": key,
            "url": signed_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

