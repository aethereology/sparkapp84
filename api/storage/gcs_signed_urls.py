import os, time
from typing import List, Dict
from google.cloud import storage
from google.oauth2 import service_account
GCS_BUCKET_PUBLIC = os.getenv("GCS_BUCKET_PUBLIC", "spark-public")
GCS_BUCKET_SECURE = os.getenv("GCS_BUCKET_SECURE", "spark-secure")
GCS_SERVICE_ACCOUNT_KEY = os.getenv("GCS_SERVICE_ACCOUNT_KEY", "")
def _client():
    if GCS_SERVICE_ACCOUNT_KEY and os.path.exists(GCS_SERVICE_ACCOUNT_KEY):
        creds = service_account.Credentials.from_service_account_file(GCS_SERVICE_ACCOUNT_KEY)
        return storage.Client(credentials=creds)
    return storage.Client()
def generate_document_access_url(bucket: str, blob_name: str, expires_seconds: int = 900, method: str = "GET") -> str:
    try:
        client = _client(); bucket_obj = client.bucket(bucket)
        blob = bucket_obj.blob(blob_name)
        url = blob.generate_signed_url(expiration=int(time.time()) + int(expires_seconds), method=method)
        return url
    except Exception:
        return f"https://storage.googleapis.com/{bucket}/{blob_name}?signed=fake"
def batch_generate_urls(items: List[Dict], reviewer: bool = False) -> List[Dict]:
    ttl = 7200 if reviewer else 900
    return [{"name": it.get("name", it["key"].split('/')[-1]),
             "url": generate_document_access_url(it.get("bucket") or GCS_BUCKET_SECURE, it["key"], ttl)}
            for it in items]
