from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime
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