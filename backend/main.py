from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.api import api_router
from app.core.config import settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import os
import threading
import time
import requests

# Configure logging
log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="StressSense API",
    description="Backend API for the StressSense stress detection system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database connections and log status
try:
    from app.db import mongodb
    print("✅ MongoDB connection initialized successfully")
    logger.info("MongoDB connection initialized successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    logger.error(f"MongoDB connection failed: {e}")

try:
    from app.db.redis_cache import cache
    if cache.enabled:
        print("✅ Redis cache connection initialized successfully")
        logger.info("Redis cache connection initialized successfully")
    else:
        print("⚠️  Redis cache disabled (connection failed)")
        logger.warning("Redis cache disabled (connection failed)")
except Exception as e:
    print(f"❌ Redis cache initialization failed: {e}")
    logger.error(f"Redis cache initialization failed: {e}")

# Add API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB
        from app.db.mongodb import client
        client.admin.command('ping')
        mongo_status = "healthy"
    except Exception as e:
        mongo_status = f"unhealthy: {str(e)}"
    
    try:
        # Check Redis
        from app.db.redis_cache import cache
        if cache.enabled:
            cache.redis_client.ping()
            redis_status = "healthy"
        else:
            redis_status = "disabled"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if mongo_status == "healthy" and redis_status in ["healthy", "disabled"] else "unhealthy",
        "timestamp": time.time(),
        "services": {
            "mongodb": mongo_status,
            "redis": redis_status
        }
    }

# Function to perform health check every 3 minutes
def health_check_worker():
    """Background worker to perform health checks every 3 minutes"""
    while True:
        try:
            # Get the port from env or default
            port = int(os.environ.get("PORT", 8000))
            response = requests.get(f"http://localhost:{port}/health", timeout=10)
            if response.status_code == 200:
                logger.info("Health check passed")
            else:
                logger.warning(f"Health check failed with status: {response.status_code}")
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
        
        # Sleep for 3 minutes (180 seconds)
        time.sleep(180)

# Start health check worker in a separate thread
health_thread = threading.Thread(target=health_check_worker, daemon=True)
health_thread.start()
logger.info("Health check worker started (runs every 3 minutes)")

# Custom error handler for 500 errors
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "internal_server_error",
            "message": "An unexpected error occurred. Please try again.",
        },
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to StressSense API",
        "docs": "/docs",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
