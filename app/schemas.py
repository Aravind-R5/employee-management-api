from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field

class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, description="Full name of the employee")
    email: EmailStr = Field(..., description="Valid corporate email address")
    department: str = Field(..., min_length=1, description="Department name")
    primary_skill: str = Field(..., min_length=1, description="Primary technical skill")
    location: str = Field(..., min_length=1, description="Current working location")
    work_mode: Literal["WFH", "WFO"] = Field(..., description="Accepted values: WFH or WFO")

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