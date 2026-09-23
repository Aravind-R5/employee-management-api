from typing import Optional, Literal
from fastapi import FastAPI, Path, Query, Depends, status
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.schemas import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    PaginatedEmployeeResponse
)
from app import services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee Management API",
    description="Employee record management with FastAPI, SQLAlchemy, and MySQL",
    version="3.0.0"
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Application is healthy and running"}

@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Employees"]
)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return services.create_employee(db, employee)

# --- UPDATED FOR TASK 3 ---
@app.get(
    "/employees",
    response_model=PaginatedEmployeeResponse,
    tags=["Employees"]
)
def list_employees(
    search: Optional[str] = Query(None, description="Search employee by name (partial & case-insensitive)"),
    department: Optional[str] = Query(None, description="Filter by department name"),
    work_mode: Optional[Literal["WFH", "WFO"]] = Query(None, description="Filter by work mode ('WFH' or 'WFO')"),
    is_active: Optional[bool] = Query(None, description="Filter by active status (true or false)"),
    limit: int = Query(10, ge=1, le=100, description="Page size (1 to 100, default 10)"),
    offset: int = Query(0, ge=0, description="Records to skip (minimum 0, default 0)"),
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