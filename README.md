# Employee Management API

A clean REST API built using **FastAPI** and **Pydantic**, managed with **uv**, to handle employee records in-memory.

---

## Setup & Running with `uv`

### Prerequisites

- Python 3.12
- `uv` installed on your machine

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Aravind-R5/employee-management-api.git
cd employee-management-api

# Create virtual environment and install dependencies
uv venv --python 3.12
uv pip install -r requirements.txt
```

### 2. Running the Server

```bash
# Run with hot-reload (development)
uv run uvicorn app.main:app --reload

# Run without hot-reload (production)
uv run uvicorn app.main:app --host [IP_ADDRESS] --port 8000
```
