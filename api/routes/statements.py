from fastapi import APIRouter, HTTPException, Response, Query
from services.receipts import find_donor, _load_csv, generate_receipt_pdf
from services.receipts import _designation_breakdown as designation_breakdown
from services.emailer import send_email
from cache.redis_cache import get_cached_statement_pdf, cache_statement_pdf
router = APIRouter()
def _pdf_response(pdf: bytes, filename: str, hit: bool = False):
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{filename}"', "X-Cache": "HIT" if hit else "MISS"})
@router.get("/donors/{donor_id}/statement/{year}")
def get_statement(donor_id: str, year: int):
    donor = find_donor(donor_id); 
    if not donor: raise HTTPException(404, "Donor not found")
    cached = get_cached_statement_pdf(donor_id, year)
    rid = f"YEAR-{year}-{donor_id}"
    if cached: return _pdf_response(cached, f"{rid}.pdf", True)
    donations = [r for r in _load_csv("donations.csv") if r.get("donor_id")==donor_id and r.get("received_at","")[:4]==str(year)]
    total = sum(float(d.get("amount","0") or 0) for d in donations)
    pdf = generate_receipt_pdf(
        receipt_id=rid, donor_name=donor.get("primary_contact_name","Donor"),
        donation_amount=total, donation_date=f"{year}-12-31", designation=f"Annual Statement {year}", restricted=False,
        payment_method="Multiple", soft_credit_to=None, line_items=designation_breakdown(donations))
    try: cache_statement_pdf(donor_id, year, pdf)
    except Exception: pass
    return _pdf_response(pdf, f"{rid}.pdf")
@router.post("/tasks/year-end-statements")
def batch_statements(year: int = Query(..., description="Year for statements")):
    donors = _load_csv("donors.csv"); donations = _load_csv("donations.csv"); count=0
    for d in donors:
        did = d.get("donor_id")
        my = [r for r in donations if r.get("donor_id")==did and r.get("received_at","")[:4]==str(year)]
        if not my: continue
        total = sum(float(x.get("amount","0") or 0) for x in my)
        rid = f"YEAR-{year}-{did}"
        pdf = generate_receipt_pdf(
            receipt_id=rid, donor_name=d.get("primary_contact_name","Donor"), donation_amount=total, donation_date=f"{year}-12-31",
            designation=f"Annual Statement {year}", restricted=False, payment_method="Multiple", soft_credit_to=None,
            line_items=designation_breakdown(my))
        if d.get("email"): send_email(d["email"], f"Your {year} annual giving statement", "<p>Attached is your annual statement.</p>", pdf, f"{rid}.pdf")
        count += 1
    return {"generated": count}
