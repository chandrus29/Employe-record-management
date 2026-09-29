from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import services
from app.database import Base, engine, get_db
from app import models
from app.schemas import Employee, EmployeeCreate, EmployeeUpdate

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
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()

    if services.email_exists(db, email):
        raise HTTPException(status_code=409, detail="Email already exists")

    data = payload.model_dump()
    data["email"] = email

    try:
        return services.create_employee(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")


@app.get("/employees", response_model=list[Employee])
def list_employees(db: Session = Depends(get_db)):
    return services.list_employees(db)


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    if employee_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be greater than zero")

    employee = services.find_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    if employee_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be greater than zero")

    employee = services.find_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    email = str(payload.email).strip().lower()
    if services.email_exists(db, email, exclude_employee_id=employee_id):
        raise HTTPException(status_code=409, detail="Email already exists")

    data = payload.model_dump()
    data["email"] = email

    try:
        return services.update_employee(db, employee, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    if employee_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be greater than zero")

    employee = services.find_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    services.delete_employee(db, employee)
    return {"message": "Employee deleted"}