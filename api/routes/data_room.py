from fastapi import APIRouter, Query
from storage.gcs_signed_urls import batch_generate_urls
router = APIRouter()
@router.get("/data-room/documents")
def list_documents(org: str = Query("spark"), reviewer: bool = Query(False)) -> dict:
    items = [
        {"key": f"{org}/governance/IRS_Letter.pdf", "name": "IRS Determination Letter"},
        {"key": f"{org}/policies/Donor_Privacy_Policy.pdf", "name": "Donor Privacy Policy"},
        {"key": f"{org}/financials/Budget_Summary_FY2025.pdf", "name": "Budget Summary FY2025"}
    ]
    urls = batch_generate_urls(items, reviewer=reviewer)
    return {"org": org, "documents": urls}
