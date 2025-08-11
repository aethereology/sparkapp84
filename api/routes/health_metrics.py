from fastapi import APIRouter
import os, time
router = APIRouter()
@router.get("/health")
def health():
    checks = {"env": os.getenv("ENV","local"), "email_provider": os.getenv("EMAIL_PROVIDER","not-set"),
              "logo_exists": os.path.exists(os.getenv("SPARK_LOGO_PATH","/app/assets/logo.png"))}
    return {"status":"ok","checks":checks}
START = time.time()
COUNTERS = {"receipts_generated": 0, "emails_sent": 0}
@router.get("/metrics")
def metrics():
    uptime = time.time() - START
    return {"uptime_seconds": int(uptime), **COUNTERS}
