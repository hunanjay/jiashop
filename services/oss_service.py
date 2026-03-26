import os
import uuid
import base64
import oss2
import io
from PIL import Image

def _get_bucket():
    access_key_id = os.environ.get("OSS_ACCESS_KEY_ID")
    access_key_secret = os.environ.get("OSS_ACCESS_KEY_SECRET")
    endpoint = os.environ.get("OSS_ENDPOINT")
    if endpoint and not endpoint.startswith("http"):
        endpoint = f"https://{endpoint}"
    bucket_name = os.environ.get("OSS_BUCKET")

    if not access_key_id or not access_key_secret or not endpoint or not bucket_name:
        return None
        
    auth = oss2.Auth(access_key_id, access_key_secret)
    return oss2.Bucket(auth, endpoint, bucket_name)

def upload_base64_to_oss(base64_str, user_id="system"):
    """
    Uploads a base64 encoded image string to Aliyun OSS and returns the Object Key.
    """
    if not isinstance(base64_str, str) or not base64_str.startswith("data:"):
        return base64_str

    bucket = _get_bucket()
    if not bucket:
        raise ValueError("OSS configuration is missing!")

    try:
        header, enc_str = base64_str.split(",", 1)
        ext = "webp"
        
        file_data = base64.b64decode(enc_str)
        img = Image.open(io.BytesIO(file_data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        out_io = io.BytesIO()
        img.save(out_io, format="WEBP", quality=85)
        file_data = out_io.getvalue()
    except Exception as e:
        print("Failed to decode or convert image:", str(e))
        raise ValueError(f"Failed to process and convert base64 image: {str(e)}")

    try:
        filename = f"uploads/{user_id}/{uuid.uuid4().hex}.{ext}"
        bucket.put_object(filename, file_data, headers={'Cache-Control': 'max-age=2592000'})
        return filename  # Return only the key
    except Exception as e:
        print("Failed to upload to OSS:", str(e))
        raise RuntimeError(f"Failed to upload to OSS: {str(e)}")

def get_signed_url(image_path, expires=3600):
    """
    Generates a signed URL for an Object Key. 
    If image_path is already a full URL or doesn't look like an OSS path, returns it as is.
    """
    if not image_path or not isinstance(image_path, str) or image_path.startswith("http") or image_path.startswith("data:"):
        return image_path
    
    # Check if it's one of ours (starts with uploads/)
    if not image_path.startswith("uploads/"):
        return image_path

    bucket = _get_bucket()
    if not bucket:
        return image_path
        
    try:
        # Generate a signed URL valid for 1 hour by default
        return bucket.sign_url('GET', image_path, expires)
    except Exception as e:
        print(f"Failed to sign URL for {image_path}: {e}")
        return image_path

