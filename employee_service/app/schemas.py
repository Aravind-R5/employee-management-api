from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class EmployeeBase(BaseModel):
    name: str = Field(..., max_length=100, description="Full name of the employee")
    email: EmailStr = Field(..., max_length=150, description="Valid corporate email address")
    department: str = Field(..., max_length=100, description="Department name")
    primary_skill: str = Field(..., max_length=100, description="Primary technical skill")
    location: str = Field(..., max_length=100, description="Current working location")
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

class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedEmployeeResponse(BaseModel):
    total: int = Field(..., description="Number of matching employees before pagination")
    limit: int = Field(..., description="Requested page size")
    offset: int = Field(..., description="Requested number of records to skip")
    items: List[EmployeeResponse] = Field(..., description="List of employee records")