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

This API manages employee records and the work items assigned to them — create, read, update, and delete — with strict request validation, a controlled work item status workflow, per-employee work summaries, auto-generated interactive docs, and persistent storage in a MySQL database via SQLAlchemy's ORM.

## ✨ Features

|     |                                                                                                                    |
| --- | ------------------------------------------------------------------------------------------------------------------ |
| ✅  | Full CRUD for employee records                                                                                     |
| ✅  | Persistent MySQL storage via SQLAlchemy ORM                                                                        |
| ✅  | Strict Pydantic validation (email format, `WFH`/`WFO` enum, non-blank/whitespace-trimmed fields)                   |
| ✅  | Duplicate-email prevention, including on update                                                                    |
| ✅  | Search, filter, and paginate employees — all pushed down to SQLAlchemy queries, not Python                         |
| ✅  | Work item management, linked to employees via a real foreign key + SQLAlchemy relationship                         |
| ✅  | Search, filter, and paginate work items (by title, employee, status, priority)                                     |
| ✅  | Work item status workflow (`TODO → IN_PROGRESS → COMPLETED`) enforced on create, `PUT`, and `PATCH`                |
| ✅  | Per-employee work summary, with status counts calculated in the database                                           |
| ✅  | Task 6: two independent services (Employee on port 8001, Work Item on port 8002), each with its own database       |
| ✅  | Task 6: the Work Item Service checks employees through an HTTPX call (5-second timeout) and returns `404` or `503` |
| ✅  | Clear `404` / `400` / `422` error handling                                                                         |
| ✅  | Auto-generated Swagger UI & ReDoc                                                                                  |
| ✅  | Environment-based configuration via `.env`                                                                         |

---

## 🗂️ Project Structure

```
employee-management-api/
├── app/                         # Task 5 application (unchanged)
│   ├── main.py        # Route definitions & request wiring
│   ├── schemas.py      # Pydantic request/response models & validation
│   ├── services.py     # Business logic — CRUD, status rules, work summary
│   ├── models.py       # SQLAlchemy ORM models (DB table definitions)
│   └── database.py     # Engine, session factory, and get_db() dependency
├── employee_service/            # Task 6: Employee Service (port 8001)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # Employee routes + /health
│   │   ├── schemas.py      # Employee request/response models
│   │   ├── services.py     # Employee business logic
│   │   ├── models.py       # Employee table
│   │   └── database.py     # Connection to employee_service_db
│   ├── requirements.txt
│   └── .env.example
├── work_item_service/           # Task 6: Work Item Service (port 8002)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # Work item routes + /health
│   │   ├── schemas.py      # Work item request/response models
│   │   ├── services.py     # Work item logic + HTTP call to the Employee Service
│   │   ├── models.py       # WorkItem table (employee_id is a plain integer)
│   │   └── database.py     # Connection to work_item_service_db
│   ├── requirements.txt
│   └── .env.example
├── requirements.txt
├── .env                # Local environment variables (not committed)
├── .env.example         # Template for required environment variables
└── README.md
```

---

## 🚀 Setup & Running with `uv`

> This section covers the Task 5 application in `app/`, which is unchanged. For the two Task 6 services, see [Microservices (Task 6)](#-microservices-task-6).

### Prerequisites

- 🐍 Python 3.12
- 📦 [`uv`](https://docs.astral.sh/uv/) installed on your machine
- 🐬 MySQL Server running locally (or reachable remotely)

### 1️⃣ Clone & install dependencies

```bash
# Clone the repository
git clone https://github.com/Aravind-R5/employee-management-api.git
cd employee-management-api

# Switch to the task-6 branch (main does not include Task 6)
git checkout task-6

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

| Method   | Endpoint                                | Description                                                             |
| -------- | --------------------------------------- | ----------------------------------------------------------------------- |
| `GET`    | `/health`                               | Health check                                                            |
| `POST`   | `/employees`                            | Create a new employee                                                   |
| `GET`    | `/employees`                            | List employees, with optional search, filters, and pagination           |
| `GET`    | `/employees/{id}`                       | Get a single employee by ID                                             |
| `PUT`    | `/employees/{id}`                       | Update an employee                                                      |
| `DELETE` | `/employees/{id}`                       | Delete an employee                                                      |
| `GET`    | `/employees/{employee_id}/work-summary` | Get an employee's work item counts by status                            |
| `POST`   | `/work-items`                           | Create a work item and assign it to an employee (starts as `TODO`)      |
| `GET`    | `/work-items`                           | List work items, with optional search, filters, and pagination          |
| `GET`    | `/work-items/{work_item_id}`            | Get a single work item by ID                                            |
| `PUT`    | `/work-items/{work_item_id}`            | Update a work item or reassign it; status changes follow the same rules |
| `PATCH`  | `/work-items/{work_item_id}/status`     | Change only the status (`TODO → IN_PROGRESS → COMPLETED`)               |
| `DELETE` | `/work-items/{work_item_id}`            | Delete a work item (returns `204 No Content`)                           |

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

| Field         | Type                                         | Notes                                                                                                                     |
| ------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `id`          | `integer`                                    | Auto-generated                                                                                                            |
| `title`       | `string`                                     | Required; blank/whitespace-only values are rejected                                                                       |
| `description` | `string`                                     | Optional                                                                                                                  |
| `employee_id` | `integer`                                    | Required; must be a positive integer; must reference an existing employee                                                 |
| `status`      | `"TODO"` \| `"IN_PROGRESS"` \| `"COMPLETED"` | Defaults to `"TODO"`; new work items must start as `TODO`, then follow the [status workflow](#-work-item-status-workflow) |
| `priority`    | `"LOW"` \| `"MEDIUM"` \| `"HIGH"`            | Defaults to `"MEDIUM"`                                                                                                    |
| `due_date`    | `date`                                       | Optional, format `YYYY-MM-DD`                                                                                             |
| `created_at`  | `datetime`                                   | Auto-generated (IST)                                                                                                      |

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

| Parameter     | Type      | Default | Description                                        |
| ------------- | --------- | ------- | -------------------------------------------------- |
| `search`      | `string`  | —       | Partial, case-insensitive match on work item title |
| `employee_id` | `integer` | —       | Filter by assigned employee                        |
| `status`      | `string`  | —       | Filter by `TODO`, `IN_PROGRESS`, or `COMPLETED`    |
| `priority`    | `string`  | —       | Filter by `LOW`, `MEDIUM`, or `HIGH`               |
| `limit`       | `integer` | `10`    | Page size. Must be between `1` and `100`           |
| `offset`      | `integer` | `0`     | Number of records to skip. Must not be negative    |

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

| Case                                                          | Response                                 |
| ------------------------------------------------------------- | ---------------------------------------- |
| `employee_id` does not correspond to an existing employee     | `404 Not Found`                          |
| Work item ID does not exist (`GET`/`PUT`/`DELETE`)            | `404 Not Found`                          |
| `status` is not one of `TODO` / `IN_PROGRESS` / `COMPLETED`   | `422 Unprocessable Entity`               |
| `priority` is not one of `LOW` / `MEDIUM` / `HIGH`            | `422 Unprocessable Entity`               |
| `title` is blank or whitespace-only                           | `422 Unprocessable Entity`               |
| `employee_id` is zero or negative                             | `422 Unprocessable Entity`               |
| Creating a work item with status `IN_PROGRESS` or `COMPLETED` | `400 Bad Request`                        |
| Skipped status change (e.g. `TODO` → `COMPLETED`)             | `400 Bad Request`                        |
| Backward status change (e.g. `IN_PROGRESS` → `TODO`)          | `400 Bad Request`                        |
| `PUT` containing a disallowed status change                   | `400 Bad Request`, nothing is saved      |
| Requesting the work item's current status again               | `200 OK`, record unchanged               |
| `PATCH` status is missing, `null`, or invalid                 | `422 Unprocessable Entity`               |
| Work summary requested for a nonexistent employee             | `404 Not Found`                          |
| No matching work items                                        | `200 OK` with `total: 0` and `items: []` |
| Successful delete                                             | `204 No Content`                         |

---

## 🔄 Work Item Status Workflow

A work item's status can only move forward, one step at a time:

```
TODO  →  IN_PROGRESS  →  COMPLETED
```

| Current status | Requested status        | Result                                |
| -------------- | ----------------------- | ------------------------------------- |
| `TODO`         | `IN_PROGRESS`           | ✅ `200 OK`                           |
| `IN_PROGRESS`  | `COMPLETED`             | ✅ `200 OK`                           |
| Any status     | The same status         | ✅ `200 OK`, record is not changed    |
| `TODO`         | `COMPLETED`             | ❌ `400 Bad Request` (skipped a step) |
| `IN_PROGRESS`  | `TODO`                  | ❌ `400 Bad Request` (backward)       |
| `COMPLETED`    | `TODO` or `IN_PROGRESS` | ❌ `400 Bad Request` (backward)       |

### Rules

- **On creation:** `status` is optional and defaults to `TODO`. Supplying `IN_PROGRESS` or `COMPLETED` returns `400` with a clear message.
- **`PATCH /work-items/{work_item_id}/status`:** `status` is required. A missing, `null`, or invalid value returns `422`. A missing work item returns `404`. A successful change returns the updated work item.
- **`PUT /work-items/{work_item_id}`:** follows the same transition rules when `status` is supplied. Omitting the `status` field keeps the current value. Sending `"status": null` is rejected with `422 Unprocessable Entity`.
- **Rejected updates save nothing:** if a `PUT` contains a disallowed status change, the whole update is rejected and no other field (title, priority, employee, etc.) is changed.
- The transition check is a single shared function, used by both `PATCH` and `PUT`.

### Change a work item's status

```
PATCH /work-items/1/status
{
  "status": "IN_PROGRESS"
}
```

```
200 OK
{
  "id": 1,
  "title": "Prepare weekly status report",
  "description": null,
  "employee_id": 2,
  "status": "IN_PROGRESS",
  "priority": "MEDIUM",
  "due_date": null,
  "created_at": "2026-10-13T10:15:00+05:30",
  "assigned_employee": {
    "id": 2,
    "name": "Employee Name",
    "email": "employee@example.com"
  }
}
```

### Update a work item without changing its status

Leave `status` out of the request body completely and the current status is preserved (explicitly passing `"status": null` is invalid and returns `422 Unprocessable Entity`):

```
PUT /work-items/1
{
  "title": "Prepare weekly status report",
  "description": "Compile this week's task progress and share it with the team lead",
  "employee_id": 2,
  "priority": "HIGH",
  "due_date": "2026-10-20"
}
```

```
200 OK  →  title, description, priority and due_date are updated; status is unchanged
```

### Error examples

```
PATCH /work-items/1/status   { "status": "COMPLETED" }      (current status is TODO)
400 Bad Request
{
  "detail": "Disallowed status change from 'TODO' to 'COMPLETED'. Allowed flow: TODO -> IN_PROGRESS -> COMPLETED."
}
```

```
POST /work-items   { "title": "Fix bug", "employee_id": 2, "status": "COMPLETED" }
400 Bad Request
{
  "detail": "New work items must start with status 'TODO'."
}
```

```
PATCH /work-items/1/status   { "status": "DONE" }   (also: {} or { "status": null })
422 Unprocessable Entity     (status must be TODO, IN_PROGRESS or COMPLETED)
```

```
PATCH /work-items/999/status   { "status": "IN_PROGRESS" }
404 Not Found
{
  "detail": "Work item with ID 999 not found."
}
```

---

## 📊 Employee Work Summary

`GET /employees/{employee_id}/work-summary` returns how many work items are currently assigned to an employee, grouped by status.

```
GET /employees/1/work-summary
```

```
200 OK
{
  "employee_id": 1,
  "total_work_items": 5,
  "todo": 2,
  "in_progress": 2,
  "completed": 1
}
```

### Rules

- The counts are calculated in the database with a single SQLAlchemy query (`COUNT` plus `SUM(CASE ...)`), not by loading work items into Python.
- Only work items **currently assigned** to the requested employee are counted, so reassigned and deleted work items are reflected immediately.
- `todo + in_progress + completed` always equals `total_work_items`.
- An employee with no work items returns zero for every count.
- A nonexistent employee returns `404 Not Found`, and an `employee_id` of zero or below returns `422`.

```
GET /employees/99/work-summary
404 Not Found
{
  "detail": "Employee with ID 99 not found."
}
```

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

## 🧩 Microservices (Task 6)

Task 6 separates part of the application into two services that run independently and talk to each other through an API call. The Task 5 application in `app/` is left unchanged.

```
Client ──► Work Item Service (8002) ── GET /employees/{id} ──► Employee Service (8001)
                   │                                                    │
          work_item_service_db                                 employee_service_db
```

| Service               | Port   | Database               | Endpoints                                                                              |
| --------------------- | ------ | ---------------------- | -------------------------------------------------------------------------------------- |
| **Employee Service**  | `8001` | `employee_service_db`  | `POST /employees`, `GET /employees`, `GET /employees/{employee_id}`, `GET /health`     |
| **Work Item Service** | `8002` | `work_item_service_db` | `POST /work-items`, `GET /work-items`, `GET /work-items/{work_item_id}`, `GET /health` |

Each service has its own FastAPI application, database connection, models, schemas, service layer, and Swagger UI. Update, delete, status, and summary features are moved across in later tasks.

### 1️⃣ Clone & switch to task-6

```bash
git clone https://github.com/Aravind-R5/employee-management-api.git
cd employee-management-api

# Switch to the task-6 branch (main does not include Task 6)
git checkout task-6
```

### 2️⃣ Create the two MySQL databases

Both databases can live on the same local MySQL server. Log into MySQL (CLI or MySQL Workbench) and run:

```sql
CREATE DATABASE employee_service_db;
CREATE DATABASE work_item_service_db;
```

> Each service creates its own tables automatically on startup (`Base.metadata.create_all`), so only the empty databases are needed. Use fresh sample data — the Task 5 database `employee_db` is not deleted or migrated.

### 3️⃣ Configure environment variables

Each service has its own `.env.example`. Copy it to `.env` **inside that service's folder** and fill in your credentials.

```bash
cd employee_service
cp .env.example .env        # Windows: copy .env.example .env
cd ../work_item_service
cp .env.example .env        # Windows: copy .env.example .env
cd ..
```

**`employee_service/.env`**

```env
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=employee_service_db
```

**`work_item_service/.env`**

```env
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=work_item_service_db
EMPLOYEE_SERVICE_URL=http://localhost:8001
```

> ⚠️ Create the `.env` file inside each service folder, not only in the repository root. A service without its own `.env` can end up reading the root one, which points to the Task 5 database. Special characters in the password (e.g. `@`) are handled by `urllib.parse.quote_plus`, as before. Never commit real `.env` files.

### 4️⃣ Install dependencies & run each service

Each service has its own `requirements.txt` and its own virtual environment. Open **two separate terminals**, one per service. The services can be started in any order.

**Terminal 1: Employee Service (port 8001)**

```bash
cd employee_service
uv venv --python 3.12
uv pip install -r requirements.txt
uv run uvicorn app.main:app --reload --port 8001
```

**Terminal 2: Work Item Service (port 8002)**

```bash
cd work_item_service
uv venv --python 3.12
uv pip install -r requirements.txt
uv run uvicorn app.main:app --reload --port 8002
```

> Run each command from inside its own service folder. Both services contain a package named `app`, so starting one from the repository root would load the Task 5 application instead.

### 5️⃣ Open the docs

| Service           | Swagger UI                   | Health check                   |
| ----------------- | ---------------------------- | ------------------------------ |
| Employee Service  | `http://127.0.0.1:8001/docs` | `http://127.0.0.1:8001/health` |
| Work Item Service | `http://127.0.0.1:8002/docs` | `http://127.0.0.1:8002/health` |

### 🔄 How the services communicate

Before saving a new work item, the Work Item Service calls the Employee Service with HTTPX (5-second timeout):

```
GET {EMPLOYEE_SERVICE_URL}/employees/{employee_id}
```

| Employee Service result                              | Work Item Service response                     | Work item saved? |
| ---------------------------------------------------- | ---------------------------------------------- | ---------------- |
| `200 OK` (employee found)                            | `201 Created`                                  | ✅ Yes           |
| `404 Not Found`                                      | `404` with `"Employee not found"`              | ❌ No            |
| Stopped, no connection, timeout, or unexpected error | `503 Service Unavailable` with a clear message | ❌ No            |

- **No shared database relationship:** the two tables now live in different databases, so `work_items.employee_id` is a plain integer with no foreign key and no ORM relationship. Employee existence is checked through the API call instead.
- **Separate data access:** each service reads and writes only its own database, and never imports the other service's models.
- **Viewing keeps working:** `GET /work-items` and `GET /work-items/{work_item_id}` only read the Work Item Service's own database, so saved work items can still be viewed while the Employee Service is stopped.
- **Configurable address:** the Employee Service URL comes from the `EMPLOYEE_SERVICE_URL` environment variable.

### 📨 Sample requests & responses

#### Employee Service (port 8001)

```
GET /health
→ 200 OK
{ "status": "ok", "service": "Employee Service", "port": 8001 }
```

```
POST /employees
{
  "name": "Asha Rao",
  "email": "asha@corp.com",
  "department": "Engineering",
  "primary_skill": "Python",
  "location": "Chennai",
  "work_mode": "WFH"
}
```

```
201 Created
{
  "name": "Asha Rao",
  "email": "asha@corp.com",
  "department": "Engineering",
  "primary_skill": "Python",
  "location": "Chennai",
  "work_mode": "WFH",
  "id": 1,
  "is_active": true,
  "created_at": "2026-10-29T10:15:00"
}
```

```
GET /employees/1   → 200 OK, the employee above
GET /employees/99  → 404 Not Found
{ "detail": "Employee with ID 99 not found." }
```

```
POST /employees   (an email that already exists)
→ 400 Bad Request
{ "detail": "Employee with email 'asha@corp.com' already exists." }
```

#### Work Item Service (port 8002)

```
POST /work-items
{
  "title": "Prepare weekly status report",
  "description": "Compile this week's task progress",
  "employee_id": 1,
  "priority": "HIGH",
  "due_date": "2026-11-20"
}
```

```
201 Created
{
  "id": 1,
  "title": "Prepare weekly status report",
  "description": "Compile this week's task progress",
  "employee_id": 1,
  "status": "TODO",
  "priority": "HIGH",
  "due_date": "2026-11-20",
  "created_at": "2026-10-29T10:20:00"
}
```

The response has `employee_id` and the work item's own details. The nested `assigned_employee` object is not part of Task 6.

```
GET /work-items?employee_id=1&limit=10&offset=0
→ 200 OK
{
  "total": 1,
  "limit": 10,
  "offset": 0,
  "items": [{ "id": 1, "title": "Prepare weekly status report", "employee_id": 1, "status": "TODO", "...": "..." }]
}
```

```
GET /work-items/99
→ 404 Not Found
{ "detail": "Work item with ID 99 not found." }
```

#### Error cases when creating a work item

| Case                                                      | Response                                                                 | Saved? |
| --------------------------------------------------------- | ------------------------------------------------------------------------ | ------ |
| `employee_id` does not exist in the Employee Service      | `404` — `{ "detail": "Employee not found" }`                             | ❌     |
| Employee Service stopped or slower than 5 seconds         | `503` — `{ "detail": "Employee Service is unavailable or timed out." }`  | ❌     |
| Employee Service returns an unexpected error              | `503` — `{ "detail": "Employee Service returned an unexpected error." }` | ❌     |
| `status` is `IN_PROGRESS` or `COMPLETED`                  | `400` — `{ "detail": "New work items must start with status 'TODO'." }`  | ❌     |
| `status` is `null` or not one of the three allowed values | `422 Unprocessable Entity`                                               | ❌     |
| `title` is blank or whitespace-only                       | `422 Unprocessable Entity`                                               | ❌     |
| `employee_id` is zero or negative                         | `422 Unprocessable Entity`                                               | ❌     |

#### Suggested test order

1. Start both services and check `/health` on ports 8001 and 8002.
2. Create an employee in the Employee Service, then create a work item for that employee (`201`).
3. Create a work item for an employee ID that doesn't exist (`404`, nothing saved).
4. Stop the Employee Service and create a work item (`503`, nothing saved).
5. With the Employee Service still stopped, open `GET /work-items` (`200`, saved items still visible).
6. Restart the Employee Service and create a work item again (`201`).
7. Restart both services and confirm the data is still there.

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
- Modeling a status workflow with an `ALLOWED_TRANSITIONS` mapping and one shared `validate_status_transition()` function, so `PATCH` and `PUT` apply exactly the same rules.
- Validating before changing anything: checking the status transition before assigning any field, so a rejected `PUT` leaves all existing data untouched.
- The difference between `422` (Pydantic rejects the shape or value of the data automatically) and `400` (a business rule enforced in the service layer with `HTTPException`), and why the "new work items must start as `TODO`" rule belongs in the service layer to return `400`.
- Using `Optional[...] = None` in a Pydantic schema so an omitted field can mean "keep the current value", versus a required field for `PATCH`.
- Building a summary in a single SQLAlchemy query with `func.count`, `func.sum(case(...))`, and `func.coalesce`, so an employee with no work items returns zeros instead of `NULL`.
- Keeping each layer in its own job: validation in schemas, business rules and database operations in services, and request handling in thin routes.

### 🧩 Difficulties Faced

- Ensuring the duplicate email check during `PUT` requests allows updating an employee's details without conflicting with their own existing email address.
- Managing local port re-binding conflicts (`[WinError 10048]`) when restarting the Uvicorn development server.
- Encountered a connection error during application startup caused by the "@" symbol in the local SQL Workbench password; resolved it using the `quote_plus` module from the `urllib.parse` package.
- While testing `PUT` without a status in Swagger UI, the pre-filled request body contained `"status": ""`, which is an invalid value and returned `422`. Omitting the status means removing the field from the body entirely.
- Understanding why creating a work item with `IN_PROGRESS` or `COMPLETED` must return `400` rather than `422`; I moved that check from a schema validator into `create_work_item` in the service layer.

### 🔍 Assumptions Made

- Email comparison for duplicate checks is treated as case-insensitive.
- Work mode strictly accepts only `"WFH"` or `"WFO"`.
- Timestamps (`created_at`) are captured using Indian Standard Time (IST, UTC+5:30).
- Database schema and tables are provisioned manually via SQL Workbench for this stage, rather than through automated migration tooling.
- A work item must always be assigned to an existing employee on creation and on update — reassigning to an unassigned/null state is not supported.
- `status` defaults to `"TODO"` and `priority` defaults to `"MEDIUM"` when not explicitly provided.
- Deleting an employee also deletes all of their associated work items (cascading delete), rather than leaving them unassigned.
- `PUT /work-items/{id}` requires the full work item object (including `employee_id`), consistent with how employee updates are handled, rather than supporting partial updates.
- On both `POST` and `PUT`, sending `"status": null` returns `422 Unprocessable Entity`. Only omitting the `status` key entirely defaults to `TODO` on creation or preserves the current status on update.
- `COMPLETED` is a final status: a completed work item cannot be moved back, and resending `COMPLETED` is accepted without changes.
- Requesting the status a work item already has returns `200 OK` and does not write to the database.
- Work item counts in the summary reflect the current database state: deleted work items are removed records and are not counted, and a reassigned work item counts toward its new employee.
