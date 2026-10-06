# Employee Management API

A REST API built with FastAPI, SQLAlchemy, and MySQL for managing employees and their assigned work items.

This project was completed across Tasks 1, 2, 3, and 4.

## Features

### Tasks 1–3: Employee Management

- Create, list, retrieve, update, and delete employees.
- Validate employee input and prevent duplicate email addresses.
- Search employees and filter by department, work mode, and active status.
- Paginate employee results with `limit` and `offset`.

### Task 4: Work Item Management

- Create work items and assign each one to an existing employee.
- Retrieve, update, reassign, and delete work items.
- Search work items by title (partial, case-insensitive).
- Filter work items by employee, status, and priority.
- Paginate work-item results.
- Return the assigned employee's basic details with every work-item response.

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- MySQL
- Pydantic
- Uvicorn
- PyMySQL

## Setup and Execution

1. Clone the repository and enter its directory.

   ```bash
   git clone <your-repository-url>
   cd employee-record-management
   ```

2. Create and activate a virtual environment.

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

4. Create the MySQL database.

   ```sql
   CREATE DATABASE employee_management;
   ```

5. Create a `.env` file in the project root.

   ```env
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/employee_management
   ```

6. Start the API.

   ```powershell
   uvicorn app.main:app --reload
   ```

7. Open Swagger UI at `http://127.0.0.1:8000/docs`.

## Database Relationship

The database has an `employees` table and a `work_items` table.

```text
One Employee  ───<  Many Work Items
employees.id       work_items.employee_id
```

`work_items.employee_id` is a foreign key to `employees.id`. A work item must be assigned to an existing employee. SQLAlchemy implements the one-to-many relationship with `Employee.work_items` and `WorkItem.assigned_employee`.

```python
# WorkItem model
employee_id = mapped_column(ForeignKey("employees.id"), nullable=False)
assigned_employee = relationship("Employee", back_populates="work_items")

# Employee model
work_items = relationship("WorkItem", back_populates="assigned_employee")
```

## Employee APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/employees` | Create an employee |
| GET | `/employees` | List employees with search, filters, and pagination |
| GET | `/employees/{employee_id}` | Get one employee |
| PUT | `/employees/{employee_id}` | Update an employee |
| DELETE | `/employees/{employee_id}` | Delete an employee |

### Create employee example

```json
{
  "name": "Asha Kumar",
  "email": "asha.kumar@example.com",
  "department": "Human Resources",
  "location": "Chennai",
  "primary_skill": "Recruitment",
  "work_mode": "WFO",
  "is_active": true
}
```

## Work Item APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/work-items` | Create and assign a work item |
| GET | `/work-items` | List work items with search, filters, and pagination |
| GET | `/work-items/{work_item_id}` | Get one work item |
| PUT | `/work-items/{work_item_id}` | Update or reassign a work item |
| DELETE | `/work-items/{work_item_id}` | Delete a work item (`204 No Content`) |

### Create work item example

**POST** `/work-items`

```json
{
  "title": "Prepare weekly status report",
  "description": "Prepare and submit the weekly team progress report.",
  "employee_id": 1,
  "status": "TODO",
  "priority": "HIGH",
  "due_date": "2026-10-10"
}
```

Expected status: `201 Created`.

Example response:

```json
{
  "id": 1,
  "title": "Prepare weekly status report",
  "description": "Prepare and submit the weekly team progress report.",
  "employee_id": 1,
  "status": "TODO",
  "priority": "HIGH",
  "due_date": "2026-10-10",
  "created_at": "2026-10-03T20:04:23",
  "assigned_employee": {
    "id": 1,
    "name": "Asha Kumar",
    "email": "asha.kumar@example.com"
  }
}
```

## Work-Item Search, Filtering, and Pagination

| Parameter | Description |
|---|---|
| `search` | Partial, case-insensitive title search |
| `employee_id` | Filter by assigned employee |
| `status` | `TODO`, `IN_PROGRESS`, or `COMPLETED` |
| `priority` | `LOW`, `MEDIUM`, or `HIGH` |
| `limit` | Default `10`, minimum `1`, maximum `100` |
| `offset` | Default `0`, minimum `0` |

Examples:

```text
GET /work-items?search=report
GET /work-items?employee_id=1
GET /work-items?status=TODO
GET /work-items?priority=HIGH
GET /work-items?search=dashboard&employee_id=2&status=IN_PROGRESS&priority=HIGH&limit=10&offset=0
GET /work-items?limit=3&offset=3
```

List responses follow this format. `total` is counted before applying `limit` and `offset`.

```json
{
  "total": 10,
  "limit": 3,
  "offset": 0,
  "items": []
}
```

## Validation and Error Cases

| Case | Expected result |
|---|---|
| Assigned employee exists | `201 Created` |
| Assigned employee does not exist | `404 Not Found` |
| Work item does not exist | `404 Not Found` |
| Blank or whitespace-only title | `422 Unprocessable Entity` |
| Invalid status | `422 Unprocessable Entity` |
| Invalid priority | `422 Unprocessable Entity` |
| `employee_id` is zero or negative | `422 Unprocessable Entity` |
| Duplicate employee email | `409 Conflict` |
| Invalid `limit` or `offset` | `422 Unprocessable Entity` |
| Delete existing work item | `204 No Content` |

## Testing Performed

- Created employees and work items for existing employees.
- Confirmed assigning a work item to a non-existent employee returns `404`.
- Retrieved a work item by ID.
- Tested title search.
- Tested employee, status, and priority filters.
- Tested combined filters.
- Tested multiple `limit` and `offset` values.
- Updated a work item and reassigned it to another employee.
- Tested invalid status and priority values.
- Tested blank-title validation.
- Tested a missing work-item ID.
- Deleted a work item.
- Restarted the application and confirmed MySQL records remain available.
- Confirmed employee APIs continue to work.

## Screenshots

Create a `screenshots` folder in the repository and put the Swagger screenshots inside it. Replace the filenames below if your own names differ.

```text
screenshots/
├── create-work-item-201.png
├── combined-filters-200.png
├── pagination-200.png
├── invalid-employee-404.png
├── invalid-status-422.png
├── update-work-item-200.png
└── delete-work-item-204.png
```




## Assumptions

- Employee IDs are automatically generated.
- A work item has exactly one assigned employee.
- An employee can have many work items.
- Work-item status defaults to `TODO`.
- Work-item priority defaults to `MEDIUM`.
- Results are returned in ascending order by work-item ID.
- MySQL is used as the persistent database.

## What I Learned

- How to build REST APIs with FastAPI.
- How to validate input using Pydantic.
- How to use SQLAlchemy with MySQL.
- How to create foreign-key relationships and one-to-many SQLAlchemy relationships.
- How to implement searching, filtering, counting, ordering, and pagination with SQLAlchemy queries.
- How to return related employee data in work-item responses.

## Difficulties Faced

- Configuring two-way SQLAlchemy relationships with `back_populates`.
- Ensuring MySQL `VARCHAR` columns have lengths.
- Handling invalid status, priority, blank-title, and missing-record errors.
- Returning assigned employee details along with work items.

## Git Branch

Task 4 was completed on the `task-4` branch.
