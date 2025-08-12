import logging
from fastapi import APIRouter, Query, Depends
from storage.gcs_signed_urls import batch_generate_urls
from auth import require_reviewer, User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/data-room/documents")
def list_documents(
    org: str = Query("spark"), 
    reviewer: bool = Query(False),
    current_user: User = Depends(require_reviewer)
) -> dict:
    """List available data room documents for organization"""
    logger.info(f"User {current_user.username} accessing data room documents for org {org}")
    
    items = [
        {"key": f"{org}/governance/IRS_Letter.pdf", "name": "IRS Determination Letter"},
        {"key": f"{org}/policies/Donor_Privacy_Policy.pdf", "name": "Donor Privacy Policy"},
        {"key": f"{org}/financials/Budget_Summary_FY2025.pdf", "name": "Budget Summary FY2025"}
    ]
    
    urls = batch_generate_urls(items, reviewer=reviewer)
    
    logger.info(f"Generated {len(urls)} signed URLs for org {org}")
    return {"org": org, "documents": urls}
