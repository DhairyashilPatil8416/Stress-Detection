from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from app.schemas.schemas import JournalEntry, User
from app.db.mongodb import journal_collection
from app.core.security.deps import get_current_employee, get_current_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[JournalEntry])
async def get_journal_entries(
    current_user: User = Depends(get_current_employee)
) -> Any:
    """
    Get all journal entries for the current employee
    """
    employee_id = current_user.get("employee_id")
    if not employee_id:
        raise HTTPException(status_code=404, detail="No employee profile associated with this user")
    
    try:
        entries = list(journal_collection.find({"employee_id": employee_id}, {'_id': 0}))
        return entries
    except Exception as e:
        logger.error(f"Error loading journal entries from DB: {str(e)}")
        return []

@router.post("/", response_model=JournalEntry)
async def create_journal_entry(
    entry: JournalEntry,
    current_user: User = Depends(get_current_employee)
) -> Any:
    """
    Create a new journal entry for the current employee
    """
    employee_id = current_user.get("employee_id")
    if not employee_id:
        raise HTTPException(status_code=404, detail="No employee profile associated with this user")
    
    entry_data = entry.dict()
    entry_data["employee_id"] = employee_id
    
    try:
        journal_collection.insert_one(entry_data)
        return entry_data
    except Exception as e:
        logger.error(f"Error saving journal entry to DB: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving journal entry"
        )
