from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.models.models import process_image_for_stress
from app.schemas.schemas import ImageData, StressRecord
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/predict-stress", response_model=Dict[str, Any])
async def predict_stress(data: ImageData) -> Dict[str, Any]:
    """
    Process an image directly to predict stress levels
    This endpoint maintains compatibility with the original API
    """
    try:
        if not data.image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No image data provided"
            )
        
        # Process the image (no device/employee auth for direct API)
        # This is for backward compatibility with the original API
        device_id = "direct-api"
        employee_id = "api-user"
        
        result = process_image_for_stress(
            data.image,
            device_id,
            employee_id
        )
        
        # Check for errors
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting stress: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred processing the image"
        )
