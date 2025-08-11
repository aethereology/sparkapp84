# API (Cloud Run — FastAPI)
Endpoints under /api/v1:
- GET  /donations/{id}/receipt.pdf
- POST /donations/{id}/receipt
- GET  /donors/{id}/statement/{year}
- POST /tasks/year-end-statements?year=YYYY
- POST /reconciliation/run
- GET  /reconciliation/latest
- POST /webhooks/square
- GET  /data-room/documents?org=spark&reviewer=true
Root: /health, /metrics
Env: REDIS_URL,* GCS_BUCKET_*, SQUARE_WEBHOOK_SIGNATURE_KEY, SQUARE_NOTIFICATION_URL, etc.
