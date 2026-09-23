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

### 🧩 Difficulties Faced

- Ensuring the duplicate email check during `PUT` requests allows updating an employee's details without conflicting with their own existing email address.
- Managing local port re-binding conflicts (`[WinError 10048]`) when restarting the Uvicorn development server.
- Encountered a connection error during application startup caused by the "@" symbol in the local SQL Workbench password; resolved it using the `quote_plus` module from the `urllib.parse` package.

### 🔍 Assumptions Made

- Email comparison for duplicate checks is treated as case-insensitive.
- Work mode strictly accepts only `"WFH"` or `"WFO"`.
- Timestamps (`created_at`) are captured using Indian Standard Time (IST, UTC+5:30).
- Database schema and tables are provisioned manually via SQL Workbench for this stage, rather than through automated migration tooling.
