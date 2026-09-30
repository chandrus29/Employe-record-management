from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, strip_whitespace=True)
    email: EmailStr
    department: str = Field(min_length=1, strip_whitespace=True)
    primary_skill: str = Field(min_length=1, strip_whitespace=True)
    location: str = Field(min_length=1, strip_whitespace=True)
    work_mode: Literal["WFH", "WFO"]


class EmployeeUpdate(EmployeeCreate):
    is_active: bool = True


class Employee(EmployeeUpdate):
    id: int = Field(gt=0)
    created_at: datetime
    
class EmployeeListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[Employee]      