<div align="center">

# 💼 Employee Management API 💼

**A clean, production-shaped REST API for managing employee records — built with FastAPI, SQLAlchemy & MySQL.**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-2.0-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)
![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?style=flat-square)
![Swagger](https://img.shields.io/badge/Docs-Swagger_UI-85EA2D?style=flat-square&logo=swagger&logoColor=black)

</div>

---

## 📖 Overview

This API manages employee records — create, read, update, and delete — with strict request validation, auto-generated interactive docs, and persistent storage in a MySQL database via SQLAlchemy's ORM.

## ✨ Features

|     |                                                                                                  |
| --- | ------------------------------------------------------------------------------------------------ |
| ✅  | Full CRUD for employee records                                                                   |
| ✅  | Persistent MySQL storage via SQLAlchemy ORM                                                      |
| ✅  | Strict Pydantic validation (email format, `WFH`/`WFO` enum, non-blank/whitespace-trimmed fields) |
| ✅  | Duplicate-email prevention, including on update                                                  |
| ✅  | Search, filter, and paginate employees — all pushed down to SQLAlchemy queries, not Python       |
| ✅  | Work item management, linked to employees via a real foreign key + SQLAlchemy relationship       |
| ✅  | Search, filter, and paginate work items (by title, employee, status, priority)                   |
| ✅  | Clear `404` / `400` / `422` error handling                                                       |
| ✅  | Auto-generated Swagger UI & ReDoc                                                                |
| ✅  | Environment-based configuration via `.env`                                                       |

---

## 🗂️ Project Structure

```
employee-management-api/
├── app/
│   ├── main.py        # Route definitions & request wiring
│   ├── schemas.py      # Pydantic request/response models & validation
│   ├── services.py     # Business logic — CRUD operations
│   ├── models.py       # SQLAlchemy ORM models (DB table definitions)
│   └── database.py     # Engine, session factory, and get_db() dependency
├── requirements.txt
├── .env                # Local environment variables (not committed)
├── .env.example         # Template for required environment variables
└── README.md
```

---

## 🚀 Setup & Running with `uv`

### Prerequisites

- 🐍 Python 3.12
- 📦 [`uv`](https://docs.astral.sh/uv/) installed on your machine
- 🐬 MySQL Server running locally (or reachable remotely)

### 1️⃣ Clone & install dependencies

```bash
# Clone the repository
git clone https://github.com/Aravind-R5/employee-management-api.git
cd employee-management-api

# Switch to the task-4 branch (main does not include Task 4)
git checkout task-4

# Create virtual environment and install dependencies
uv venv --python 3.12
uv pip install -r requirements.txt
```

### 2️⃣ Create the MySQL database

Run the included `Employee.sql` script to create the database (and any seed setup it contains):

```bash
mysql -u root -p < Employee.sql
```

Or, if you'd rather create it manually via the MySQL CLI / MySQL Workbench:

```sql
CREATE DATABASE employee_db;
```

> The application creates its tables automatically on startup (`Base.metadata.create_all`) — `Employee.sql` (or the manual command above) only needs to create the empty database itself.

### 3️⃣ Configure environment variables

Create a `.env` file in the project root with your database credentials:

```env
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=employee_db
```

> ⚠️ If your password contains special characters (e.g. `@`), they must be URL-encoded — the app handles this internally via `urllib.parse.quote_plus`, but keep it in mind if you're building the connection string manually elsewhere.

### 4️⃣ Run the server

```bash
# Run with hot-reload (development)
uv run uvicorn app.main:app --reload

# Run without hot-reload (production)
uv run uvicorn app.main:app --host [IP_ADDRESS] --port [PORT]
```

### 5️⃣ Open the docs

| Docs          | URL                           |
| ------------- | ----------------------------- |
| 📘 Swagger UI | `http://127.0.0.1:8000/docs`  |
| 📗 ReDoc      | `http://127.0.0.1:8000/redoc` |

---

## 🔌 API Endpoints

| Method   | Endpoint          | Description                                                   |
| -------- | ----------------- | ------------------------------------------------------------- |
| `GET`    | `/health`         | Health check                                                  |
| `POST`   | `/employees`      | Create a new employee                                         |
| `GET`    | `/employees`      | List employees, with optional search, filters, and pagination |
| `GET`    | `/employees/{id}` | Get a single employee by ID                                   |
| `PUT`    | `/employees/{id}` | Update an employee                                            |
| `DELETE` | `/employees/{id}` | Delete an employee                                            |
| `POST`   | `/work-items`      | Create a work item and assign it to an employee               |
| `GET`    | `/work-items`      | List work items, with optional search, filters, and pagination |
| `GET`    | `/work-items/{work_item_id}` | Get a single work item by ID                         |
| `PUT`    | `/work-items/{work_item_id}` | Update a work item, including reassigning it         |
| `DELETE` | `/work-items/{work_item_id}` | Delete a work item (returns `204 No Content`)        |

---

## 🔗 Database Relationship

`Employee` and `WorkItem` are linked by a **one-to-many relationship**: one employee can have many work items, and each work item belongs to exactly one employee.

- **`work_items.employee_id`** is a real `ForeignKey("employees.id", ondelete="CASCADE")` column — the database itself rejects a work item pointing at an employee that doesn't exist, and automatically deletes an employee's work items if that employee is ever removed.
- SQLAlchemy's `relationship()` is configured on **both sides**, so related objects can be navigated in either direction without writing manual joins:
  - `employee.work_items` → list of that employee's work items
  - `work_item.assigned_employee` → the employee that work item belongs to
- On the `Employee` side, `cascade="all, delete-orphan"` mirrors the database-level `ondelete="CASCADE"` at the ORM level, so deleting an employee through the application also removes their work items in the same transaction.
- `GET /work-items` and `GET /work-items/{id}` use SQLAlchemy's `joinedload()` to fetch each work item and its assigned employee in a single SQL query (a `JOIN`), rather than firing a separate query per item — avoiding the classic N+1 query problem.

---

## 📝 Work Item API & Sample Requests

### Fields

| Field          | Type                                   | Notes                                                |
| -------------- | --------------------------------------- | ----------------------------------------------------- |
| `id`           | `integer`                               | Auto-generated                                        |
| `title`        | `string`                                | Required; blank/whitespace-only values are rejected   |
| `description`  | `string`                                | Optional                                               |
| `employee_id`  | `integer`                               | Required; must be a positive integer; must reference an existing employee |
| `status`       | `"TODO"` \| `"IN_PROGRESS"` \| `"COMPLETED"` | Defaults to `"TODO"`                              |
| `priority`     | `"LOW"` \| `"MEDIUM"` \| `"HIGH"`       | Defaults to `"MEDIUM"`                                 |
| `due_date`     | `date`                                  | Optional, format `YYYY-MM-DD`                          |
| `created_at`   | `datetime`                              | Auto-generated (IST)                                   |

### Create a work item

```
POST /work-items
{
  "title": "Prepare weekly status report",
  "employee_id": 2,
  "status": "TODO",
  "priority": "MEDIUM"
}
```

```
201 Created
{
  "id": 1,
  "title": "Prepare weekly status report",
  "description": null,
  "employee_id": 2,
  "status": "TODO",
  "priority": "MEDIUM",
  "due_date": null,
  "created_at": "2026-09-27T10:15:00+05:30",
  "assigned_employee": {
    "id": 2,
    "name": "Employee Name",
    "email": "employee@example.com"
  }
}
```

### `GET /work-items` query parameters

| Parameter     | Type      | Default | Description                                               |
| ------------- | --------- | ------- | ----------------------------------------------------------- |
| `search`      | `string`  | —       | Partial, case-insensitive match on work item title          |
| `employee_id` | `integer` | —       | Filter by assigned employee                                 |
| `status`      | `string`  | —       | Filter by `TODO`, `IN_PROGRESS`, or `COMPLETED`              |
| `priority`    | `string`  | —       | Filter by `LOW`, `MEDIUM`, or `HIGH`                         |
| `limit`       | `integer` | `10`    | Page size. Must be between `1` and `100`                    |
| `offset`      | `integer` | `0`     | Number of records to skip. Must not be negative             |

All filters can be used individually or combined, the same way employee filtering works.

```
GET /work-items?employee_id=2&status=IN_PROGRESS&priority=HIGH
→ in-progress, high-priority work items assigned to employee 2

GET /work-items?search=report&limit=5&offset=0
→ first 5 work items whose title contains "report"
```

```json
{
  "total": 2,
  "limit": 10,
  "offset": 0,
  "items": []
}
```

### Validation & error cases

| Case                                                | Response                                    |
| ---------------------------------------------------- | -------------------------------------------- |
| `employee_id` does not correspond to an existing employee | `404 Not Found`                        |
| Work item ID does not exist (`GET`/`PUT`/`DELETE`)   | `404 Not Found`                              |
| `status` is not one of `TODO` / `IN_PROGRESS` / `COMPLETED` | `422 Unprocessable Entity`            |
| `priority` is not one of `LOW` / `MEDIUM` / `HIGH`   | `422 Unprocessable Entity`                   |
| `title` is blank or whitespace-only                  | `422 Unprocessable Entity`                   |
| `employee_id` is zero or negative                    | `422 Unprocessable Entity`                   |
| No matching work items                               | `200 OK` with `total: 0` and `items: []`     |
| Successful delete                                     | `204 No Content`                             |

---

## 🔎 Search, Filtering & Pagination

`GET /employees` accepts the following optional query parameters, which can be used individually or combined. If none are provided, all employees are returned using the default pagination (`limit=10`, `offset=0`).

| Parameter    | Type      | Default | Description                                                                       |
| ------------ | --------- | ------- | --------------------------------------------------------------------------------- |
| `search`     | `string`  | —       | Partial, case-insensitive match on employee name (e.g. `asha` matches `Asha Rao`) |
| `department` | `string`  | —       | Exact match on department, case-insensitive                                       |
| `work_mode`  | `string`  | —       | Filter by `WFH` or `WFO` only — any other value is rejected                       |
| `is_active`  | `boolean` | —       | Filter by `true` or `false`                                                       |
| `limit`      | `integer` | `10`    | Page size. Must be between `1` and `100`                                          |
| `offset`     | `integer` | `0`     | Number of records to skip. Must not be negative                                   |

### Response shape

```json
{
  "total": 23,
  "limit": 5,
  "offset": 0,
  "items": [{ "id": 1, "name": "Asha Rao", "...": "..." }]
}
```

- `total` — number of employees matching the filters, **before** pagination is applied.
- `items` — the current page of matching employees, ordered by ascending `id`.
- If nothing matches, the response is still `200 OK` with `total: 0` and `items: []`.
- If `offset` goes past the end of the matching records, `items` comes back empty while `total` still reflects the correct count.

### Example requests

```
GET /employees
→ first 10 employees, no filters applied

GET /employees?search=asha
→ employees whose name contains "asha" (case-insensitive)

GET /employees?department=Engineering&work_mode=WFH&limit=5&offset=0
→ first 5 employees in Engineering who work from home

GET /employees?department=Engineering&work_mode=WFH&limit=5&offset=5
→ the next 5 matching employees (page 2 of the same filter)

GET /employees?is_active=false
→ only inactive employees

GET /employees?limit=0
→ 422 — limit must be between 1 and 100

GET /employees?work_mode=REMOTE
→ 422 — work_mode must be "WFH" or "WFO"
```

---

## 🧠 Reflection

### 📚 What I Learned

- Structuring a clean FastAPI project by separating route endpoints (`main.py`), business logic (`services.py`), and data validation models (`schemas.py`).
- Implementing Pydantic validation using `EmailStr` for email syntax verification and `Literal["WFH", "WFO"]` for strict work mode constraints.
- Enforcing path parameter constraints with `Path(..., gt=0)` to reject non-positive IDs with clear error responses.
- Managing virtual environments, dependencies, and execution with `uv`.
- Provisioning a project database in SQL Workbench and connecting it to the application layer.
- Designing ORM models (`models.py`) and a database connection/session layer (`database.py`) using SQLAlchemy.
- Refactoring `schemas.py` and `services.py` to move off in-memory storage and operate against a real database, including session-based query, commit, and rollback patterns.
- Core working principles of SQLAlchemy: engine and session management, and how a request-scoped session is handed off and closed via a dependency.
- Implementing case-insensitive partial search with `.ilike()` versus exact case-insensitive matching with `func.lower(...) == ...`, and when each is the right fit.
- Performing search, filtering, counting, and pagination entirely through chained SQLAlchemy query objects, so filtering happens at the database level instead of loading all records into Python.
- Using `Query(...)` with `ge=`/`le=` constraints to validate `limit` and `offset` at the FastAPI layer, before the request ever reaches the service layer.
- The importance of `.order_by(Employee.id.asc())` for stable, predictable pagination across repeated requests.
- Distinguishing `if is_active:` from `if is_active is not None:` — the former incorrectly treats an explicit `is_active=false` filter as "no filter," since `False` is falsy in Python.
- Modeling a one-to-many relationship between `Employee` and `WorkItem` using a `ForeignKey` column plus two-sided `relationship()` declarations (`back_populates`), so related objects can be navigated in either direction (`employee.work_items` and `work_item.assigned_employee`).
- The difference between ORM-level cascading (`cascade="all, delete-orphan"`) and database-level cascading (`ondelete="CASCADE"`), and why having both gives stronger data-integrity guarantees than either alone.
- Using SQLAlchemy's `Enum` column type to enforce `status` and `priority` as real database-level constraints, in addition to Pydantic's `Literal` validation at the API layer.
- Using `joinedload()` to fetch a work item and its assigned employee in a single SQL query, and why skipping this leads to the N+1 query problem once a response nests a related object.
- Designing a lightweight nested response schema (`EmployeeBasic`) to avoid exposing a full employee record inside every work item response.
- Reusing an existing service function (`get_employee_by_id`) purely for its validation side-effect, to turn a low-level foreign key failure into a clean `404` before the database is touched.

### 🧩 Difficulties Faced

- Ensuring the duplicate email check during `PUT` requests allows updating an employee's details without conflicting with their own existing email address.
- Managing local port re-binding conflicts (`[WinError 10048]`) when restarting the Uvicorn development server.
- Encountered a connection error during application startup caused by the "@" symbol in the local SQL Workbench password; resolved it using the `quote_plus` module from the `urllib.parse` package.

### 🔍 Assumptions Made

- Email comparison for duplicate checks is treated as case-insensitive.
- Work mode strictly accepts only `"WFH"` or `"WFO"`.
- Timestamps (`created_at`) are captured using Indian Standard Time (IST, UTC+5:30).
- Database schema and tables are provisioned manually via SQL Workbench for this stage, rather than through automated migration tooling.
- A work item must always be assigned to an existing employee on creation and on update — reassigning to an unassigned/null state is not supported.
- `status` defaults to `"TODO"` and `priority` defaults to `"MEDIUM"` when not explicitly provided.
- Deleting an employee also deletes all of their associated work items (cascading delete), rather than leaving them unassigned.
- `PUT /work-items/{id}` requires the full work item object (including `employee_id`), consistent with how employee updates are handled, rather than supporting partial updates.