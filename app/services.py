from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import Employee
from app import models, schemas


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
    
def get_employee_by_id(db: Session, employee_id: int):
    return (
        db.query(models.Employee)
        .filter(models.Employee.id == employee_id)
        .first()
    )


def create_work_item(
    db: Session,
    work_item: schemas.WorkItemCreate,
):
    db_work_item = models.WorkItem(**work_item.model_dump())

    db.add(db_work_item)
    db.commit()
    db.refresh(db_work_item)

    return (
        db.query(models.WorkItem)
        .options(joinedload(models.WorkItem.assigned_employee))
        .filter(models.WorkItem.id == db_work_item.id)
        .first()
    )


def get_work_item(db: Session, work_item_id: int):
    return (
        db.query(models.WorkItem)
        .options(joinedload(models.WorkItem.assigned_employee))
        .filter(models.WorkItem.id == work_item_id)
        .first()
    )


def get_work_items(
    db: Session,
    search: str | None = None,
    employee_id: int | None = None,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    query = db.query(models.WorkItem)

    if search:
        query = query.filter(
            models.WorkItem.title.ilike(f"%{search}%")
        )

    if employee_id is not None:
        query = query.filter(
            models.WorkItem.employee_id == employee_id
        )

    if status is not None:
        query = query.filter(
            models.WorkItem.status == status
        )

    if priority is not None:
        query = query.filter(
            models.WorkItem.priority == priority
        )

    total = query.count()

    items = (
        query.options(joinedload(models.WorkItem.assigned_employee))
        .order_by(models.WorkItem.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return total, items


def update_work_item(
    db: Session,
    db_work_item: models.WorkItem,
    work_item_update: schemas.WorkItemUpdate,
):
    update_data = work_item_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_work_item, field, value)

    db.commit()
    db.refresh(db_work_item)

    return get_work_item(db, db_work_item.id)


def delete_work_item(
    db: Session,
    db_work_item: models.WorkItem,
):
    db.delete(db_work_item)
    db.commit()