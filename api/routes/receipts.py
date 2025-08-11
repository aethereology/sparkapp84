from fastapi import APIRouter, HTTPException, Response
from services.receipts import find_donation, find_donor, generate_receipt_pdf, line_items_from_row
from services.emailer import send_email
from cache.redis_cache import get_cached_receipt_pdf, cache_receipt_pdf
router = APIRouter()
def _pdf_response(pdf: bytes, filename: str, hit: bool = False):
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{filename}"', "X-Cache": "HIT" if hit else "MISS"})
@router.get("/donations/{donation_id}/receipt.pdf")
def get_receipt(donation_id: str):
    dn = find_donation(donation_id)
    if not dn: raise HTTPException(404, "Donation not found")
    donor = find_donor(dn.get("donor_id","")) or {"primary_contact_name":"Donor","email":""}
    rid = dn.get("receipt_id") or f"RCPT-{donation_id}"
    cached = get_cached_receipt_pdf(donation_id)
    if cached: return _pdf_response(cached, f"{rid}.pdf", True)
    pdf = generate_receipt_pdf(
        receipt_id=rid, donor_name=donor["primary_contact_name"],
        donation_amount=float(dn.get("amount","0") or 0), donation_date=(dn.get("received_at") or "")[:10],
        designation=dn.get("designation","General Fund"), restricted=(dn.get("restricted","no").lower()=="yes"),
        payment_method=(dn.get("method","square")).title(), soft_credit_to=dn.get("soft_credit_to") or None,
        line_items=line_items_from_row(dn))
    try: cache_receipt_pdf(donation_id, pdf)
    except Exception: pass
    return _pdf_response(pdf, f"{rid}.pdf")
@router.post("/donations/{donation_id}/receipt")
def send_receipt(donation_id: str):
    dn = find_donation(donation_id)
    if not dn: raise HTTPException(404, "Donation not found")
    donor = find_donor(dn.get("donor_id","")) or {"primary_contact_name":"Donor","email":""}
    if not donor.get("email"): raise HTTPException(400, "No donor email on file")
    rid = dn.get("receipt_id") or f"RCPT-{donation_id}"
    cached = get_cached_receipt_pdf(donation_id)
    pdf = cached or generate_receipt_pdf(
        receipt_id=rid, donor_name=donor["primary_contact_name"],
        donation_amount=float(dn.get("amount","0") or 0), donation_date=(dn.get("received_at") or "")[:10],
        designation=dn.get("designation","General Fund"), restricted=(dn.get("restricted","no").lower()=="yes"),
        payment_method=(dn.get("method","square")).title(), soft_credit_to=dn.get("soft_credit_to") or None,
        line_items=line_items_from_row(dn))
    if not cached:
        try: cache_receipt_pdf(donation_id, pdf)
        except Exception: pass
    ok = send_email(donor["email"], "Your donation receipt", "<p>Thank you for your gift.</p>", pdf, f"{rid}.pdf")
    return {"sent": bool(ok)}
