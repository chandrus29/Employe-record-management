from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Employee


def create_employee(db: Session, data: dict) -> Employee:
    employee = Employee(**data)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def list_employees(db: Session) -> list[Employee]:
    return db.query(Employee).all()


def find_employee(db: Session, employee_id: int) -> Employee | None:
    return db.query(Employee).filter(Employee.id == employee_id).first()


def email_exists(
    db: Session,
    email: str,
    exclude_employee_id: int | None = None,
) -> bool:
    query = db.query(Employee).filter(
        func.lower(Employee.email) == email.strip().lower()
    )

    if exclude_employee_id is not None:
        query = query.filter(Employee.id != exclude_employee_id)

    return query.first() is not None


def update_employee(db: Session, employee: Employee, data: dict) -> Employee:
    for field, value in data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: Employee) -> None:
    db.delete(employee)
    db.commit()