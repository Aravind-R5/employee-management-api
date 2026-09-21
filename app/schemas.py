from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator

class EmployeeBase(BaseModel):
    name: str = Field(..., description="Full name of the employee")
    email: EmailStr = Field(..., description="Valid corporate email address")
    department: str = Field(..., description="Department name")
    primary_skill: str = Field(..., description="Primary technical skill")
    location: str = Field(..., description="Current working location")
    work_mode: Literal["WFH", "WFO"] = Field(..., description="Accepted values: WFH or WFO")

    @field_validator("name", "department", "primary_skill", "location")
    @classmethod
    def reject_empty_or_whitespace(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return trimmed

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    is_active: bool = Field(default=True, description="Active status")

class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        
# --- EXTENDED FOR TASK 3 ---
class PaginatedEmployeeResponse(BaseModel):
    total: int = Field(..., description="Number of matching employees before pagination")
    limit: int = Field(..., description="Requested page size")
    offset: int = Field(..., description="Requested number of records to skip")
    items: List[EmployeeResponse] = Field(..., description="List of employee records")