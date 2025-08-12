import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Header, HTTPException
from webhooks.security import verify_square_webhook, check_timestamp, rate_limit, idem_check, idem_store, process_lock

logger = logging.getLogger(__name__)
router = APIRouter()

def process_square_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process Square webhook events based on event type"""
    event_type = event_data.get("type", "")
    event_id = event_data.get("event_id") or event_data.get("id") or "no-id"
    
    logger.info(f"Processing Square event {event_id} of type {event_type}")
    
    try:
        if event_type == "payment.created":
            return process_payment_created(event_data)
        elif event_type == "payment.updated":
            return process_payment_updated(event_data)
        elif event_type == "refund.created":
            return process_refund_created(event_data)
        elif event_type == "invoice.payment_made":
            return process_invoice_payment(event_data)
        else:
            logger.warning(f"Unhandled Square event type: {event_type}")
            return {"status": "ignored", "reason": f"Unhandled event type: {event_type}"}
    
    except Exception as e:
        logger.error(f"Error processing Square event {event_id}: {str(e)}")
        return {"status": "error", "error": str(e)}

def process_payment_created(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process payment.created events from Square"""
    try:
        payment_data = event_data.get("data", {}).get("object", {}).get("payment", {})
        
        payment_info = {
            "square_payment_id": payment_data.get("id"),
            "amount": payment_data.get("amount_money", {}).get("amount", 0) / 100,  # Convert cents to dollars
            "currency": payment_data.get("amount_money", {}).get("currency", "USD"),
            "status": payment_data.get("status"),
            "created_at": payment_data.get("created_at"),
            "location_id": payment_data.get("location_id"),
            "order_id": payment_data.get("order_id"),
            "receipt_number": payment_data.get("receipt_number"),
            "payment_method": get_payment_method_info(payment_data)
        }
        
        # Log the payment for processing by donation system
        logger.info(f"New Square payment: ${payment_info['amount']:.2f} {payment_info['currency']} "
                   f"(ID: {payment_info['square_payment_id']})")
        
        # Here you would typically:
        # 1. Create/update donation record in your database
        # 2. Generate receipt
        # 3. Send email notification
        # 4. Update reconciliation data
        
        return {
            "status": "processed",
            "action": "payment_created", 
            "payment_id": payment_info["square_payment_id"],
            "amount": payment_info["amount"]
        }
        
    except Exception as e:
        logger.error(f"Error processing payment.created event: {str(e)}")
        raise

def process_payment_updated(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process payment.updated events from Square"""
    try:
        payment_data = event_data.get("data", {}).get("object", {}).get("payment", {})
        payment_id = payment_data.get("id")
        new_status = payment_data.get("status")
        
        logger.info(f"Square payment {payment_id} updated to status: {new_status}")
        
        # Handle status changes (completed, failed, canceled, etc.)
        if new_status == "COMPLETED":
            # Payment completed - update donation record
            pass
        elif new_status == "FAILED":
            # Payment failed - mark donation as failed
            pass
        elif new_status == "CANCELED":
            # Payment canceled - handle cancellation
            pass
            
        return {
            "status": "processed",
            "action": "payment_updated",
            "payment_id": payment_id,
            "new_status": new_status
        }
        
    except Exception as e:
        logger.error(f"Error processing payment.updated event: {str(e)}")
        raise

def process_refund_created(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process refund.created events from Square"""
    try:
        refund_data = event_data.get("data", {}).get("object", {}).get("refund", {})
        
        refund_info = {
            "refund_id": refund_data.get("id"),
            "payment_id": refund_data.get("payment_id"),
            "amount": refund_data.get("amount_money", {}).get("amount", 0) / 100,
            "reason": refund_data.get("reason"),
            "status": refund_data.get("status"),
            "created_at": refund_data.get("created_at")
        }
        
        logger.info(f"Square refund created: ${refund_info['amount']:.2f} for payment {refund_info['payment_id']}")
        
        # Process refund - update donation records, send notifications
        
        return {
            "status": "processed",
            "action": "refund_created",
            "refund_id": refund_info["refund_id"],
            "payment_id": refund_info["payment_id"],
            "amount": refund_info["amount"]
        }
        
    except Exception as e:
        logger.error(f"Error processing refund.created event: {str(e)}")
        raise

def process_invoice_payment(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process invoice.payment_made events from Square"""
    try:
        invoice_data = event_data.get("data", {}).get("object", {}).get("invoice", {})
        
        logger.info(f"Square invoice payment made for invoice {invoice_data.get('id')}")
        
        return {
            "status": "processed",
            "action": "invoice_payment_made",
            "invoice_id": invoice_data.get("id")
        }
        
    except Exception as e:
        logger.error(f"Error processing invoice.payment_made event: {str(e)}")
        raise

def get_payment_method_info(payment_data: Dict[str, Any]) -> str:
    """Extract payment method information from Square payment data"""
    if "card_details" in payment_data:
        card_details = payment_data["card_details"]
        card_type = card_details.get("card", {}).get("card_brand", "Card")
        last_four = card_details.get("card", {}).get("last_4", "****")
        return f"{card_type} ending in {last_four}"
    elif "cash_details" in payment_data:
        return "Cash"
    elif "external_details" in payment_data:
        return payment_data["external_details"].get("type", "External")
    else:
        return "Unknown"

@router.post("")
async def square_webhook(request: Request, 
                         x_square_hmacsha256_signature: str = Header(None),
                         x_request_timestamp: str = Header(None)):
    """Handle Square webhook events with proper processing"""
    raw = await request.body()
    source_ip = request.client.host if request.client else "unknown"
    
    # Apply rate limiting
    rate_limit("square", source_ip)
    
    # Verify webhook signature
    if not verify_square_webhook(raw, x_square_hmacsha256_signature):
        logger.warning(f"Invalid Square webhook signature from {source_ip}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Check timestamp freshness
    if not check_timestamp(x_request_timestamp):
        logger.warning(f"Invalid or stale timestamp from Square webhook: {x_request_timestamp}")
        raise HTTPException(status_code=400, detail="Invalid or stale timestamp")
    
    # Parse webhook data
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error("Failed to parse Square webhook JSON")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_id = data.get("event_id") or data.get("id") or "no-id"
    
    # Check for duplicate events
    cached = idem_check("square", event_id)
    if cached: 
        logger.info(f"Duplicate Square event {event_id} - returning cached result")
        return {"status": "duplicate", "event_id": event_id, "cached": True}
    
    # Acquire processing lock
    if not process_lock("square", event_id):
        logger.warning(f"Square event {event_id} already being processed")
        raise HTTPException(status_code=409, detail="Processing in progress")
    
    try:
        # Process the event
        result = process_square_event(data)
        result["event_id"] = event_id
        result["processed_at"] = datetime.utcnow().isoformat()
        
        # Store result for idempotency
        idem_store("square", event_id, result)
        
        logger.info(f"Successfully processed Square event {event_id}: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process Square event {event_id}: {str(e)}")
        # Store error result
        error_result = {
            "status": "error",
            "event_id": event_id,
            "error": str(e),
            "processed_at": datetime.utcnow().isoformat()
        }
        idem_store("square", event_id, error_result)
        raise HTTPException(status_code=500, detail="Event processing failed")
