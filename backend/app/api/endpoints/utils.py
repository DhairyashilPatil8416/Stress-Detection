from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.core.config import settings
import logging
import platform
import psutil
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "0.1.0",
    }

@router.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """
    Simple metrics endpoint
    """
    try:
        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Server metrics
        from app.db.mongodb import (
            users_collection, employees_collection,
            devices_collection, stress_records_collection
        )
        
        # Get counts
        user_count = users_collection.count_documents({})
        employee_count = employees_collection.count_documents({"active": True})
        device_count = devices_collection.count_documents({"active": True})
        
        # Get stress counts by level for today
        today = datetime.utcnow().strftime("%Y-%m-%d")
        high_stress = stress_records_collection.count_documents({
            "timestamp": {"$regex": f"^{today}"},
            "stress_level": "High"
        })
        
        total_today = stress_records_collection.count_documents({
            "timestamp": {"$regex": f"^{today}"}
        })
        
        high_pct = (high_stress / total_today * 100) if total_today > 0 else 0
        
        # Total records in the last week
        week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        weekly_records = stress_records_collection.count_documents({
            "timestamp": {"$gte": week_ago}
        })
        
        return {
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "python_version": platform.python_version(),
            },
            "application": {
                "user_count": user_count,
                "active_employees": employee_count,
                "active_devices": device_count,
                "high_stress_today_pct": high_pct,
                "records_last_7_days": weekly_records
            }
        }
    except Exception as e:
        logger.error(f"Error generating metrics: {str(e)}")
        return {
            "status": "error",
            "message": "Error generating metrics"
        }
