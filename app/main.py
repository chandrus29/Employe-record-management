from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, services
from app.database import Base, engine, get_db
from app.schemas import (
    Employee,
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeUpdate,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Management API")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/employees",
    response_model=Employee,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    if services.email_exists(db, email):
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    data = payload.model_dump()
    data["email"] = email

    try:
        return services.create_employee(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )


@app.get("/employees", response_model=EmployeeListResponse)
def list_employees(
    search: str | None = None,
    department: str | None = None,
    work_mode: Literal["WFH", "WFO"] | None = None,
    is_active: bool | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return services.list_employees(
        db=db,
        search=search,
        department=department,
        work_mode=work_mode,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    if employee_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID must be greater than zero",
        )

    employee = services.find_employee(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    return employee


@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    if employee_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID must be greater than zero",
        )

    employee = services.find_employee(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    email = str(payload.email).strip().lower()

    if services.email_exists(db, email, exclude_id=employee_id):
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    data = payload.model_dump()
    data["email"] = email

    try:
        return services.update_employee(db, employee, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )


@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    if employee_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID must be greater than zero",
        )

    employee = services.find_employee(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    services.delete_employee(db, employee)
    return {"message": "Employee deleted successfully"}