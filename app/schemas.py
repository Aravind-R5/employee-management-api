from datetime import datetime, date
from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

# EMPLOYEE SCHEMAS

# Fields shared by every employee request and response
class EmployeeBase(BaseModel):
    name: str = Field(..., description="Full name of the employee")
    email: EmailStr = Field(..., description="Valid corporate email address")
    department: str = Field(..., description="Department name")
    primary_skill: str = Field(..., description="Primary technical skill")
    location: str = Field(..., description="Current working location")
    work_mode: Literal["WFH", "WFO"] = Field(..., description="Accepted values: WFH or WFO")

    # Trims spaces and rejects blank or whitespace-only values
    @field_validator("name", "department", "primary_skill", "location")
    @classmethod
    def reject_empty_or_whitespace(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return trimmed

# Request body for POST /employees
class EmployeeCreate(EmployeeBase):
    pass

# Request body for PUT /employees/{id}
class EmployeeUpdate(EmployeeBase):
    is_active: bool = Field(default=True, description="Active status")

# Employee returned by the API, including generated fields
class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime

    # Lets Pydantic read values straight from the database model
    class Config:
        from_attributes = True

# Response for GET /employees: one page of employees plus paging details
class PaginatedEmployeeResponse(BaseModel):
    total: int = Field(..., description="Number of matching employees before pagination")
    limit: int = Field(..., description="Requested page size")
    offset: int = Field(..., description="Requested number of records to skip")
    items: List[EmployeeResponse] = Field(..., description="List of employee records")

# TASK 5: EMPLOYEE SUMMARY SCHEMA

# Response for GET /employees/{id}/work-summary: work item counts by status
class WorkSummaryResponse(BaseModel):
    employee_id: int
    total_work_items: int
    todo: int
    in_progress: int
    completed: int

# WORK ITEM SCHEMAS

# Short employee details shown inside each work item response
class EmployeeBasic(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

# Fields shared by work item create and update requests
class WorkItemBase(BaseModel):
    title: str = Field(..., max_length=200, description="Title of the work item")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description")
    employee_id: int = Field(..., gt=0, description="ID of assigned employee (must be > 0)")
    priority: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        default="MEDIUM",
        description="Allowed: LOW, MEDIUM, HIGH"
    )
    due_date: Optional[date] = Field(None, description="Optional due date (YYYY-MM-DD)")

    # Trims spaces and rejects a blank or whitespace-only title
    @field_validator("title")
    @classmethod
    def reject_empty_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Title cannot be empty or contain only whitespace.")
        return trimmed

# Request body for POST /work-items
class WorkItemCreate(WorkItemBase):
    # Status is optional during creation and defaults to "TODO"
    status: Optional[Literal["TODO", "IN_PROGRESS", "COMPLETED"]] = Field(
        default="TODO",
        description="Defaults to TODO. New work items must start as TODO."
    )

# Request body for PUT /work-items/{id}
class WorkItemUpdate(WorkItemBase):
    # Optional so that omitting status preserves the current status in DB
    status: Optional[Literal["TODO", "IN_PROGRESS", "COMPLETED"]] = Field(
        default=None,
        description="New status if changing, or omit/null to keep existing status"
    )

# Request body for PATCH /work-items/{id}/status
class WorkItemStatusUpdate(BaseModel):
    # Required for PATCH /work-items/{id}/status. Non-null and valid literal
    status: Literal["TODO", "IN_PROGRESS", "COMPLETED"] = Field(
        ...,
        description="Status must be one of: TODO, IN_PROGRESS, COMPLETED"
    )

# Work item returned by the API, with its assigned employee
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

# Response for GET /work-items: one page of work items plus paging details
class PaginatedWorkItemResponse(BaseModel):
    total: int = Field(..., description="Number of matching work items before pagination")
    limit: int = Field(..., description="Requested page size")
    offset: int = Field(..., description="Requested number of records to skip")
    items: List[WorkItemResponse] = Field(..., description="List of work items")