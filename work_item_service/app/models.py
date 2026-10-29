from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Date, Enum as SQLEnum
from app.database import Base

IST = timezone(timedelta(hours=5, minutes=30))

class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    # Stored as a plain Integer (no ForeignKey, no ORM relationship)
    employee_id = Column(Integer, nullable=False, index=True)
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