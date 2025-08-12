import logging
from fastapi import APIRouter, HTTPException, Response, Depends
from services.receipts import find_donation, find_donor, generate_receipt_pdf, line_items_from_row
from services.emailer import send_email
from cache.redis_cache import get_cached_receipt_pdf, cache_receipt_pdf
from auth import require_user, User

logger = logging.getLogger(__name__)
router = APIRouter()

def _pdf_response(pdf: bytes, filename: str, hit: bool = False):
    """Create PDF response with appropriate headers"""
    return Response(
        content=pdf, 
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"', 
            "X-Cache": "HIT" if hit else "MISS"
        }
    )

@router.get("/donations/{donation_id}/receipt.pdf")
def get_receipt(
    donation_id: str,
    current_user: User = Depends(require_user)
):
    """Generate and return receipt PDF for donation"""
    logger.info(f"User {current_user.username} requesting receipt for donation {donation_id}")
    
    dn = find_donation(donation_id)
    if not dn: 
        logger.warning(f"Donation {donation_id} not found")
        raise HTTPException(404, "Donation not found")
    
    donor = find_donor(dn.get("donor_id", "")) or {"primary_contact_name": "Donor", "email": ""}
    rid = dn.get("receipt_id") or f"RCPT-{donation_id}"
    
    # Check cache first
    cached = get_cached_receipt_pdf(donation_id)
    if cached:
        logger.info(f"Serving cached receipt for donation {donation_id}")
        return _pdf_response(cached, f"{rid}.pdf", True)
    
    # Generate new PDF
    logger.info(f"Generating new receipt PDF for donation {donation_id}")
    pdf = generate_receipt_pdf(
        receipt_id=rid, 
        donor_name=donor["primary_contact_name"],
        donation_amount=float(dn.get("amount", "0") or 0), 
        donation_date=(dn.get("received_at") or "")[:10],
        designation=dn.get("designation", "General Fund"), 
        restricted=(dn.get("restricted", "no").lower() == "yes"),
        payment_method=(dn.get("method", "square")).title(), 
        soft_credit_to=dn.get("soft_credit_to") or None,
        line_items=line_items_from_row(dn)
    )
    
    # Cache the PDF
    try: 
        cache_receipt_pdf(donation_id, pdf)
        logger.info(f"Cached receipt PDF for donation {donation_id}")
    except Exception as e:
        logger.warning(f"Failed to cache receipt PDF for {donation_id}: {str(e)}")
    
    return _pdf_response(pdf, f"{rid}.pdf")

@router.post("/donations/{donation_id}/receipt")
def send_receipt(
    donation_id: str,
    current_user: User = Depends(require_user)
):
    """Email receipt PDF to donor"""
    logger.info(f"User {current_user.username} sending receipt for donation {donation_id}")
    
    dn = find_donation(donation_id)
    if not dn: 
        logger.warning(f"Donation {donation_id} not found")
        raise HTTPException(404, "Donation not found")
    
    donor = find_donor(dn.get("donor_id", "")) or {"primary_contact_name": "Donor", "email": ""}
    if not donor.get("email"): 
        logger.warning(f"No email address for donor of donation {donation_id}")
        raise HTTPException(400, "No donor email on file")
    
    rid = dn.get("receipt_id") or f"RCPT-{donation_id}"
    
    # Get PDF (cached or generate new)
    cached = get_cached_receipt_pdf(donation_id)
    pdf = cached or generate_receipt_pdf(
        receipt_id=rid, 
        donor_name=donor["primary_contact_name"],
        donation_amount=float(dn.get("amount", "0") or 0), 
        donation_date=(dn.get("received_at") or "")[:10],
        designation=dn.get("designation", "General Fund"), 
        restricted=(dn.get("restricted", "no").lower() == "yes"),
        payment_method=(dn.get("method", "square")).title(), 
        soft_credit_to=dn.get("soft_credit_to") or None,
        line_items=line_items_from_row(dn)
    )
    
    # Cache if not already cached
    if not cached:
        try: 
            cache_receipt_pdf(donation_id, pdf)
            logger.info(f"Cached receipt PDF for donation {donation_id}")
        except Exception as e:
            logger.warning(f"Failed to cache receipt PDF for {donation_id}: {str(e)}")
    
    # Send email
    success = send_email(
        donor["email"], 
        "Your donation receipt", 
        "<p>Thank you for your gift to SparkCreatives. Your receipt is attached.</p>", 
        pdf, 
        f"{rid}.pdf"
    )
    
    if success:
        logger.info(f"Receipt emailed successfully for donation {donation_id} to {donor['email']}")
    else:
        logger.error(f"Failed to email receipt for donation {donation_id} to {donor['email']}")
    
    return {"sent": bool(success)}
