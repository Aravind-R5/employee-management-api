from datetime import datetime, date
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

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
    # Non-optional literal: omitting status sets default to "TODO".
    # Sending status: null fails literal validation and returns 422.
    status: Literal["TODO", "IN_PROGRESS", "COMPLETED"] = Field(
        default="TODO",
        description="Defaults to TODO. Passing null returns 422."
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

    class Config:
        from_attributes = True

class PaginatedWorkItemResponse(BaseModel):
    total: int = Field(..., description="Number of matching work items before pagination")
    limit: int = Field(..., description="Requested page size")
    offset: int = Field(..., description="Requested number of records to skip")
    items: List[WorkItemResponse] = Field(..., description="List of work items")