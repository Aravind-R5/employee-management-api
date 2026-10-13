from typing import Optional, Literal
from fastapi import FastAPI, Path, Query, Depends, status
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.schemas import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    PaginatedEmployeeResponse,
    WorkSummaryResponse,
    WorkItemCreate,
    WorkItemResponse,
    WorkItemUpdate,
    WorkItemStatusUpdate,
    PaginatedWorkItemResponse
)
from app import services

# Creates tables in MySQL if they do not exist
Base.metadata.create_all(bind=engine)

# FastAPI application configuration
app = FastAPI(
    title="Employee & Work Item Management API",
    description="Employee and Work Item management with state machine transitions and summary reports",
    version="5.0.0"
)

# Health check route to verify server status
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Application is healthy and running"}

# EMPLOYEE ENDPOINTS

# Creates a new employee with unique email validation
@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Employees"]
)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return services.create_employee(db, employee)

# Lists employees with optional search and filters, paginated
@app.get(
    "/employees",
    response_model=PaginatedEmployeeResponse,
    tags=["Employees"]
)
def list_employees(
    search: Optional[str] = Query(None, description="Search employee by name"),
    department: Optional[str] = Query(None, description="Filter by department"),
    work_mode: Optional[Literal["WFH", "WFO"]] = Query(None, description="Filter by work mode"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(10, ge=1, le=100, description="Page size (1-100)"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: Session = Depends(get_db)
):
    return services.get_employees(
        db=db,
        search=search,
        department=department,
        work_mode=work_mode,
        is_active=is_active,
        limit=limit,
        offset=offset
    )

# Returns one employee by ID, or 404 if not found
@app.get(
    "/employees/{id}",
    response_model=EmployeeResponse,
    tags=["Employees"]
)
def get_employee(
    id: int = Path(..., gt=0, description="Employee ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    return services.get_employee_by_id(db, id)

# Updates an existing employee after unique email check
@app.put(
    "/employees/{id}",
    response_model=EmployeeResponse,
    tags=["Employees"]
)
def update_employee(
    employee: EmployeeUpdate,
    id: int = Path(..., gt=0, description="Employee ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    return services.update_employee(db, id, employee)

# Deletes an employee and cascades deletion to their work items
@app.delete(
    "/employees/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Employees"]
)
def delete_employee(
    id: int = Path(..., gt=0, description="Employee ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    return services.delete_employee(db, id)

# TASK 5: WORK SUMMARY ROUTE

# Returns work item counts grouped by status for a given employee
@app.get(
    "/employees/{employee_id}/work-summary",
    response_model=WorkSummaryResponse,
    tags=["Employees"]
)
def get_employee_work_summary(
    employee_id: int = Path(..., gt=0, description="Employee ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    return services.get_employee_work_summary(db, employee_id)

# WORK ITEM ENDPOINTS

# Creates a work item; status must default to or start with TODO
@app.post(
    "/work-items",
    response_model=WorkItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Work Items"]
)
def create_work_item(item: WorkItemCreate, db: Session = Depends(get_db)):
    return services.create_work_item(db, item)

# Lists work items with optional search and filters, paginated
@app.get(
    "/work-items",
    response_model=PaginatedWorkItemResponse,
    tags=["Work Items"]
)
def list_work_items(
    search: Optional[str] = Query(None, description="Search work item by title (partial & case-insensitive)"),
    employee_id: Optional[int] = Query(None, gt=0, description="Filter by assigned employee ID"),
    status: Optional[Literal["TODO", "IN_PROGRESS", "COMPLETED"]] = Query(None, description="Filter by status"),
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = Query(None, description="Filter by priority"),
    limit: int = Query(10, ge=1, le=100, description="Page size (1 to 100, default 10)"),
    offset: int = Query(0, ge=0, description="Records to skip (minimum 0, default 0)"),
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

# Returns one work item by ID with assigned employee details
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

# TASK 5: STATUS PATCH ROUTE

# Updates only work item status following TODO -> IN_PROGRESS -> COMPLETED order
@app.patch(
    "/work-items/{work_item_id}/status",
    response_model=WorkItemResponse,
    tags=["Work Items"]
)
def patch_work_item_status(
    data: WorkItemStatusUpdate,
    work_item_id: int = Path(..., gt=0, description="Work item ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    return services.patch_work_item_status(db, work_item_id, data)

# Updates a work item; validates status transitions or preserves current status if omitted
@app.put(
    "/work-items/{work_item_id}",
    response_model=WorkItemResponse,
    tags=["Work Items"]
)
def update_work_item(
    item: WorkItemUpdate,
    work_item_id: int = Path(..., gt=0, description="Work item ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    return services.update_work_item(db, work_item_id, item)

# Deletes a work item by ID, returning 204 No Content
@app.delete(
    "/work-items/{work_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Work Items"]
)
def delete_work_item(
    work_item_id: int = Path(..., gt=0, description="Work item ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    services.delete_work_item(db, work_item_id)
    return None