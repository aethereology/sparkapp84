import json
from fastapi import APIRouter, Request, Header, HTTPException
from webhooks.security import verify_square_webhook, check_timestamp, rate_limit, idem_check, idem_store, process_lock
router = APIRouter()
@router.post("")
async def square_webhook(request: Request, 
                         x_square_hmacsha256_signature: str = Header(None),
                         x_request_timestamp: str = Header(None)):
    raw = await request.body()
    source_ip = request.client.host if request.client else "unknown"
    rate_limit("square", source_ip)
    if not verify_square_webhook(raw, x_square_hmacsha256_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    if not check_timestamp(x_request_timestamp):
        raise HTTPException(status_code=400, detail="Invalid or stale timestamp")
    data = json.loads(raw.decode("utf-8"))
    event_id = data.get("event_id") or data.get("id") or "no-id"
    cached = idem_check("square", event_id)
    if cached: return {"status": "duplicate", "event_id": event_id, "cached": True}
    if not process_lock("square", event_id):
        raise HTTPException(status_code=409, detail="Processing in progress")
    # TODO: process the event
    result = {"status": "processed", "event_id": event_id}
    idem_store("square", event_id, result)
    return result
