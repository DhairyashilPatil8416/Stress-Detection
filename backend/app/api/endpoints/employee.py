from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Any, Optional, Dict
from app.schemas.schemas import User, StressRecord
from app.models.models import get_latest_stress_by_employee, get_stress_records_by_employee
from app.core.security.deps import get_current_employee
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/stress/latest", response_model=StressRecord)
async def get_my_latest_stress(
    current_user: User = Depends(get_current_employee)
) -> Any:
    """
    Get the employee's latest stress reading (self view)
    """
    employee_id = current_user.get("employee_id")
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile associated with this user account"
        )
    
    record = get_latest_stress_by_employee(employee_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stress records found"
        )
    
    # Clean MongoDB _id
    if "_id" in record:
        record.pop("_id")
    
    return record

@router.get("/stress/history", response_model=List[StressRecord])
async def get_my_stress_history(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),  # Lower limit for employee view
    current_user: User = Depends(get_current_employee)
) -> Any:
    """
    Get the employee's stress history (self view)
    """
    employee_id = current_user.get("employee_id")
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile associated with this user account"
        )
    
    records = get_stress_records_by_employee(employee_id, from_date, to_date, limit)
    
    # Clean MongoDB _id from results
    for record in records:
        if "_id" in record:
            record.pop("_id")
    
    return records

@router.get("/stress/suggestions", response_model=Dict[str, List[str]])
async def get_stress_suggestions(
    current_user: User = Depends(get_current_employee)
) -> Any:
    """
    Get suggestions based on latest stress level
    """
    employee_id = current_user.get("employee_id")
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee profile associated with this user account"
        )
    
    record = get_latest_stress_by_employee(employee_id)
    
    if not record:
        # If no record, return all suggestions
        return {"suggestions": [
            item for sublist in settings.STRESS_SUGGESTIONS.values() for item in sublist
        ]}
    
    stress_level = record.get("stress_level", "Medium")
    
    return {"suggestions": settings.STRESS_SUGGESTIONS.get(stress_level, [])}

@router.get("/privacy", response_model=Dict[str, str])
async def get_privacy_info(
    current_user: User = Depends(get_current_employee)
) -> Any:
    """
    Get privacy information for the employee
    """
    return {"privacy_banner": settings.PRIVACY_BANNER}

@router.get("/stress/history/{employee_id}", status_code=status.HTTP_200_OK)
async def get_employee_stress_history(
    employee_id: str,
    days: Optional[int] = Query(7, description="Number of days of history to retrieve")
) -> Any:
    """
    Get stress history for an employee
    """
    try:
        # Get stress readings from database
        from app.db.mongodb import stress_readings_collection
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query database
        readings = list(stress_readings_collection.find({
            "employee_id": employee_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).sort("timestamp", -1))
        
        # Clean MongoDB _id from results and convert datetimes to strings
        for reading in readings:
            if "_id" in reading:
                reading.pop("_id")
            # Convert datetime to ISO format string
            if "timestamp" in reading and isinstance(reading["timestamp"], datetime):
                reading["timestamp"] = reading["timestamp"].isoformat() + "Z"
        
        # Create daily summaries
        daily_summaries = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            next_date = current_date + timedelta(days=1)
            
            # Filter readings for the current day
            day_readings = [
                r for r in readings 
                if current_date <= datetime.fromisoformat(r["timestamp"].replace('Z', '')).date() < next_date
            ]
            
            # Calculate stress level counts
            stress_counts = {"Low": 0, "Medium": 0, "High": 0}
            for r in day_readings:
                level = r.get("stress_level")
                if level in stress_counts:
                    stress_counts[level] += 1
            
            # Determine dominant stress level
            dominant_level = "Low"
            max_count = 0
            for level, count in stress_counts.items():
                if count > max_count:
                    max_count = count
                    dominant_level = level
            
            # Create summary
            summary = {
                "date": current_date.isoformat(),
                "reading_count": len(day_readings),
                "stress_levels": stress_counts,
                "dominant_level": dominant_level
            }
            daily_summaries.append(summary)
            
            # Move to next day
            current_date = next_date
        
        return {
            "employee_id": employee_id,
            "days": days,
            "readings": readings,
            "daily_summaries": daily_summaries
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving stress history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred retrieving stress history"
        )
