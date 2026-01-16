from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List, Any, Dict


class PersonSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    skills: Optional[List[str]] = None


class GenericSchema(BaseModel):
    """Generic schema for any data type"""
    data: Dict[str, Any]