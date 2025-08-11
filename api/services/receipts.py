import os, io, csv
from datetime import datetime
from typing import Optional, List, Dict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import qrcode

ORG_NAME = os.getenv("SPARK_ORG_NAME", "SparkCreatives Inc.")
ORG_EIN = os.getenv("SPARK_EIN", "33-4477854")
ORG_ADDR = os.getenv("SPARK_ADDR", "6120 Caladesi Ct, Jacksonville, FL 32258")
BASE_VERIFY_URL = os.getenv("SPARK_VERIFY_BASE_URL", "https://sparkcreatives.org/verify")
LOGO_PATH = os.getenv("SPARK_LOGO_PATH", "/app/assets/logo.png")

def _load_logo_bytes() -> Optional[bytes]:
    try:
        with open(LOGO_PATH, "rb") as f:
            return f.read()
    except Exception:
        return None

def _qr_bytes(url: str) -> bytes:
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def _draw_header(c, W, H, logo_bytes: Optional[bytes]):
    c.setFillColorRGB(0.946, 0.592, 0.219)  # #F19738
    c.rect(0, H-1.0*inch, W, 1.0*inch, fill=1, stroke=0)
    if logo_bytes:
        try:
            img = ImageReader(io.BytesIO(logo_bytes))
            c.drawImage(img, 0.75*inch, H-0.9*inch, width=0.8*inch, height=0.8*inch, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1.8*inch, H-0.55*inch, ORG_NAME[:64])
    c.setFont("Helvetica", 9.5)
    c.drawString(1.8*inch, H-0.8*inch, f"EIN: {ORG_EIN} • {ORG_ADDR}")

def _designation_breakdown(rows: List[Dict]) -> List[Dict]:
    from collections import defaultdict
    totals = defaultdict(float)
    for r in rows:
        des = r.get("designation") or "General Fund"
        amt = float(r.get("amount") or 0)
        totals[des] += amt
    return [{"designation": k, "amount": v} for k,v in sorted(totals.items())]

def generate_receipt_pdf(receipt_id: str, donor_name: str, donation_amount: float, donation_date: str,
                         designation: str, restricted: bool, payment_method: str,
                         soft_credit_to: Optional[str]=None, line_items: Optional[List[Dict]]=None) -> bytes:
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=LETTER); W,H = LETTER
    _draw_header(c, W, H, _load_logo_bytes())

    y = H - 1.25*inch
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14); c.drawString(0.75*inch, y, "Donation Receipt")
    c.setFont("Helvetica", 10); c.drawRightString(W-0.75*inch, y, f"Receipt ID: {receipt_id}")
    y -= 0.3*inch

    c.setFont("Helvetica-Bold", 11); c.drawString(0.75*inch, y, "Donor"); y -= 0.2*inch
    c.setFont("Helvetica", 10); c.drawString(0.95*inch, y, donor_name); y -= 0.35*inch

    c.setFont("Helvetica-Bold", 11); c.drawString(0.75*inch, y, "Donation Details"); y -= 0.2*inch
    c.setFont("Helvetica", 10)
    for k,v in [("Date", donation_date), ("Amount", f"${donation_amount:,.2f}"),
                ("Payment Method", payment_method), ("Designation", designation or "General Fund"),
                ("Restriction", "Restricted" if restricted else "Unrestricted")]:
        c.drawString(0.95*inch, y, f"{k}:"); c.drawString(2.3*inch, y, str(v)); y -= 0.18*inch

    if soft_credit_to:
        c.drawString(0.95*inch, y, "Soft Credit:"); c.drawString(2.3*inch, y, soft_credit_to); y -= 0.18*inch
    y -= 0.2*inch

    if line_items:
        c.setFont("Helvetica-Bold", 10); c.drawString(0.75*inch, y, "Designation Breakdown"); y -= 0.2*inch
        c.setFont("Helvetica", 9.5)
        for li in line_items:
            c.drawString(0.95*inch, y, f"- {li.get('designation','')}")
            c.drawRightString(W-0.75*inch, y, f"${float(li.get('amount',0)):.2f}")
            y -= 0.16*inch
        y -= 0.15*inch

    verify_url = f"{BASE_VERIFY_URL}?rid={receipt_id}"
    try:
        qr_png = _qr_bytes(verify_url)
        c.drawImage(ImageReader(io.BytesIO(qr_png)), W-1.9*inch, 0.9*inch, width=1.1*inch, height=1.1*inch, mask='auto')
        c.setFont("Helvetica", 8.5); c.drawRightString(W-0.75*inch, 0.85*inch, "Verify receipt")
    except Exception:
        pass

    c.setFont("Helvetica-Oblique", 9.5)
    c.drawString(0.75*inch, 0.95*inch, "No goods or services were provided in exchange for this contribution.")
    c.setFont("Helvetica", 8.5)
    c.drawString(0.75*inch, 0.75*inch, "Thank you for fueling creativity and shipping boxes of hope.")
    c.drawRightString(W-0.75*inch, 0.75*inch, datetime.utcnow().strftime("Generated %Y-%m-%d %H:%M UTC"))
    c.showPage(); c.save()
    return buf.getvalue()

def _load_csv(name: str):
    data_dir = os.getenv("DATA_DIR", "/app/data")
    path = os.path.join(data_dir, name)
    with open(path, newline="", encoding="utf-8") as f:
        import csv; return list(csv.DictReader(f))

def find_donation(donation_id: str) -> Optional[dict]:
    for r in _load_csv("donations.csv"):
        if r.get("donation_id")==donation_id:
            return r
    return None

def find_donor(donor_id: str) -> Optional[dict]:
    for r in _load_csv("donors.csv"):
        if r.get("donor_id")==donor_id:
            return r
    return None

def line_items_from_row(row: dict) -> Optional[list]:
    br = (row.get("designation_breakdown") or "").strip()
    if not br: return None
    out = []
    for part in br.split(";"):
        if ":" in part:
            d,a = part.split(":",1)
            try:
                out.append({"designation":d.strip(), "amount":float(a)})
            except: pass
    return out or None
