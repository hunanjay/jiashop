import os
import traceback
import re
from io import BytesIO

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.dependencies import require_roles
from services.oss_service import upload_base64_to_oss, get_signed_url, download_image_bytes

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")


@upload_bp.get("/image")
@require_roles("admin", "superadmin")
def get_image_for_clipboard():
    """Return an owned OSS image through the same-origin API for clipboard use."""
    key = request.args.get("key", "")
    if not key.startswith("uploads/") or ".." in key.split("/") or not re.fullmatch(r"[A-Za-z0-9_./-]+", key):
        return jsonify({"error": "Invalid image key"}), 400

    image_data = download_image_bytes(key)
    if image_data is None:
        return jsonify({"error": "Image not found"}), 404

    content_type = {
        ".gif": "image/gif",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(os.path.splitext(key)[1].lower())
    if not content_type:
        return jsonify({"error": "Unsupported image type"}), 415

    return send_file(BytesIO(image_data), mimetype=content_type, max_age=300)

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
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

