from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Any, Optional
from datetime import datetime, timedelta
from app.schemas.schemas import (
    User, LatestStressRecord, StressRecord, Command, CommandCreate,
    StressAggregateResponse, TimeseriesPoint, AggregateStats, DepartmentStats
)
from app.models.models import (
    get_latest_stress_for_all_employees, get_stress_records_by_employee,
    get_employee, get_all_employees, create_command, get_device
)
from app.db.mongodb import stress_records_collection, employees_collection
from app.db.redis_cache import cache
from app.core.security.deps import get_current_manager
import logging
from pymongo import DESCENDING

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/employees", response_model=List[dict])
async def get_all_employees_endpoint(
    current_user: User = Depends(get_current_manager)
):
    """Get a list of all active employees (manager only)"""
    employees = get_all_employees()
    
    # Clean MongoDB _id from results
    for employee in employees:
        if "_id" in employee:
            employee.pop("_id")
    
    return employees

@router.get("/employee/{employee_id}", response_model=dict)
async def get_employee_details(
    employee_id: str,
    current_user: User = Depends(get_current_manager)
) -> Any:
    '''
    Get detailed information about a specific employee (manager only)
    '''
    # Get employee details
    employee = get_employee(employee_id)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Clean MongoDB _id
    if "_id" in employee:
        employee.pop("_id")
        
    return employee

@router.get("/employee/{employee_id}", response_model=dict)
async def get_employee_details(
    employee_id: str,
    current_user: User = Depends(get_current_manager)
) -> Any:
    '''
    Get detailed information about a specific employee (manager only)
    '''
    # Get employee details
    employee = get_employee(employee_id)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Clean MongoDB _id
    if "_id" in employee:
        employee.pop("_id")
        
    return employee

@router.get("/stress/latest", response_model=List[LatestStressRecord])
async def get_latest_stress_all_employees(
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Get the latest stress record for each active employee (manager only)
    """
    cache_key = "latest_stress_all_employees"

    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info("Returning cached latest stress data")
        return cached_result

    # Get latest stress records from database
    latest_records = get_latest_stress_for_all_employees()

    # Format the response
    result = []
    for record in latest_records:
        # Get employee details
        employee = get_employee(record["employee_id"])
        if not employee or not employee.get("active", True):
            continue

        result.append({
            "employee_id": record["employee_id"],
            "display_name": employee["display_name"],
            "department": employee.get("department", "N/A"),
            "latest_stress_level": record["stress_level"],
            "latest_emotion": record["emotion"],
            "confidence": record["confidence"],
            "timestamp": record["timestamp"],
            "device_id": record["device_id"]
        })

    # Cache the result for 30 seconds
    cache.set(cache_key, result, 30)
    logger.info("Cached latest stress data for 30 seconds")

    return result

@router.get("/stress/history/{employee_id}", response_model=List[StressRecord])
async def get_employee_stress_history(
    employee_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Get stress history for a specific employee (manager only)
    """
    # Verify employee exists
    employee = get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get stress records with date filtering
    records = get_stress_records_by_employee(employee_id, from_date, to_date, limit)
    
    # Clean MongoDB _id from results
    for record in records:
        if "_id" in record:
            record.pop("_id")
    
    return records

@router.get("/stress/aggregate", response_model=StressAggregateResponse)
async def get_stress_aggregates(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    group_by: str = Query("day", regex="^(day|week|department)$"),
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Get stress level aggregates with optional grouping (manager only)
    """
    # Build query for date range
    query = {}
    if from_date or to_date:
        query["timestamp"] = {}
        if from_date:
            query["timestamp"]["$gte"] = from_date
        if to_date:
            query["timestamp"]["$lte"] = to_date
    
    # Get total counts by stress level
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$stress_level",
            "count": {"$sum": 1}
        }}
    ]
    
    stress_counts = list(stress_records_collection.aggregate(pipeline))
    
    # Initialize counts
    high_count = 0
    medium_count = 0
    low_count = 0
    
    # Extract counts from results
    for item in stress_counts:
        if item["_id"] == "High":
            high_count = item["count"]
        elif item["_id"] == "Medium":
            medium_count = item["count"]
        elif item["_id"] == "Low":
            low_count = item["count"]
    
    total_count = high_count + medium_count + low_count
    
    # Calculate percentages
    high_pct = (high_count / total_count) * 100 if total_count > 0 else 0
    medium_pct = (medium_count / total_count) * 100 if total_count > 0 else 0
    low_pct = (low_count / total_count) * 100 if total_count > 0 else 0
    
    # Build time series data
    timeseries = []
    daily_trend = []
    
    if group_by == "day":
        # Group by day
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": {
                    "$substr": ["$timestamp", 0, 10]  # YYYY-MM-DD
                },
                "high_count": {
                    "$sum": {"$cond": [{"$eq": ["$stress_level", "High"]}, 1, 0]}
                },
                "medium_count": {
                    "$sum": {"$cond": [{"$eq": ["$stress_level", "Medium"]}, 1, 0]}
                },
                "low_count": {
                    "$sum": {"$cond": [{"$eq": ["$stress_level", "Low"]}, 1, 0]}
                },
                "total": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        daily_data = list(stress_records_collection.aggregate(pipeline))
        
        # Build daily trend data for frontend
        daily_trend = []
        for day in daily_data:
            daily_trend.append({
                "date": day["_id"],
                "Low": day.get("low_count", 0),
                "Medium": day.get("medium_count", 0),
                "High": day.get("high_count", 0)
            })
        
        for day in daily_data:
            # Calculate stress score (0-100)
            # Higher weight to High stress, medium weight to Medium stress
            stress_score = 0
            if day["total"] > 0:
                stress_score = ((day["high_count"] * 100) + (day["medium_count"] * 50)) / day["total"]
            
            timeseries.append({
                "timestamp": f"{day['_id']}T00:00:00Z",
                "value": stress_score
            })
    
    elif group_by == "week":
        # Use MongoDB date operators to group by week
        # This is a simplified approach - in a real system you'd use 
        # MongoDB's date operators for accurate week calculations
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": {
                    "$substr": ["$timestamp", 0, 10]  # YYYY-MM-DD (we'll aggregate by week in Python)
                },
                "high_count": {
                    "$sum": {"$cond": [{"$eq": ["$stress_level", "High"]}, 1, 0]}
                },
                "medium_count": {
                    "$sum": {"$cond": [{"$eq": ["$stress_level", "Medium"]}, 1, 0]}
                },
                "low_count": {
                    "$sum": {"$cond": [{"$eq": ["$stress_level", "Low"]}, 1, 0]}
                },
                "total": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        daily_data = list(stress_records_collection.aggregate(pipeline))
        
        # Group days into weeks
        weekly_data = {}
        for day in daily_data:
            date_obj = datetime.strptime(day["_id"], "%Y-%m-%d")
            year, week_num, _ = date_obj.isocalendar()
            week_key = f"{year}-W{week_num:02d}"
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    "high_count": 0,
                    "medium_count": 0,
                    "low_count": 0,
                    "total": 0,
                    "start_date": date_obj - timedelta(days=date_obj.weekday())  # Monday
                }
            
            weekly_data[week_key]["high_count"] += day["high_count"]
            weekly_data[week_key]["medium_count"] += day["medium_count"]
            weekly_data[week_key]["low_count"] += day["low_count"]
            weekly_data[week_key]["total"] += day["total"]
        
        # Convert to timeseries
        for week_key, data in sorted(weekly_data.items()):
            # Calculate stress score
            stress_score = 0
            if data["total"] > 0:
                stress_score = ((data["high_count"] * 100) + (data["medium_count"] * 50)) / data["total"]
            
            timeseries.append({
                "timestamp": data["start_date"].strftime("%Y-%m-%dT00:00:00Z"),
                "value": stress_score
            })
    
    # Department statistics (if requested)
    department_stats = []
    if group_by == "department":
        # Get all active employees with their departments
        employees = get_all_employees(active_only=True)
        
        # Group employees by department
        dept_employees = {}
        for emp in employees:
            dept = emp.get("department", "Unassigned")
            if dept not in dept_employees:
                dept_employees[dept] = []
            dept_employees[dept].append(emp["employee_id"])
        
        # For each department, calculate stress level percentages
        for dept, emp_ids in dept_employees.items():
            dept_query = query.copy()
            dept_query["employee_id"] = {"$in": emp_ids}
            
            pipeline = [
                {"$match": dept_query},
                {"$group": {
                    "_id": "$stress_level",
                    "count": {"$sum": 1}
                }}
            ]
            
            dept_stress = list(stress_records_collection.aggregate(pipeline))
            
            # Initialize counts
            dept_high = 0
            dept_medium = 0
            dept_low = 0
            
            for item in dept_stress:
                if item["_id"] == "High":
                    dept_high = item["count"]
                elif item["_id"] == "Medium":
                    dept_medium = item["count"]
                elif item["_id"] == "Low":
                    dept_low = item["count"]
            
            dept_total = dept_high + dept_medium + dept_low
            
            # Calculate percentages
            if dept_total > 0:
                department_stats.append({
                    "department": dept,
                    "high_stress_percentage": (dept_high / dept_total) * 100,
                    "medium_stress_percentage": (dept_medium / dept_total) * 100,
                    "low_stress_percentage": (dept_low / dept_total) * 100
                })
    
    # Build response
    response = {
        "overall": {
            "total_records": total_count,
            "high_stress_count": high_count,
            "medium_stress_count": medium_count,
            "low_stress_count": low_count,
            "high_stress_percentage": high_pct,
            "medium_stress_percentage": medium_pct,
            "low_stress_percentage": low_pct
        },
        "distribution": {
            "Low": low_count,
            "Medium": medium_count,
            "High": high_count
        },
        "timeseries": timeseries
    }
    
    if daily_trend:
        response["dailyTrend"] = daily_trend
        response["timeline"] = daily_trend  # For backward compatibility
    
    if department_stats:
        response["departments"] = department_stats
    
    return response


@router.get("/stress/aggregate_test", response_model=dict)
async def get_stress_aggregates_test(
    current_user: User = Depends(get_current_manager)
):
    """Test endpoint that returns dummy stress aggregates for frontend testing"""
    # Return dummy data for frontend testing
    return {
        "summary": {
            "uniqueEmployees": 5,
            "totalReadings": 50,
            "avgStressLevel": 45.5
        },
        "distribution": {
            "Low": 20,
            "Medium": 20,
            "High": 10
        },
        "timeline": [
            {"date": "2025-08-15", "Low": 4, "Medium": 3, "High": 2},
            {"date": "2025-08-16", "Low": 5, "Medium": 2, "High": 1},
            {"date": "2025-08-17", "Low": 3, "Medium": 4, "High": 2},
            {"date": "2025-08-18", "Low": 2, "Medium": 5, "High": 3},
            {"date": "2025-08-19", "Low": 6, "Medium": 2, "High": 1}
        ],
        "departments": [
            {"name": "Engineering", "avgStress": 35.2},
            {"name": "Marketing", "avgStress": 48.7},
            {"name": "Sales", "avgStress": 52.3}
        ]
    }


@router.post("/trigger/{employee_id}", response_model=Command)
async def trigger_analyze_for_employee(
    employee_id: str,
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Trigger an ANALYZE_NOW command for an employee's active devices (manager only)
    """
    # Verify employee exists
    employee = get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get active devices for employee
    from app.models.models import get_devices_by_employee
    devices = get_devices_by_employee(employee_id, active_only=True)
    
    if not devices:
        raise HTTPException(
            status_code=404,
            detail="No active devices found for this employee"
        )
    
    # Create command for the first active device
    command_data = CommandCreate(
        device_id=devices[0]["device_id"],
        type="ANALYZE_NOW"
    )
    
    command = create_command(command_data)
    logger.info(f"Created ANALYZE_NOW command {command.command_id} for device {devices[0]['device_id']}")
    
    return command
