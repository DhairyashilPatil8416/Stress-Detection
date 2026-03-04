from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import List, Any, Optional
from app.schemas.schemas import (
    Employee, EmployeeCreate, EmployeeUpdate,
    Device, DeviceCreate, DeviceUpdate, DeviceWithKey,
    User, UserCreate, UserUpdate
)
from app.models.models import (
    create_employee, get_employee, get_all_employees, update_employee,
    create_device, get_device, get_devices_by_employee, get_all_devices, update_device,
    get_user_by_id, update_user
)
from app.core.security.deps import get_current_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Employee endpoints
@router.post("/employees", response_model=Employee)
async def create_new_employee(
    employee_data: EmployeeCreate,
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Create new employee (manager only)
    """
    logger.info(f"Creating new employee: {employee_data.display_name}")
    return create_employee(employee_data)

@router.get("/employees", response_model=List[Employee])
async def read_employees(
    current_user: User = Depends(get_current_manager),
    active_only: bool = True
) -> Any:
    """
    Get all employees (manager only)
    """
    employees = get_all_employees(active_only)
    return employees

@router.get("/employees/{employee_id}", response_model=Employee)
async def read_employee(
    employee_id: str,
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Get a specific employee by ID (manager only)
    """
    employee = get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee_info(
    employee_id: str,
    employee_data: EmployeeUpdate,
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Update an employee (manager only)
    """
    employee = get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    update_employee(employee_id, employee_data)
    
    # Return updated employee
    return get_employee(employee_id)

# Device endpoints
@router.post("/devices", response_model=DeviceWithKey)
async def create_new_device(
    device_data: DeviceCreate,
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Create a new device bound to an employee (manager only)
    Returns API key only once - must be saved immediately
    """
    employee = get_employee(device_data.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    logger.info(f"Creating new device for employee ID: {device_data.employee_id}")
    return create_device(device_data)

@router.get("/devices", response_model=List[Device])
async def read_devices(
    current_user: User = Depends(get_current_manager),
    employee_id: Optional[str] = None,
    active_only: bool = True
) -> Any:
    """
    Get all devices, optionally filtered by employee (manager only)
    """
    if employee_id:
        # Check if employee exists
        employee = get_employee(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        devices = get_devices_by_employee(employee_id, active_only)
    else:
        devices = get_all_devices(active_only)
    
    return devices

@router.get("/devices/{device_id}", response_model=Device)
async def read_device(
    device_id: str,
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Get a specific device by ID (manager only)
    """
    device = get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.patch("/devices/{device_id}", response_model=Device)
async def update_device_info(
    device_id: str,
    device_data: DeviceUpdate,
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Update a device or rotate API key (manager only)
    If rotate_key is true, a new API key will be generated and old one will be invalidated
    """
    device = get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    new_api_key = update_device(device_id, device_data)
    
    if new_api_key:
        logger.info(f"Rotated API key for device: {device_id}")
        return {**get_device(device_id), "api_key": new_api_key}
    
    return get_device(device_id)

# User account management
@router.patch("/users/{user_id}", response_model=User)
async def update_user_account(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_manager)
) -> Any:
    """
    Update a user account (manager only)
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_user(user_id, user_data)
    
    # Return updated user
    updated_user = get_user_by_id(user_id)
    
    # Remove password_hash before returning
    if updated_user and "_id" in updated_user:
        updated_user.pop("_id", None)
    if updated_user and "password_hash" in updated_user:
        updated_user.pop("password_hash", None)
    
    return updated_user
