from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Query, Body
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from app.schemas.schemas import StressSubmission, StressResponse
from app.models.models import create_stress_record
from app.core.security.deps import verify_device_api_key, limiter
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/record", status_code=status.HTTP_201_CREATED)
async def record_stress(
    request: Request,
    data: Dict[str, Any] = Body(...),
    device: Dict[str, Any] = Depends(verify_device_api_key)
) -> Any:
    """
    Record a stress reading from a device.
    API key can be provided either in X-Device-Key header or as api_key query parameter.
    """
    logger.info(f"[BACKEND] Received stress record request")
    logger.info(f"[BACKEND] Request data: {data}")
    logger.info(f"[BACKEND] Device info: {device}")
    logger.info(f"[BACKEND] Headers: {dict(request.headers)}")
    
    try:
        # Get device and employee IDs from the authenticated device
        device_id = device.get("device_id")
        employee_id = device.get("employee_id")
        logger.info(f"Authenticated device: {device_id}, employee: {employee_id}")
        
        # Validate required fields
        if not data.get("emotion") or not data.get("stress_level") or not data.get("confidence"):
            logger.error(f"Missing required fields in data: {data}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: emotion, stress_level, confidence"
            )
        
        # Validate emotion enum
        valid_emotions = ["happy", "neutral", "sad", "angry", "fear", "disgust", "surprise"]
        if data["emotion"] not in valid_emotions:
            logger.error(f"Invalid emotion: {data['emotion']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid emotion. Must be one of: {', '.join(valid_emotions)}"
            )
        
        # Validate stress level enum
        valid_levels = ["Low", "Medium", "High"]
        if data["stress_level"] not in valid_levels:
            logger.error(f"Invalid stress_level: {data['stress_level']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stress_level. Must be one of: {', '.join(valid_levels)}"
            )
        
        logger.info(f"Validation passed. Creating stress record for emotion: {data['emotion']}, stress_level: {data['stress_level']}")
        
        # Create stress record using the model function
        from app.schemas.schemas import StressSubmission
        submission = StressSubmission(
            device_id=device_id,
            employee_id=employee_id,
            emotion=data["emotion"],
            stress_level=data["stress_level"],
            confidence=float(data["confidence"]),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            face_quality=data.get("face_quality")
        )
        
        record = create_stress_record(submission)
        logger.info(f"Successfully created stress record {record.record_id} for employee {employee_id}")
        
        return {
            "record_id": record.record_id,
            "message": "Stress reading recorded successfully"
        }
        
    except HTTPException:
        logger.error(f"HTTPException in record_stress: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in record_stress: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred recording the stress reading"
        )

@router.get("/remote-check/{employee_id}")
async def check_remote_stress_request(employee_id: str) -> Dict[str, Any]:
    """
    Check for pending remote stress check requests for an employee.
    This endpoint is polled by the Windows app to check if a manager has requested a stress check.
    """
    try:
        from app.db.mongodb import commands_collection
        from app.schemas.schemas import CommandStatusEnum
        
        logger.info(f"[REMOTE CHECK] Checking for pending remote requests for employee: {employee_id}")
        
        # Find the most recent pending ANALYZE_NOW command for this employee
        # First get the device_id for this employee
        from app.db.mongodb import devices_collection
        device = devices_collection.find_one({
            "employee_id": employee_id,
            "active": True
        })
        
        if not device:
            logger.warning(f"[REMOTE CHECK] No active device found for employee: {employee_id}")
            return {"pending_request": False}
        
        device_id = device["device_id"]
        
        # Look for pending ANALYZE_NOW commands for this device
        pending_command = commands_collection.find_one({
            "device_id": device_id,
            "type": "ANALYZE_NOW",
            "status": "pending"
        }, sort=[("created_at", -1)])  # Get the most recent one
        
        if pending_command:
            logger.info(f"[REMOTE CHECK] Found pending remote request: {pending_command['command_id']}")
            return {
                "pending_request": True,
                "request_id": pending_command["command_id"],
                "command_type": pending_command["type"],
                "created_at": pending_command["created_at"]
            }
        else:
            logger.debug(f"[REMOTE CHECK] No pending requests for employee: {employee_id}")
            return {"pending_request": False}
            
    except Exception as e:
        logger.error(f"[REMOTE CHECK] Error checking remote requests: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking for remote stress requests"
        )

@router.post("/remote-submit")
async def submit_remote_stress(
    request: Request,
    data: Dict[str, Any] = Body(...),
    device: Dict[str, Any] = Depends(verify_device_api_key)
) -> Dict[str, Any]:
    """
    Submit stress data from a remote request.
    This endpoint handles stress data submitted in response to a remote check request.
    """
    try:
        logger.info(f"[REMOTE SUBMIT] Received remote stress submission")
        logger.info(f"[REMOTE SUBMIT] Request data: {data}")
        
        # Get device and employee IDs from the authenticated device
        device_id = device.get("device_id")
        employee_id = device.get("employee_id")
        
        # Validate required fields
        required_fields = ["stress_level", "emotion", "confidence", "request_id"]
        for field in required_fields:
            if field not in data:
                logger.error(f"[REMOTE SUBMIT] Missing required field: {field}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Validate emotion enum
        valid_emotions = ["happy", "neutral", "sad", "angry", "fear", "disgust", "surprise"]
        if data["emotion"] not in valid_emotions:
            logger.error(f"[REMOTE SUBMIT] Invalid emotion: {data['emotion']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid emotion. Must be one of: {', '.join(valid_emotions)}"
            )
        
        # Validate stress level enum
        valid_levels = ["Low", "Medium", "High"]
        if data["stress_level"] not in valid_levels:
            logger.error(f"[REMOTE SUBMIT] Invalid stress_level: {data['stress_level']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stress_level. Must be one of: {', '.join(valid_levels)}"
            )
        
        # Update the command status to 'done'
        from app.db.mongodb import commands_collection
        request_id = data["request_id"]
        
        update_result = commands_collection.update_one(
            {"command_id": request_id, "device_id": device_id},
            {
                "$set": {
                    "status": "done",
                    "done_at": datetime.utcnow().isoformat() + "Z"
                }
            }
        )
        
        if update_result.modified_count == 0:
            logger.warning(f"[REMOTE SUBMIT] Could not update command status for request_id: {request_id}")
        
        # Create stress record
        from app.schemas.schemas import StressSubmission
        submission = StressSubmission(
            device_id=device_id,
            employee_id=employee_id,
            emotion=data["emotion"],
            stress_level=data["stress_level"],
            confidence=float(data["confidence"]),
            timestamp=datetime.utcnow().isoformat(),
            face_quality=None  # Remote submissions don't include face quality
        )
        
        record = create_stress_record(submission)
        logger.info(f"[REMOTE SUBMIT] Successfully created remote stress record {record.record_id} for employee {employee_id}")
        
        return {
            "record_id": record.record_id,
            "message": "Remote stress reading recorded successfully",
            "request_id": request_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[REMOTE SUBMIT] Error submitting remote stress data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting remote stress data"
        )
