"""
Seed script to initialize the database with a manager account and test data.
Run this script once to set up initial data in the MongoDB database.
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from passlib.context import CryptContext
import hashlib
import secrets
import string
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("DB_NAME", "stress_sense_db")
DEVICE_KEY_PEPPER = os.getenv("DEVICE_KEY_PEPPER", "insecure_pepper_change_this_in_production")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users_collection = db["users"]
    employees_collection = db["employees"]
    devices_collection = db["devices"]
    stress_records_collection = db["stress_records"]
    logger.info(f"Connected to MongoDB: {MONGO_URI}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    sys.exit(1)

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper functions
def get_password_hash(password):
    return pwd_context.hash(password)

def generate_api_key(length=32):
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return api_key

def hash_api_key(api_key):
    peppered = api_key + DEVICE_KEY_PEPPER
    return hashlib.sha256(peppered.encode()).hexdigest()

# Data seeding functions
def seed_manager():
    """Create a manager account if none exists"""
    # Check for existing HR manager
    hr_manager = users_collection.find_one({"username": "HR"})
    
    # Always create/update the HR manager
    if hr_manager:
        logger.info(f"HR manager already exists, updating password and ensuring account is active")
        users_collection.update_one(
            {"_id": hr_manager["_id"]},
            {"$set": {
                "password_hash": get_password_hash("admin123"),
                "role": "manager",
                "active": True
            }}
        )
        return
    else:
        # Create HR manager
        hr_manager_data = {
            "user_id": str(uuid.uuid4()),
            "username": "HR",
            "password_hash": get_password_hash("admin123"),
            "role": "manager",
            "employee_id": None,
            "active": True,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        users_collection.insert_one(hr_manager_data)
        logger.info(f"Created HR manager account: {hr_manager_data['username']}")
    
    # Check for general manager
    existing_manager = users_collection.find_one({"username": "admin"})
    
    if existing_manager:
        logger.info(f"Manager already exists: {existing_manager['username']}")
        return
    
    manager_data = {
        "user_id": str(uuid.uuid4()),
        "username": "admin",
        "password_hash": get_password_hash("adminpassword"),
        "role": "manager",
        "employee_id": None,
        "active": True,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    users_collection.insert_one(manager_data)
    logger.info(f"Created manager account: {manager_data['username']}")

def seed_employees():
    """Create sample employees if none exist"""
    existing_employees = list(employees_collection.find())
    
    if existing_employees:
        logger.info(f"Found {len(existing_employees)} existing employees, skipping employee creation")
        return existing_employees
    
    departments = ["Engineering", "Marketing", "HR", "Sales", "Finance"]
    test_employees = [
        {"name": "John Smith", "department": "Engineering", "email": "john@example.com"},
        {"name": "Sarah Johnson", "department": "Marketing", "email": "sarah@example.com"},
        {"name": "Michael Brown", "department": "HR", "email": "michael@example.com"},
        {"name": "Emily Davis", "department": "Sales", "email": "emily@example.com"},
        {"name": "David Wilson", "department": "Finance", "email": "david@example.com"},
    ]
    
    created_employees = []
    
    for emp in test_employees:
        employee_id = str(uuid.uuid4())
        employee_data = {
            "employee_id": employee_id,
            "display_name": emp["name"],
            "email": emp["email"],
            "department": emp["department"],
            "active": True,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        employees_collection.insert_one(employee_data)
        created_employees.append(employee_data)
        
        # Create user account for each employee
        user_data = {
            "user_id": str(uuid.uuid4()),
            "username": emp["email"].split("@")[0],  # Use first part of email as username
            "password_hash": get_password_hash("password123"),
            "role": "employee",
            "employee_id": employee_id,
            "active": True,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        users_collection.insert_one(user_data)
        
        logger.info(f"Created employee: {emp['name']} with user account: {user_data['username']}")
    
    return created_employees

def seed_devices(employees):
    """Create sample devices for employees"""
    if not employees:
        logger.info("No employees to create devices for")
        return
    
    existing_devices = list(devices_collection.find())
    
    if existing_devices:
        logger.info(f"Found {len(existing_devices)} existing devices, skipping device creation")
        return
    
    created_devices = []
    
    for employee in employees:
        # Create one device per employee
        api_key = generate_api_key()
        api_key_hash = hash_api_key(api_key)
        
        device_data = {
            "device_id": str(uuid.uuid4()),
            "employee_id": employee["employee_id"],
            "device_name": f"Laptop-{employee['display_name'].split()[0]}",
            "api_key_hash": api_key_hash,
            "active": True,
            "last_seen_at": None,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        devices_collection.insert_one(device_data)
        created_devices.append(device_data)
        
        logger.info(f"Created device for {employee['display_name']} with API key: {api_key}")
        logger.info("IMPORTANT: Save this API key as it won't be shown again!")
    
    return created_devices

def seed_stress_records(employees):
    """Create sample stress records for employees"""
    if not employees:
        logger.info("No employees to create stress records for")
        return
    
    existing_records = list(stress_records_collection.find())
    
    if existing_records:
        logger.info(f"Found {len(existing_records)} existing stress records, skipping record creation")
        return
    
    emotions = ["happy", "neutral", "sad", "angry", "fear", "disgust", "surprise"]
    stress_levels = ["Low", "Medium", "High"]
    
    # Get devices for employees
    devices = list(devices_collection.find())
    device_map = {d["employee_id"]: d["device_id"] for d in devices}
    
    now = datetime.utcnow()
    
    for employee in employees:
        employee_id = employee["employee_id"]
        device_id = device_map.get(employee_id)
        
        if not device_id:
            continue
        
        # Create records for the past 14 days
        for day in range(14):
            # Random number of records per day (1-3)
            for _ in range(random.randint(1, 3)):
                record_date = now - timedelta(days=day)
                
                # Random time during work hours
                hour = random.randint(9, 17)
                minute = random.randint(0, 59)
                record_time = record_date.replace(hour=hour, minute=minute)
                
                # Random emotion and stress level
                emotion = random.choice(emotions)
                
                # Use realistic mapping
                if emotion in ["happy", "neutral"]:
                    stress_level = "Low"
                elif emotion in ["sad", "angry", "surprise"]:
                    stress_level = "Medium"
                else:
                    stress_level = "High"
                    
                # Add occasional mismatches
                if random.random() < 0.1:  # 10% chance of mismatch
                    stress_level = random.choice([sl for sl in stress_levels if sl != stress_level])
                    mapping_mismatch = True
                else:
                    mapping_mismatch = False
                
                record_data = {
                    "record_id": str(uuid.uuid4()),
                    "employee_id": employee_id,
                    "device_id": device_id,
                    "emotion": emotion,
                    "stress_level": stress_level,
                    "confidence": random.uniform(40, 95),
                    "timestamp": record_time.isoformat() + "Z",
                    "ingested_at": datetime.utcnow().isoformat() + "Z",
                    "mapping_mismatch": mapping_mismatch,
                    "face_quality": {
                        "is_bright": True,
                        "is_proper_size": True,
                        "is_centered": True,
                        "brightness": random.uniform(40, 70),
                        "face_ratio": random.uniform(0.1, 0.3),
                        "center_distance": random.uniform(0.05, 0.2)
                    }
                }
                
                stress_records_collection.insert_one(record_data)
        
        logger.info(f"Created stress records for employee: {employee['display_name']}")

# Run the seeding process
if __name__ == "__main__":
    logger.info("Starting database seeding...")
    
    seed_manager()
    employees = seed_employees()
    seed_devices(employees)
    seed_stress_records(employees)
    
    logger.info("Database seeding completed successfully!")
    logger.info("\nDefault accounts created:")
    logger.info("- Manager: username=admin, password=adminpassword")
    logger.info("- Employees: username=<first part of email>, password=password123")
    logger.info("\nIMPORTANT: For production, change these default passwords!")
