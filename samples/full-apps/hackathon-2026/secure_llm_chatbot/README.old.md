# Protegrity AI Monorepo

This repository contains the **Protegrity AI** application, including:

- A **Django**-based backend
- A **React** frontend (JavaScript/TypeScript)
- Project-level documentation

Root directory (simplified):

- `backend/` – Django backend app (APIs, orchestration, DB access)
- `frontend/` – Frontend app (UI)
- `documentation/` – Additional architecture and design docs
- `arch.txt` – High-level architecture / scratch notes
- `venv/` – Python virtual environment (local only, not checked in)

Typical local path (yours):

- `~/Documents/webDev/protegrity_ai`

---

## 1. Prerequisites

### Backend

- Python 3.x
- `pip`
- (Recommended) virtual environment

### Frontend

- Node.js (with npm) installed
- Optionally `yarn`

---

## 2. Quick Start (Both Backend and Frontend)

From a **fresh terminal**:

1. Navigate to the repo:

   cd ~/Documents/webDev/protegrity_ai
2. (Backend) Activate virtualenv:

   source venv/bin/activate

   If you don’t have a `venv` yet:

   python3 -m venv venv
   source venv/bin/activate
3. (Backend) Install dependencies & run migrations:

   cd backend
   pip install -r requirements.txt
   python manage.py migrate
4. (Backend) Run the Django dev server:

   python manage.py runserver

   Backend will usually be at:

   - http://127.0.0.1:8000/
5. Open a **second terminal** for the frontend:

   cd ~/Documents/webDev/protegrity_ai/frontend
   npm install
   npm start

   Frontend will usually be at:

   - http://localhost:3000/

Now you have:

- Backend: listening on port 8000
- Frontend: listening on port 3000 and talking to the backend (via whatever API base URL is configured)

Press `Ctrl + C` in each terminal to stop the servers.

---

## 3. Repository Layout

High-level structure:

- `backend/`

  - `manage.py` – Django management entry point
  - `apps/` – Django apps (models, views, serializers, etc.)
  - `orchestrator/` – Orchestration layer for long-running / multi-step operations
  - `db.sqlite3` – Local SQLite database (dev only)
  - `pytest.ini` – Pytest configuration
  - `RUN.md` – How to run the backend locally
- `frontend/`

  - Frontend application source
  - `package.json` – Frontend dependencies and scripts
  - `RUN.md` – How to run the frontend locally
- `documentation/`

  - `backend/ARCHITECTURE.md` – High-level backend architecture and request flow
  - (Optionally more docs as the project grows)

---

## 4. Running Only the Backend

If you just want the backend:

cd ~/Documents/webDev/protegrity_ai
source venv/bin/activate
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
More detail lives in:

- `backend/RUN.md`

---

## 5. Running Only the Frontend

If you just want the frontend:

cd ~/Documents/webDev/protegrity_ai/frontend
npm install
npm start
More detail lives in:

- `frontend/RUN.md`

---

## 6. Environment Configuration

### Backend

Backend settings (DB, debug mode, secrets, etc.) are typically managed via:

- Django `settings.py` and/or
- Environment variables (for example via a `.env` file if you add one)

Common things you might configure:

- Database URL (for non-SQLite setups)
- Secret key
- Allowed hosts
- Any integration keys (OpenAI, internal services, etc.)

Check project-specific docs or settings modules for exact variable names.

### Frontend

If the frontend needs to know where the backend lives, it usually uses environment variables such as:

REACT_APP_API_BASE_URL=http://127.0.0.1:8000/
These are typically stored in:

- `.env`
- `.env.development`

If you change these, restart the frontend dev server (`npm start`).

---

## 7. Running Tests

### Backend tests

From the repo root with the virtualenv active:

cd ~/Documents/webDev/protegrity_ai
source venv/bin/activate
cd backend
Using Django’s test runner:

python manage.py test
Or, if pytest is set up (see `pytest.ini`):

pytest
### Frontend tests (if configured)

From the frontend directory:

cd ~/Documents/webDev/protegrity_ai/frontend
npm test
(or the test command defined in `package.json`).

---

## 8. Documentation

Key documentation files:

- Backend architecture:

  - `documentation/backend/ARCHITECTURE.md`
- Backend run instructions:

  - `backend/RUN.md`
- Frontend run instructions:

  - `frontend/RUN.md`

As the project grows, prefer adding more docs under `documentation/` (for example `documentation/frontend/`, `documentation/infra/`, etc.) and linking them here.

---

## 9. Common Issues / Tips

### Virtual environment not active

If you see “module not found” or similar when running `manage.py`:

- Make sure you are in the repo root and the venv is active:

  cd ~/Documents/webDev/protegrity_ai
  source venv/bin/activate
### Port conflicts- Backend port 8000 already in use:

  python manage.py runserver 8001

  - Frontend port 3000 already in use:

    - Stop other dev servers, or when prompted, allow React dev server to run on another port (for example 3001).
### Dependency mismatch

If things start failing after a change:- Backend:

  cd ~/Documents/webDev/protegrity_ai/backend
  pip install -r requirements.txt

  - Frontend:

    cd ~/Documents/webDev/protegrity_ai/frontend
    npm install
  ---

  ## 10. TL;DR for Local Dev

  Backend + frontend, from a clean shell:

  cd ~/Documents/webDev/protegrity_ai
  source venv/bin/activate
  cd backend
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver   # window/tab 1
  Open a new terminal:

  cd ~/Documents/webDev/protegrity_ai/frontend
  npm install
  npm start                    # window/tab 2
  You’re now up with backend on `127.0.0.1:8000` and frontend on `localhost:3000`.

  List project tree:

  cd ~/Documents/webDev/protegrity_ai

  brew install tree (if not installed)

  tree -a -I '.git|.venv|venv|node_modules|__pycache__|.mypy_cache|.pytest_cache|.DS_Store|*.pyc|.env*'
