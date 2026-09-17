from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeUpdate

def check_duplicate_email(db: Session, email: str, exclude_id: Optional[int] = None) -> None:
    query = db.query(Employee).filter(func.lower(Employee.email) == email.lower())
    if exclude_id is not None:
        query = query.filter(Employee.id != exclude_id)
    
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with email '{email}' already exists."
        )

def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    check_duplicate_email(db, data.email)
    
    new_employee = Employee(
        name=data.name,
        email=data.email,
        department=data.department,
        primary_skill=data.primary_skill,
        location=data.location,
        work_mode=data.work_mode,
        is_active=True
    )
    try:
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        return new_employee
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with email '{data.email}' already exists."
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving to the database."
        )

def get_all_employees(db: Session) -> List[Employee]:
    return db.query(Employee).all()

def get_employee_by_id(db: Session, emp_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == emp_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {emp_id} not found."
        )
    return employee

def update_employee(db: Session, emp_id: int, data: EmployeeUpdate) -> Employee:
    employee = get_employee_by_id(db, emp_id)
    check_duplicate_email(db, data.email, exclude_id=emp_id)
    
    employee.name = data.name
    employee.email = data.email
    employee.department = data.department
    employee.primary_skill = data.primary_skill
    employee.location = data.location
    employee.work_mode = data.work_mode
    employee.is_active = data.is_active
    
    try:
        db.commit()
        db.refresh(employee)
        return employee
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with email '{data.email}' already exists."
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the database."
        )

def delete_employee(db: Session, emp_id: int) -> dict:
    employee = get_employee_by_id(db, emp_id)
    try:
        db.delete(employee)
        db.commit()
        return {"detail": f"Employee with ID {emp_id} successfully deleted."}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting from the database."
        )