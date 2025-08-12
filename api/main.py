import logging
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from routes.receipts import router as receipts_router
from routes.statements import router as statements_router
from routes.reconciliation import router as reconciliation_router
from routes.data_room import router as data_room_router
from routes.health_metrics import router as health_router
from webhooks.square import router as square_router
from auth import router as auth_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
ENVIRONMENT = os.getenv("ENV", "local")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"SparkCreatives API starting up - Environment: {ENVIRONMENT}")
    yield
    # Shutdown  
    logger.info("SparkCreatives API shutting down")

app = FastAPI(
    title="SparkCreatives Cloud Run API",
    description="Donation management API with authentication",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Security middleware
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=ALLOWED_HOSTS
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()} - {request.method} {request.url}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)} - {request.method} {request.url}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s"
    )
    return response

# Include routers
app.include_router(auth_router)  # Authentication routes
app.include_router(health_router, tags=["health"])

# Protected API routes
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(receipts_router, tags=["receipts"])
api_v1.include_router(statements_router, tags=["statements"]) 
api_v1.include_router(reconciliation_router, tags=["reconciliation"])
api_v1.include_router(data_room_router, tags=["data-room"])

# Webhook routes (no auth required)
api_v1.include_router(square_router, prefix="/webhooks/square", tags=["webhooks-square"])

app.include_router(api_v1)
