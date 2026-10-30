from typing import Optional, Literal
from fastapi import FastAPI, Path, Query, Depends, status
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.schemas import (
    WorkItemCreate,
    WorkItemResponse,
    PaginatedWorkItemResponse
)
from app import services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Work Item Service",
    description="Dedicated microservice for managing work items on port 8002",
    version="1.0.0"
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Work Item Service", "port": 8002}

@app.post(
    "/work-items",
    response_model=WorkItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Work Items"]
)
def create_work_item(item: WorkItemCreate, db: Session = Depends(get_db)):
    return services.create_work_item(db, item)

@app.get(
    "/work-items",
    response_model=PaginatedWorkItemResponse,
    tags=["Work Items"]
)
def list_work_items(
    search: Optional[str] = Query(None, description="Search work item by title"),
    employee_id: Optional[int] = Query(None, gt=0, description="Filter by assigned employee ID"),
    status: Optional[Literal["TODO", "IN_PROGRESS", "COMPLETED"]] = Query(None, description="Filter by status"),
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = Query(None, description="Filter by priority"),
    limit: int = Query(10, ge=1, le=100, description="Page size (1 to 100)"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: Session = Depends(get_db)
):
    return services.get_work_items(
        db=db,
        search=search,
        employee_id=employee_id,
        status_filter=status,
        priority=priority,
        limit=limit,
        offset=offset
    )

@app.get(
    "/work-items/{work_item_id}",
    response_model=WorkItemResponse,
    tags=["Work Items"]
)
def get_work_item(
    work_item_id: int = Path(..., gt=0, description="Work item ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    return services.get_work_item_by_id(db, work_item_id)