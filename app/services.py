from typing import Dict, Any, Optional
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

# --- REPLACED & EXTENDED FOR TASK 3 ---
def get_employees(
    db: Session,
    search: Optional[str] = None,
    department: Optional[str] = None,
    work_mode: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    # 1. Base query
    query = db.query(Employee)

    # 2. Case-insensitive partial name search (LIKE %search%)
    if search:
        search_cleaned = search.strip()
        if search_cleaned:
            query = query.filter(Employee.name.ilike(f"%{search_cleaned}%"))

    # 3. Exact department filter (case-insensitive comparison)
    if department:
        dept_cleaned = department.strip()
        if dept_cleaned:
            query = query.filter(func.lower(Employee.department) == dept_cleaned.lower())

    # 4. Work mode filter
    if work_mode:
        query = query.filter(Employee.work_mode == work_mode)

    # 5. Active status filter
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)

    # 6. Get total count of matching records before applying pagination
    total_count = query.count()

    # 7. Apply ascending ID ordering and pagination at SQL level
    records = query.order_by(Employee.id.asc()).offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "items": records
    }

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