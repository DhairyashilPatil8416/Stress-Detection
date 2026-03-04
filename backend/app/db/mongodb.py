from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    
    # Collections
    users_collection = db["users"]
    employees_collection = db["employees"]
    devices_collection = db["devices"]
    stress_records_collection = db["stress_records"]
    stress_readings_collection = db["stress_readings"]
    commands_collection = db["commands"]
    journal_collection = db["journal_entries"]
    
    # Create indexes
    users_collection.create_index("username", unique=True)
    users_collection.create_index("role")
    
    employees_collection.create_index("employee_id", unique=True)
    employees_collection.create_index("department")
    
    devices_collection.create_index("device_id", unique=True)
    devices_collection.create_index("device_number", unique=True)
    devices_collection.create_index("employee_id")
    devices_collection.create_index("active")
    
    stress_records_collection.create_index([("employee_id", 1), ("timestamp", 1)])
    stress_records_collection.create_index("timestamp")
    
    stress_readings_collection.create_index([("employee_id", 1), ("timestamp", 1)])
    stress_readings_collection.create_index("device_id")
    stress_readings_collection.create_index("timestamp")
    
    commands_collection.create_index("device_id")
    commands_collection.create_index("status")
    
    logger.info("Connected to MongoDB and created indexes successfully")
    
    # Test connection
    client.admin.command('ping')
    logger.info("MongoDB connection established and verified")
    
except ConnectionFailure:
    logger.error("MongoDB server not available")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
