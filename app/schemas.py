from datetime import datetime, date
from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

# --- EMPLOYEE SCHEMAS ---

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

class PaginatedEmployeeResponse(BaseModel):
    total: int = Field(..., description="Number of matching employees before pagination")
    limit: int = Field(..., description="Requested page size")
    offset: int = Field(..., description="Requested number of records to skip")
    items: List[EmployeeResponse] = Field(..., description="List of employee records")

# --- EMPLOYEE SUMMARY SCHEMA (TASK 5) ---

class WorkSummaryResponse(BaseModel):
    employee_id: int
    total_work_items: int
    todo: int
    in_progress: int
    completed: int


# --- WORK ITEM SCHEMAS ---

class EmployeeBasic(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class WorkItemBase(BaseModel):
    title: str = Field(..., max_length=200, description="Title of the work item")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description")
    employee_id: int = Field(..., gt=0, description="ID of assigned employee (must be > 0)")
    priority: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        default="MEDIUM",
        description="Allowed: LOW, MEDIUM, HIGH"
    )
    due_date: Optional[date] = Field(None, description="Optional due date (YYYY-MM-DD)")

    @field_validator("title")
    @classmethod
    def reject_empty_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Title cannot be empty or contain only whitespace.")
        return trimmed

class WorkItemCreate(WorkItemBase):
    # Status is optional during creation and defaults to "TODO"
    status: Optional[Literal["TODO", "IN_PROGRESS", "COMPLETED"]] = Field(
        default="TODO",
        description="Defaults to TODO. New work items must start as TODO."
    )

class WorkItemUpdate(WorkItemBase):
    # Optional so that omitting status preserves the current status in DB
    status: Optional[Literal["TODO", "IN_PROGRESS", "COMPLETED"]] = Field(
        default=None,
        description="New status if changing, or omit/null to keep existing status"
    )

class WorkItemStatusUpdate(BaseModel):
    # Required for PATCH /work-items/{id}/status. Non-null and valid literal
    status: Literal["TODO", "IN_PROGRESS", "COMPLETED"] = Field(
        ...,
        description="Status must be one of: TODO, IN_PROGRESS, COMPLETED"
    )

class WorkItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    employee_id: int
    status: Literal["TODO", "IN_PROGRESS", "COMPLETED"]
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    due_date: Optional[date] = None
    created_at: datetime
    assigned_employee: EmployeeBasic

    class Config:
        from_attributes = True

class PaginatedWorkItemResponse(BaseModel):
    total: int = Field(..., description="Number of matching work items before pagination")
    limit: int = Field(..., description="Requested page size")
    offset: int = Field(..., description="Requested number of records to skip")
    items: List[WorkItemResponse] = Field(..., description="List of work items")