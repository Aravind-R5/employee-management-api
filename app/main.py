from typing import List
from fastapi import FastAPI, Path, Depends, status
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app import services

# Automatically create tables in MySQL if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee Management API",
    description="Employee record management with FastAPI, SQLAlchemy, and MySQL",
    version="2.0.0"
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

@app.get(
    "/employees",
    response_model=List[EmployeeResponse],
    tags=["Employees"]
)
def list_employees(db: Session = Depends(get_db)):
    return services.get_all_employees(db)

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