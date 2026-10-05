from typing import Optional, Literal
from fastapi import FastAPI, Path, Query, Depends, status
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.schemas import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    PaginatedEmployeeResponse,
    WorkItemCreate,
    WorkItemResponse,
    WorkItemUpdate,
    PaginatedWorkItemResponse
)
from app import services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee & Work Item Management API",
    description="Employee and Work Item management with FastAPI, SQLAlchemy, and MySQL",
    version="4.0.0"
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Application is healthy and running"}

# EMPLOYEE ENDPOINTS

@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Employees"]
)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return services.create_employee(db, employee)

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


# WORK ITEM ENDPOINTS (TASK 4)

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