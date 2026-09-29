from datetime import datetime, timezone

employees: list[dict] = []
next_id = 1


def create_employee(data: dict) -> dict:
    global next_id

    employee = {
        **data,
        "id": next_id,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    employees.append(employee)
    next_id += 1
    return employee


def find_employee(employee_id: int) -> dict | None:
    return next(
        (employee for employee in employees if employee["id"] == employee_id),
        None,
    )