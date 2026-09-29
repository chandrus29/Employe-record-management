from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    department: str = Field(min_length=1)
    primary_skill: str = Field(min_length=1)
    location: str = Field(min_length=1)
    work_mode: Literal["WFH", "WFO"]


class EmployeeUpdate(EmployeeCreate):
    is_active: bool = True


class Employee(EmployeeUpdate):
    id: int = Field(gt=0)
    created_at: datetime