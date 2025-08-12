import os
import base64
import json
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)
PROVIDER = os.getenv("EMAIL_PROVIDER", "sendgrid")

def send_email(to_email: str, subject: str, html: str, attachment: Optional[bytes] = None, filename: str = "attachment.pdf") -> bool:
    """Send email via configured provider (SendGrid or Postmark)"""
    logger.info(f"Sending email to {to_email} with subject: {subject}")
    
    try:
        if PROVIDER == "sendgrid":
            return _send_via_sendgrid(to_email, subject, html, attachment, filename)
        else:
            return _send_via_postmark(to_email, subject, html, attachment, filename)
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def _send_via_sendgrid(to_email: str, subject: str, html: str, attachment: Optional[bytes], filename: str) -> bool:
    """Send email via SendGrid API"""
    key = os.getenv("SENDGRID_API_KEY")
    if not key:
        logger.warning("SENDGRID_API_KEY not configured - email sending disabled")
        return False
    
    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {
            "email": os.getenv("FROM_EMAIL", "noreply@sparkcreatives.org"), 
            "name": os.getenv("FROM_NAME", "SparkCreatives")
        },
        "subject": subject,
        "content": [{"type": "text/html", "value": html}]
    }
    
    if attachment:
        payload["attachments"] = [{
            "content": base64.b64encode(attachment).decode("utf-8"),
            "filename": filename, 
            "type": "application/pdf"
        }]
        logger.info(f"Email includes attachment: {filename}")
    
    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps(payload),
            timeout=30
        )
        
        success = response.status_code in (200, 202)
        if success:
            logger.info(f"Email sent successfully via SendGrid to {to_email}")
        else:
            logger.error(f"SendGrid API error {response.status_code}: {response.text}")
        
        return success
        
    except requests.RequestException as e:
        logger.error(f"SendGrid API request failed: {str(e)}")
        return False

def _send_via_postmark(to_email: str, subject: str, html: str, attachment: Optional[bytes], filename: str) -> bool:
    """Send email via Postmark API"""
    token = os.getenv("POSTMARK_TOKEN")
    if not token:
        logger.warning("POSTMARK_TOKEN not configured - email sending disabled")
        return False
    
    payload = {
        "From": os.getenv("FROM_EMAIL", "noreply@sparkcreatives.org"),
        "To": to_email, 
        "Subject": subject, 
        "HtmlBody": html
    }
    
    if attachment:
        payload["Attachments"] = [{
            "Name": filename, 
            "Content": base64.b64encode(attachment).decode("utf-8"),
            "ContentType": "application/pdf"
        }]
        logger.info(f"Email includes attachment: {filename}")
    
    try:
        response = requests.post(
            "https://api.postmarkapp.com/email",
            headers={
                "X-Postmark-Server-Token": token, 
                "Content-Type": "application/json"
            },
            data=json.dumps(payload),
            timeout=30
        )
        
        success = response.status_code in (200, 201)
        if success:
            logger.info(f"Email sent successfully via Postmark to {to_email}")
        else:
            logger.error(f"Postmark API error {response.status_code}: {response.text}")
        
        return success
        
    except requests.RequestException as e:
        logger.error(f"Postmark API request failed: {str(e)}")
        return False
