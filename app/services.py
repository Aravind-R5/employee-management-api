from typing import Dict, Any, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models import Employee, WorkItem
from app.schemas import EmployeeCreate, EmployeeUpdate, WorkItemCreate, WorkItemUpdate

# EMPLOYEE SERVICES

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

def get_employees(
    db: Session,
    search: Optional[str] = None,
    department: Optional[str] = None,
    work_mode: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    query = db.query(Employee)

    if search:
        search_cleaned = search.strip()
        if search_cleaned:
            query = query.filter(Employee.name.ilike(f"%{search_cleaned}%"))

    if department:
        dept_cleaned = department.strip()
        if dept_cleaned:
            query = query.filter(func.lower(Employee.department) == dept_cleaned.lower())

    if work_mode:
        query = query.filter(Employee.work_mode == work_mode)

    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)

    total_count = query.count()
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



# WORK ITEM SERVICES (TASK 4)

def create_work_item(db: Session, data: WorkItemCreate) -> WorkItem:
    # 1. Validate assigned employee exists; return 404 if missing
    get_employee_by_id(db, data.employee_id)

    new_item = WorkItem(
        title=data.title,
        description=data.description,
        employee_id=data.employee_id,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date
    )
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the work item."
        )

def get_work_items(
    db: Session,
    search: Optional[str] = None,
    employee_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    # Use joinedload to efficiently load assigned_employee in the same SQL query
    query = db.query(WorkItem).options(joinedload(WorkItem.assigned_employee))

    # Partial, case-insensitive title search
    if search:
        search_cleaned = search.strip()
        if search_cleaned:
            query = query.filter(WorkItem.title.ilike(f"%{search_cleaned}%"))

    # Filter by employee
    if employee_id is not None:
        query = query.filter(WorkItem.employee_id == employee_id)

    # Filter by status
    if status_filter:
        query = query.filter(WorkItem.status == status_filter)

    # Filter by priority
    if priority:
        query = query.filter(WorkItem.priority == priority)

    total_count = query.count()
    records = query.order_by(WorkItem.id.asc()).offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "items": records
    }

def get_work_item_by_id(db: Session, work_item_id: int) -> WorkItem:
    item = (
        db.query(WorkItem)
        .options(joinedload(WorkItem.assigned_employee))
        .filter(WorkItem.id == work_item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item with ID {work_item_id} not found."
        )
    return item

def update_work_item(db: Session, work_item_id: int, data: WorkItemUpdate) -> WorkItem:
    item = get_work_item_by_id(db, work_item_id)

    # If reassigning or checking employee existence
    get_employee_by_id(db, data.employee_id)

    item.title = data.title
    item.description = data.description
    item.employee_id = data.employee_id
    item.status = data.status
    item.priority = data.priority
    item.due_date = data.due_date

    try:
        db.commit()
        db.refresh(item)
        return item
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the work item."
        )

def delete_work_item(db: Session, work_item_id: int) -> None:
    item = get_work_item_by_id(db, work_item_id)
    try:
        db.delete(item)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the work item."
        )