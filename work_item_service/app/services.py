import os
from typing import Dict, Any, Optional
import httpx 
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import WorkItem
from app.schemas import WorkItemCreate

EMPLOYEE_SERVICE_URL = os.getenv("EMPLOYEE_SERVICE_URL", "http://localhost:8001").rstrip("/")

def verify_employee_exists(employee_id: int) -> None:
    """
    Validates employee existence via HTTP GET against Employee Service.
    Configured with a strict 5.0s timeout.
    """
    url = f"{EMPLOYEE_SERVICE_URL}/employees/{employee_id}"
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)

        if response.status_code == 200:
            return
        elif response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Employee Service returned an unexpected error."
            )
    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Employee Service is unavailable or timed out."
        )

def create_work_item(db: Session, data: WorkItemCreate) -> WorkItem:
    # 1. Verify employee existence via inter-service HTTP call
    verify_employee_exists(data.employee_id)

    # 2. Rule: New work items must start with TODO
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

def get_work_items(
    db: Session,
    search: Optional[str] = None,
    employee_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    # Pure query on WorkItem table: does not call Employee Service
    query = db.query(WorkItem)

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

    total_count = query.count()
    records = query.order_by(WorkItem.id.asc()).offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "items": records
    }

def get_work_item_by_id(db: Session, work_item_id: int) -> WorkItem:
    item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item with ID {work_item_id} not found."
        )
    return item