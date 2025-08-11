from fastapi import FastAPI, APIRouter
from routes.receipts import router as receipts_router
from routes.statements import router as statements_router
from routes.reconciliation import router as reconciliation_router
from routes.data_room import router as data_room_router
from routes.health_metrics import router as health_router
from webhooks.square import router as square_router

app = FastAPI(title="SparkCreatives Cloud Run API")
app.include_router(health_router, tags=["health"])
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(receipts_router, tags=["receipts"])
api_v1.include_router(statements_router, tags=["statements"])
api_v1.include_router(reconciliation_router, tags=["reconciliation"])
api_v1.include_router(data_room_router, tags=["data-room"])
api_v1.include_router(square_router, prefix="/webhooks/square", tags=["webhooks-square"])
app.include_router(api_v1)
