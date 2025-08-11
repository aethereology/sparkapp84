import os, base64, json, requests
PROVIDER = os.getenv("EMAIL_PROVIDER", "sendgrid")
def send_email(to_email: str, subject: str, html: str, attachment: bytes=None, filename: str="attachment.pdf") -> bool:
    if PROVIDER == "sendgrid":
        key = os.getenv("SENDGRID_API_KEY")
        if not key:
            print("[email] SENDGRID_API_KEY missing; skipping"); return False
        payload = {"personalizations":[{"to":[{"email": to_email}]}],
                   "from":{"email": os.getenv("FROM_EMAIL","noreply@sparkcreatives.org"), "name": os.getenv("FROM_NAME","SparkCreatives")},
                   "subject": subject,
                   "content":[{"type":"text/html","value": html}]}
        if attachment:
            payload["attachments"]=[{"content": base64.b64encode(attachment).decode("utf-8"),
                                     "filename": filename, "type":"application/pdf"}]
        r = requests.post("https://api.sendgrid.com/v3/mail/send",
                          headers={"Authorization": f"Bearer {key}","Content-Type":"application/json"},
                          data=json.dumps(payload))
        return r.status_code in (200,202)
    else:
        token = os.getenv("POSTMARK_TOKEN")
        if not token:
            print("[email] POSTMARK_TOKEN missing; skipping"); return False
        payload = {"From": os.getenv("FROM_EMAIL","noreply@sparkcreatives.org"),
                   "To": to_email, "Subject": subject, "HtmlBody": html}
        if attachment:
            payload["Attachments"]=[{"Name": filename, "Content": base64.b64encode(attachment).decode("utf-8"),
                                     "ContentType":"application/pdf"}]
        r = requests.post("https://api.postmarkapp.com/email",
                          headers={"X-Postmark-Server-Token": token, "Content-Type":"application/json"},
                          data=json.dumps(payload))
        return r.status_code in (200, 201)
