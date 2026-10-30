from typing import Optional, Literal
from fastapi import FastAPI, Path, Query, Depends, status
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.schemas import (
    EmployeeCreate,
    EmployeeResponse,
    PaginatedEmployeeResponse
)
from app import services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee Service",
    description="Dedicated microservice for managing employee records on port 8001",
    version="1.0.0"
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Employee Service", "port": 8001}

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
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
    tags=["Employees"]
)
def get_employee(
    employee_id: int = Path(..., gt=0, description="Employee ID must be greater than 0"),
    db: Session = Depends(get_db)
):
    return services.get_employee_by_id(db, employee_id)