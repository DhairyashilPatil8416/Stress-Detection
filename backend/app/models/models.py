import uuid
from datetime import datetime
from app.schemas.schemas import (
    UserCreate, User, EmployeeCreate, Employee,
    DeviceCreate, Device, DeviceWithKey, StressSubmission,
    StressRecord, CommandCreate, Command, CommandUpdate
)
from app.core.security.auth import get_password_hash, generate_api_key, hash_api_key
from app.db.mongodb import (
    users_collection, employees_collection, devices_collection,
    stress_records_collection, commands_collection
)
from app.db.redis_cache import cache
from app.core.config import settings, EMOTION_STRESS_MAP
import logging

logger = logging.getLogger(__name__)

# User operations
def create_user(user_data: UserCreate) -> User:
    """Create a new user account"""
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"
    
    # If registering as employee, ensure employee record exists
    if user_data.role == "employee":
        if not user_data.employee_id:
            # Generate employee_id if not provided
            user_data.employee_id = str(uuid.uuid4())
        
        # Check if employee already exists
        existing_employee = employees_collection.find_one({"employee_id": user_data.employee_id})
        if not existing_employee:
            # Create employee record
            employee_db = {
                "employee_id": user_data.employee_id,
                "display_name": getattr(user_data, 'full_name', user_data.username),
                "email": getattr(user_data, 'email', None),
                "department": getattr(user_data, 'department', 'General'),  # Use provided department or default to General
                "active": True,
                "created_at": created_at
            }
            employees_collection.insert_one(employee_db)
            logger.info(f"Created employee record for user {user_data.username} with employee_id {user_data.employee_id}")
    
    user_db = {
        "user_id": user_id,
        "username": user_data.username,
        "password_hash": get_password_hash(user_data.password),
        "role": user_data.role,
        "full_name": getattr(user_data, 'full_name', None),
        "email": getattr(user_data, 'email', None),
        "employee_id": user_data.employee_id,
        "active": True,
        "created_at": created_at
    }
    
    users_collection.insert_one(user_db)
    return User(**{k: v for k, v in user_db.items() if k != "password_hash"})

def get_user_by_username(username: str):
    """Get a user by username"""
    return users_collection.find_one({"username": username})

def get_user_by_id(user_id: str):
    """Get a user by ID"""
    return users_collection.find_one({"user_id": user_id})

def update_user(user_id: str, update_data):
    """Update a user's information"""
    update_fields = {}
    
    if update_data.username is not None:
        update_fields["username"] = update_data.username
    
    if update_data.password is not None:
        update_fields["password_hash"] = get_password_hash(update_data.password)
    
    if update_data.active is not None:
        update_fields["active"] = update_data.active
    
    if update_fields:
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": update_fields}
        )

# Employee operations
def create_employee(employee_data: EmployeeCreate) -> Employee:
    """Create a new employee record"""
    employee_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"
    
    employee_db = {
        "employee_id": employee_id,
        "display_name": employee_data.display_name,
        "email": employee_data.email,
        "department": employee_data.department,
        "active": True,
        "created_at": created_at
    }
    
    employees_collection.insert_one(employee_db)
    return Employee(**employee_db)

def get_employee(employee_id: str):
    """Get an employee by ID"""
    return employees_collection.find_one({"employee_id": employee_id})

def get_all_employees(active_only: bool = True):
    """Get all employees, optionally filtering by active status"""
    query = {"active": True} if active_only else {}
    return list(employees_collection.find(query))

def update_employee(employee_id: str, update_data):
    """Update an employee's information"""
    update_fields = {}
    
    if update_data.display_name is not None:
        update_fields["display_name"] = update_data.display_name
    
    if update_data.email is not None:
        update_fields["email"] = update_data.email
    
    if update_data.department is not None:
        update_fields["department"] = update_data.department
    
    if update_data.active is not None:
        update_fields["active"] = update_data.active
    
    if update_fields:
        employees_collection.update_one(
            {"employee_id": employee_id},
            {"$set": update_fields}
        )

# Device operations
def create_device(device_data: DeviceCreate) -> DeviceWithKey:
    """Create a new device and generate API key"""
    device_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"
    api_key = generate_api_key()
    api_key_hash = hash_api_key(api_key)
    
    device_db = {
        "device_id": device_id,
        "employee_id": device_data.employee_id,
        "device_name": device_data.device_name,
        "api_key_hash": api_key_hash,
        "active": True,
        "last_seen_at": None,
        "created_at": created_at
    }
    
    devices_collection.insert_one(device_db)
    return DeviceWithKey(**{**device_db, "api_key": api_key})

def get_device(device_id: str):
    """Get a device by ID"""
    return devices_collection.find_one({"device_id": device_id})

def get_devices_by_employee(employee_id: str, active_only: bool = True):
    """Get all devices for an employee, optionally filtering by active status"""
    query = {"employee_id": employee_id}
    if active_only:
        query["active"] = True
    
    return list(devices_collection.find(query))

def get_all_devices(active_only: bool = True):
    """Get all devices, optionally filtering by active status"""
    query = {"active": True} if active_only else {}
    return list(devices_collection.find(query))

def update_device(device_id: str, update_data):
    """Update a device's information and optionally rotate API key"""
    update_fields = {}
    api_key = None
    
    if update_data.device_name is not None:
        update_fields["device_name"] = update_data.device_name
    
    if update_data.active is not None:
        update_fields["active"] = update_data.active
    
    if update_data.rotate_key:
        api_key = generate_api_key()
        update_fields["api_key_hash"] = hash_api_key(api_key)
    
    if update_fields:
        devices_collection.update_one(
            {"device_id": device_id},
            {"$set": update_fields}
        )
    
    return api_key

# Stress record operations
def create_stress_record(submission: StressSubmission) -> StressRecord:
    """Create a new stress record from device submission"""
    record_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    
    # Check for mapping mismatch
    expected_level = EMOTION_STRESS_MAP.get(submission.emotion, {}).get("level")
    mapping_mismatch = False
    
    if expected_level and expected_level != submission.stress_level and submission.confidence > 60:
        logger.warning(f"Stress level mapping mismatch: emotion {submission.emotion} " +
                      f"should be {expected_level} but got {submission.stress_level}")
        mapping_mismatch = True
    
    record_db = {
        "record_id": record_id,
        "employee_id": submission.employee_id,
        "device_id": submission.device_id,
        "emotion": submission.emotion,
        "stress_level": submission.stress_level,
        "confidence": submission.confidence,
        "timestamp": submission.timestamp,
        "ingested_at": now,
        "mapping_mismatch": mapping_mismatch,
        "face_quality": submission.face_quality.dict() if submission.face_quality else None
    }
    
    logger.info(f"[DATABASE] Creating stress record: {record_db}")
    stress_records_collection.insert_one(record_db)
    logger.info(f"[DATABASE] Stress record created successfully with ID: {record_id}")

    # Clear cache for latest stress data since we have new data
    cache.delete("latest_stress_all_employees")
    cache.clear_pattern("employee_stress_history_*")
    logger.info("[CACHE] Cleared latest stress data cache after new record creation")

    return StressRecord(**record_db)

def get_stress_records_by_employee(employee_id: str, from_date=None, to_date=None, limit=50):
    """Get stress records for an employee with optional date filtering"""
    query = {"employee_id": employee_id}
    
    if from_date and to_date:
        query["timestamp"] = {"$gte": from_date, "$lte": to_date}
    elif from_date:
        query["timestamp"] = {"$gte": from_date}
    elif to_date:
        query["timestamp"] = {"$lte": to_date}
    
    return list(stress_records_collection.find(query).sort("timestamp", -1).limit(limit))

def get_latest_stress_by_employee(employee_id: str):
    """Get the most recent stress record for an employee"""
    records = list(stress_records_collection.find(
        {"employee_id": employee_id}
    ).sort("timestamp", -1).limit(1))
    
    return records[0] if records else None

def get_latest_stress_for_all_employees():
    """Get the most recent stress record for each active employee"""
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$employee_id",
            "latest_record": {"$first": "$$ROOT"}
        }},
        {"$replaceRoot": {"newRoot": "$latest_record"}}
    ]
    
    return list(stress_records_collection.aggregate(pipeline))

def get_all_stress_records(limit=100):
    """Get all stress records from the database (for demo/admin purposes)"""
    return list(stress_records_collection.find({}).sort("timestamp", -1).limit(limit))

# Command operations
def create_command(command_data: CommandCreate) -> Command:
    """Create a new command for a device"""
    command_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"
    
    command_db = {
        "command_id": command_id,
        "device_id": command_data.device_id,
        "type": command_data.type,
        "status": "pending",
        "created_at": created_at,
        "ack_at": None,
        "done_at": None,
        "error": None
    }
    
    commands_collection.insert_one(command_db)
    return Command(**command_db)

def get_pending_commands(device_id: str):
    """Get pending commands for a device"""
    return list(commands_collection.find({
        "device_id": device_id,
        "status": "pending"
    }))

def update_command(command_id: str, update_data: CommandUpdate):
    """Update a command's status"""
    update_fields = {"status": update_data.status}
    
    if update_data.status == "ack":
        update_fields["ack_at"] = datetime.utcnow().isoformat() + "Z"
    elif update_data.status in ["done", "failed"]:
        update_fields["done_at"] = datetime.utcnow().isoformat() + "Z"
    
    if update_data.error:
        update_fields["error"] = update_data.error
    
    commands_collection.update_one(
        {"command_id": command_id},
        {"$set": update_fields}
    )

def process_image_for_stress(image_base64: str, device_id: str, employee_id: str) -> dict:
    """
    Process an image to detect stress and save the result
    This combines our ML model with database storage
    """
    from app.models.stress_analysis import analyze_image
    
    # Analyze the image
    analysis_result = analyze_image(image_base64)
    
    # If error, return the error
    if "error" in analysis_result:
        return analysis_result
    
    # Create a submission from the analysis
    submission = StressSubmission(
        device_id=device_id,
        employee_id=employee_id,
        emotion=analysis_result["emotion"],
        stress_level=analysis_result["stress_level"],
        confidence=analysis_result["confidence"],
        timestamp=datetime.utcnow().isoformat() + "Z",
        face_quality=analysis_result.get("face_quality")
    )
    
    # Save the record
    record = create_stress_record(submission)
    
    # Return combined result
    return {
        **analysis_result,
        "record_id": record.record_id
    }
