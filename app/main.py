from fastapi import FastAPI, HTTPException, status

from app import services
from app.schemas import Employee, EmployeeCreate, EmployeeUpdate

app = FastAPI(title="Employee Management API")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/employees", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate):
    email = str(payload.email).lower()

    if any(item["email"].lower() == email for item in services.employees):
        raise HTTPException(status_code=409, detail="Email already exists")

    return services.create_employee(payload.model_dump())


@app.get("/employees", response_model=list[Employee])
def list_employees():
    return services.employees


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int):
    if employee_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be greater than zero")

    employee = services.find_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, payload: EmployeeUpdate):
    if employee_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be greater than zero")

    employee = services.find_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    email = str(payload.email).lower()
    duplicate = any(
        item["id"] != employee_id and item["email"].lower() == email
        for item in services.employees
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Email already exists")

    employee.update(payload.model_dump())
    return employee


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    if employee_id <= 0:
        raise HTTPException(status_code=400, detail="ID must be greater than zero")

    employee = services.find_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    services.employees.remove(employee)
    return {"message": "Employee deleted"}