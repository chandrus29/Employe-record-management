from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Employee


def commit_or_rollback(db: Session) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def create_employee(db: Session, data: dict) -> Employee:
    employee = Employee(**data)
    db.add(employee)
    commit_or_rollback(db)
    db.refresh(employee)
    return employee


def list_employees(
    db: Session,
    search: str | None = None,
    department: str | None = None,
    work_mode: str | None = None,
    is_active: bool | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    query = db.query(Employee)

    if search is not None and search.strip():
        query = query.filter(
            Employee.name.ilike(f"%{search.strip()}%")
        )

    if department is not None and department.strip():
        query = query.filter(
            Employee.department == department.strip()
        )

    if work_mode is not None:
        query = query.filter(Employee.work_mode == work_mode)

    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)

    total = query.count()

    items = (
        query.order_by(Employee.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


def find_employee(db: Session, employee_id: int) -> Employee | None:
    return (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )


def email_exists(
    db: Session,
    email: str,
    exclude_id: int | None = None,
) -> bool:
    query = db.query(Employee).filter(
        func.lower(Employee.email) == email.strip().lower()
    )

    if exclude_id is not None:
        query = query.filter(Employee.id != exclude_id)

    return query.first() is not None


def update_employee(
    db: Session,
    employee: Employee,
    data: dict,
) -> Employee:
    for field, value in data.items():
        setattr(employee, field, value)

    commit_or_rollback(db)
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: Employee) -> None:
    db.delete(employee)
    commit_or_rollback(db)