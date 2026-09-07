from typing import List
from fastapi import FastAPI, Path, status
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app import services

app = FastAPI(
    title="Employee Management API",
    description="In-memory employee record management built with FastAPI",
    version="1.0.0"
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
def create_employee(employee: EmployeeCreate):
    return services.create_employee(employee)

@app.get(
    "/employees",
    response_model=List[EmployeeResponse],
    tags=["Employees"]
)
def list_employees():
    return services.get_all_employees()

@app.get(
    "/employees/{id}",
    response_model=EmployeeResponse,
    tags=["Employees"]
)
def get_employee(
    id: int = Path(..., gt=0, description="Employee ID must be greater than 0")
):
    return services.get_employee_by_id(id)

@app.put(
    "/employees/{id}",
    response_model=EmployeeResponse,
    tags=["Employees"]
)
def update_employee(
    employee: EmployeeUpdate,
    id: int = Path(..., gt=0, description="Employee ID must be greater than 0")
):
    return services.update_employee(id, employee)

@app.delete(
    "/employees/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Employees"]
)
def delete_employee(
    id: int = Path(..., gt=0, description="Employee ID must be greater than 0")
):
    return services.delete_employee(id)