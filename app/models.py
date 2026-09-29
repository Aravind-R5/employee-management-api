from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base

IST = timezone(timedelta(hours=5, minutes=30))

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    primary_skill = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    work_mode = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(IST), nullable=False)

    # Relationship to WorkItem
    work_items = relationship("WorkItem", back_populates="assigned_employee", cascade="all, delete-orphan")


class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(
        SQLEnum("TODO", "IN_PROGRESS", "COMPLETED", name="work_item_status"),
        default="TODO",
        nullable=False
    )
    priority = Column(
        SQLEnum("LOW", "MEDIUM", "HIGH", name="work_item_priority"),
        default="MEDIUM",
        nullable=False
    )
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST), nullable=False)

    # Relationship back to Employee
    assigned_employee = relationship("Employee", back_populates="work_items")