from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EmotionEnum(str, Enum):
    happy = "happy"
    neutral = "neutral"
    sad = "sad"
    angry = "angry"
    fear = "fear"
    disgust = "disgust"
    surprise = "surprise"

class StressLevelEnum(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"

class RoleEnum(str, Enum):
    manager = "manager"
    employee = "employee"

class CommandTypeEnum(str, Enum):
    ANALYZE_NOW = "ANALYZE_NOW"

class CommandStatusEnum(str, Enum):
    pending = "pending"
    ack = "ack"
    done = "done"
    failed = "failed"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: RoleEnum
    employee_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[RoleEnum] = None
    employee_id: Optional[str] = None

class UserBase(BaseModel):
    username: str
    role: RoleEnum
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str
    employee_id: Optional[str] = None
    department: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None

class UserInDB(UserBase):
    user_id: str
    password_hash: str
    employee_id: Optional[str] = None
    active: bool = True
    created_at: str

class User(UserBase):
    user_id: str
    employee_id: Optional[str] = None
    active: bool = True
    created_at: str

class EmployeeBase(BaseModel):
    display_name: str
    email: Optional[EmailStr] = None
    department: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    active: Optional[bool] = None

class Employee(EmployeeBase):
    employee_id: str
    active: bool = True
    created_at: str

class DeviceBase(BaseModel):
    employee_id: str
    device_name: Optional[str] = None
    device_number: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    active: Optional[bool] = None
    rotate_key: Optional[bool] = False

class Device(DeviceBase):
    device_id: str
    active: bool = True
    last_seen_at: Optional[str] = None
    created_at: str

class DeviceWithKey(Device):
    api_key: str

class FaceQuality(BaseModel):
    is_bright: bool
    is_proper_size: bool
    is_centered: bool
    brightness: float
    face_ratio: float
    center_distance: float

class StressRecordBase(BaseModel):
    employee_id: str
    device_id: str
    emotion: EmotionEnum
    stress_level: StressLevelEnum
    confidence: float = Field(..., ge=0, le=100)
    timestamp: str

class StressRecord(StressRecordBase):
    record_id: str
    ingested_at: str
    mapping_mismatch: Optional[bool] = False

class StressSubmission(BaseModel):
    device_id: str
    employee_id: str
    emotion: EmotionEnum
    stress_level: StressLevelEnum
    confidence: float = Field(..., ge=0, le=100)
    timestamp: str
    face_quality: Optional[FaceQuality] = None

class StressResponse(BaseModel):
    record_id: str

class CommandBase(BaseModel):
    device_id: str
    type: CommandTypeEnum = CommandTypeEnum.ANALYZE_NOW

class CommandCreate(CommandBase):
    pass

class CommandUpdate(BaseModel):
    status: CommandStatusEnum
    error: Optional[str] = None

class Command(CommandBase):
    command_id: str
    status: CommandStatusEnum
    created_at: str
    ack_at: Optional[str] = None
    done_at: Optional[str] = None
    error: Optional[str] = None

class LatestStressRecord(BaseModel):
    employee_id: str
    display_name: str
    latest_stress_level: StressLevelEnum
    latest_emotion: EmotionEnum
    confidence: float
    timestamp: str
    device_id: str

class AggregateStats(BaseModel):
    total_records: int
    high_stress_count: int
    medium_stress_count: int
    low_stress_count: int
    high_stress_percentage: float
    medium_stress_percentage: float
    low_stress_percentage: float

class TimeseriesPoint(BaseModel):
    timestamp: str
    value: float

class DepartmentStats(BaseModel):
    department: str
    high_stress_percentage: float
    medium_stress_percentage: float
    low_stress_percentage: float

class StressAggregateResponse(BaseModel):
    overall: AggregateStats
    timeseries: List[TimeseriesPoint]
    departments: Optional[List[DepartmentStats]] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class JournalEntry(BaseModel):
    mood: str
    note: str
    stressLevel: str
    timestamp: str
    
class ImageData(BaseModel):
    image: str  # base64 encoded image
    timestamp: str
