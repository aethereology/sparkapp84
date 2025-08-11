from fastapi import APIRouter
import os
from services.reconciliation import run_reconciliation, latest_report
router = APIRouter()
@router.post("/reconciliation/run")
def run_recon():
    data_dir = os.getenv("DATA_DIR", "/app/data")
    return run_reconciliation(data_dir)
@router.get("/reconciliation/latest")
def latest():
    data_dir = os.getenv("DATA_DIR", "/app/data")
    return latest_report(data_dir)
