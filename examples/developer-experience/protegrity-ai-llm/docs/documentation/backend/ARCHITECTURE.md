cd ~/Documents/webDev/protegrity_ai/documentation/backend

cat << 'EOF' > ARCHITECTURE.md
# Backend Architecture

This document describes the high-level architecture of the **Protegrity AI Backend**.

## 1. Overview

The backend is a **Django** application that exposes APIs to the frontend and orchestrates background processes.

**Repo layout (backend-related):**

- `backend/`
  - `manage.py` – Django management entrypoint
  - `apps/` – Django apps (business logic, models, views, serializers, etc.)
  - `orchestrator/` – Orchestration logic (tasks, pipelines, integrations)  
  - `db.sqlite3` – Local development database (SQLite)
  - `pytest.ini` – Pytest configuration

> Note: This is the **runtime** backend. Documentation lives under `documentation/backend/`.

## 2. Runtime Architecture

At a high level, the backend consists of:

1. **Django Web Layer**
   - URL routing and views / DRF viewsets
   - Authentication and permissions
   - Validation and error handling

2. **Business Logic Layer**
   - Implemented inside `apps/` as services, managers, and model methods.
   - Responsible for enforcing domain rules (e.g., project ownership, quotas, etc.).

3. **Orchestration Layer (`orchestrator/`)**
   - Coordinates longer-running or multi-step operations.
   - Typical responsibilities:
     - Calling external APIs or services
     - Chaining multiple operations
     - Handling retries and error states

4. **Persistence Layer**
   - Django ORM on top of SQLite (dev) / Postgres (prod, planned).
   - Models defined in `apps/*/models.py`.
   - Migrations managed via `python manage.py makemigrations` and `python manage.py migrate`.

## 3. Request Flow (High Level)

1. **Client** (frontend or external caller) sends HTTP request to the backend.
2. **Django URL router** matches the URL to a view/viewset.
3. The **view**:
   - Authenticates the user
   - Validates input
   - Delegates to business logic or orchestrator services
4. **Business/Orchestrator logic**:
   - Reads and writes data via Django models.
   - Optionally calls external services.
5. **Response** is serialized to JSON and returned to the client.

```mermaid
sequenceDiagram
    participant C as Client
    participant B as Backend (Django)
    participant S as Services / Orchestrator
    participant DB as Database

    C->>B: HTTP Request (JSON)
    B->>S: Call service/orchestrator
    S->>DB: Query / Update data
    DB-->>S: Results
    S-->>B: Domain result
    B-->>C: HTTP Response (JSON)
