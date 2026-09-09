from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from app.schemas import EmployeeCreate, EmployeeUpdate

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Temporary in-memory list storage
employees_db: List[dict] = []
id_counter: int = 1

def check_duplicate_email(email: str, exclude_id: Optional[int] = None) -> None:
    for emp in employees_db:
        if emp["email"].lower() == email.lower() and emp["id"] != exclude_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with email '{email}' already exists."
            )

def create_employee(data: EmployeeCreate) -> dict:
    global id_counter
    check_duplicate_email(data.email)
    
    new_employee = {
        "id": id_counter,
        "name": data.name,
        "email": data.email,
        "department": data.department,
        "primary_skill": data.primary_skill,
        "location": data.location,
        "work_mode": data.work_mode,
        "is_active": True,
        "created_at": datetime.now(IST)
    }
    employees_db.append(new_employee)
    id_counter += 1
    return new_employee

def get_all_employees() -> List[dict]:
    return employees_db

def get_employee_by_id(emp_id: int) -> dict:
    for emp in employees_db:
        if emp["id"] == emp_id:
            return emp
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Employee with ID {emp_id} not found."
    )

def update_employee(emp_id: int, data: EmployeeUpdate) -> dict:
    emp = get_employee_by_id(emp_id)
    check_duplicate_email(data.email, exclude_id=emp_id)
    
    emp.update({
        "name": data.name,
        "email": data.email,
        "department": data.department,
        "primary_skill": data.primary_skill,
        "location": data.location,
        "work_mode": data.work_mode,
        "is_active": data.is_active
    })
    return emp

def delete_employee(emp_id: int) -> dict:
    emp = get_employee_by_id(emp_id)
    employees_db.remove(emp)
    return {"detail": f"Employee with ID {emp_id} successfully deleted."}