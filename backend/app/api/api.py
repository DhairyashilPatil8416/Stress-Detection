from fastapi import APIRouter
from app.api.endpoints import auth, admin, stress, device, manager, employee, utils, journal, predict

api_router = APIRouter()

# Auth endpoints
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["authentication"]
)

# Admin endpoints (manager only)
api_router.include_router(
    admin.router, 
    prefix="/admin", 
    tags=["admin"]
)

# Stress submission endpoints (device)
api_router.include_router(
    stress.router, 
    prefix="/stress", 
    tags=["stress"]
)

# Device command endpoints
api_router.include_router(
    device.router, 
    prefix="/device", 
    tags=["device"]
)

# Devices endpoints (by device ID)
api_router.include_router(
    device.router, 
    prefix="/devices", 
    tags=["devices"]
)

# Manager dashboard endpoints
api_router.include_router(
    manager.router, 
    prefix="/manager", 
    tags=["manager"]
)

# Employee self-view endpoints
api_router.include_router(
    employee.router, 
    prefix="/me", 
    tags=["employee"]
)

# Employee data endpoints
api_router.include_router(
    employee.router, 
    prefix="/employee", 
    tags=["employee_data"]
)

# Journal endpoints
api_router.include_router(
    journal.router,
    prefix="/journal-entries",
    tags=["journal"]
)

# Image processing endpoint (direct API)
api_router.include_router(
    predict.router, 
    prefix="/predict", 
    tags=["predict"]
)

# Utility endpoints
api_router.include_router(
    utils.router, 
    prefix="/utils", 
    tags=["utils"]
)
