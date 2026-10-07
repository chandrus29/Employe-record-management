from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, strip_whitespace=True)
    email: EmailStr
    department: str = Field(min_length=1, strip_whitespace=True)
    primary_skill: str = Field(min_length=1, strip_whitespace=True)
    location: str = Field(min_length=1, strip_whitespace=True)
    work_mode: Literal["WFH", "WFO"]

    @field_validator("name", "department", "primary_skill", "location")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


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


class AssignedEmployeeResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class WorkItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    employee_id: int = Field(gt=0)
    status: Literal["TODO", "IN_PROGRESS", "COMPLETED"] = "TODO"
    priority: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title must not be blank")
        return value.strip()


class WorkItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    employee_id: int | None = Field(default=None, gt=0)
    status: Literal["TODO", "IN_PROGRESS", "COMPLETED"] | None = None
    priority: Literal["LOW", "MEDIUM", "HIGH"] | None = None
    due_date: date | None = None

    @field_validator(
        "title",
        "employee_id",
        "status",
        "priority",
        mode="before",
    )
    @classmethod
    def reject_null_for_required_fields(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Title must not be blank")
        return value.strip() if value is not None else value


class WorkItemResponse(BaseModel):
    id: int
    title: str
    description: str | None
    employee_id: int
    status: str
    priority: str
    due_date: date | None
    created_at: datetime
    assigned_employee: AssignedEmployeeResponse

    model_config = {"from_attributes": True}


class WorkItemListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[WorkItemResponse]