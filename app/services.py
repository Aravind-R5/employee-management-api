from typing import Dict, Any, Optional
from sqlalchemy import func, case
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models import Employee, WorkItem
from app.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    WorkItemCreate,
    WorkItemUpdate,
    WorkItemStatusUpdate
)

# EMPLOYEE SERVICES

# Raises 400 if another employee already has this email (case-insensitive)
def check_duplicate_email(db: Session, email: str, exclude_id: Optional[int] = None) -> None:
    query = db.query(Employee).filter(func.lower(Employee.email) == email.lower())
    if exclude_id is not None:
        query = query.filter(Employee.id != exclude_id)
    
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with email '{email}' already exists."
        )

# Saves a new employee after checking the email is unique
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

# Lists employees with optional search and filters, paginated in SQL
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

    # Partial, case-insensitive name search
    if search:
        search_cleaned = search.strip()
        if search_cleaned:
            query = query.filter(Employee.name.ilike(f"%{search_cleaned}%"))

    # Exact department match, ignoring case
    if department:
        dept_cleaned = department.strip()
        if dept_cleaned:
            query = query.filter(func.lower(Employee.department) == dept_cleaned.lower())

    if work_mode:
        query = query.filter(Employee.work_mode == work_mode)

    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)

    # Total is counted before limit/offset are applied
    total_count = query.count()
    records = query.order_by(Employee.id.asc()).offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "items": records
    }

# Returns one employee, or 404 if not found
def get_employee_by_id(db: Session, emp_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == emp_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {emp_id} not found."
        )
    return employee

# Updates an employee; the email must stay unique across other employees
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

# Deletes an employee (their work items are deleted with them)
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

# TASK 5: WORK SUMMARY SERVICE

def get_employee_work_summary(db: Session, employee_id: int) -> Dict[str, int]:
    # 1. Employee must exist; returns 404 if not found
    get_employee_by_id(db, employee_id)

    # 2. Aggregation query using SQL CASE logic
    # coalesce makes the counts 0 when the employee has no work items
    summary = db.query(
        func.count(WorkItem.id).label("total_work_items"),
        func.coalesce(func.sum(case((WorkItem.status == "TODO", 1), else_=0)), 0).label("todo"),
        func.coalesce(func.sum(case((WorkItem.status == "IN_PROGRESS", 1), else_=0)), 0).label("in_progress"),
        func.coalesce(func.sum(case((WorkItem.status == "COMPLETED", 1), else_=0)), 0).label("completed")
    ).filter(WorkItem.employee_id == employee_id).one()

    return {
        "employee_id": employee_id,
        "total_work_items": int(summary.total_work_items),
        "todo": int(summary.todo),
        "in_progress": int(summary.in_progress),
        "completed": int(summary.completed)
    }

# WORK ITEM SERVICES

# Each status can only move to the one listed here
ALLOWED_TRANSITIONS = {
    "TODO": "IN_PROGRESS",
    "IN_PROGRESS": "COMPLETED"
}

# Raises 400 for skipped or backward status changes
def validate_status_transition(current_status: str, target_status: str) -> None:
    # If the target status matches the current status, allow it without changes
    if current_status == target_status:
        return

    # Check forward order: TODO -> IN_PROGRESS -> COMPLETED
    allowed_next = ALLOWED_TRANSITIONS.get(current_status)
    if target_status != allowed_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Disallowed status change from '{current_status}' to '{target_status}'. Allowed flow: TODO -> IN_PROGRESS -> COMPLETED."
        )

# Creates a work item for an existing employee; it must start as TODO
def create_work_item(db: Session, data: WorkItemCreate) -> WorkItem:
    # 1. Validate employee exists
    get_employee_by_id(db, data.employee_id)

    # 2. Status rule: New items must start with TODO
    final_status = data.status if data.status is not None else "TODO"
    if final_status in ["IN_PROGRESS", "COMPLETED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New work items must start with status 'TODO'."
        )

    new_item = WorkItem(
        title=data.title,
        description=data.description,
        employee_id=data.employee_id,
        status=final_status,
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

# Lists work items with optional search and filters, paginated in SQL
def get_work_items(
    db: Session,
    search: Optional[str] = None,
    employee_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    # joinedload fetches each work item's employee in the same query
    query = db.query(WorkItem).options(joinedload(WorkItem.assigned_employee))

    # Partial, case-insensitive title search
    if search:
        search_cleaned = search.strip()
        if search_cleaned:
            query = query.filter(WorkItem.title.ilike(f"%{search_cleaned}%"))

    if employee_id is not None:
        query = query.filter(WorkItem.employee_id == employee_id)

    if status_filter:
        query = query.filter(WorkItem.status == status_filter)

    if priority:
        query = query.filter(WorkItem.priority == priority)

    # Total is counted before limit/offset are applied
    total_count = query.count()
    records = query.order_by(WorkItem.id.asc()).offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "items": records
    }

# Returns one work item with its employee, or 404 if not found
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

# Task 5: Dedicated PATCH service
def patch_work_item_status(db: Session, work_item_id: int, data: WorkItemStatusUpdate) -> WorkItem:
    item = get_work_item_by_id(db, work_item_id)
    validate_status_transition(item.status, data.status)

    # Saves only when the status actually changes
    if item.status != data.status:
        item.status = data.status
        try:
            db.commit()
            db.refresh(item)
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating work item status."
            )

    return item

# Task 5: PUT service with status rules and preservation
def update_work_item(db: Session, work_item_id: int, data: WorkItemUpdate) -> WorkItem:
    item = get_work_item_by_id(db, work_item_id)

    # 1. Validate employee exists
    get_employee_by_id(db, data.employee_id)

    # 2. Check status change rules if status is provided in request body
    # Checked before any field is changed, so a rejected update saves nothing
    if data.status is not None:
        validate_status_transition(item.status, data.status)
        item.status = data.status

    item.title = data.title
    item.description = data.description
    item.employee_id = data.employee_id
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

# Deletes a work item, or 404 if not found
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