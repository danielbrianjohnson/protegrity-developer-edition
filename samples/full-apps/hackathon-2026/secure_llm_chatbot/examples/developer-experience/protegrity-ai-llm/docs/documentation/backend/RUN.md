# Running the Backend

This document explains how to run the **Protegrity AI backend** for local development.

---

## 1. Prerequisites

- Python 3.x installed
- (Recommended) virtual environment for Python

Repo layout (simplified):

- `protegrity_ai/`
  - `backend/` – Django backend (this folder)
  - `frontend/` – Frontend app
  - `documentation/`
  - `venv/` – Python virtual environment (optional but recommended)

---

## 2. Activate Virtual Environment

From the repo root:

cd ~/Documents/webDev/protegrity_ai
If you already have a `venv/`:

source venv/bin/activate
If you don’t have one yet (one-time setup):

python3 -m venv venv
source venv/bin/activate
---

## 3. Install Backend Dependencies

From the repo root or inside `backend/` (depending on where `requirements.txt` lives):

cd ~/Documents/webDev/protegrity_ai/backend
pip install -r requirements.txt
---

## 4. Apply Database Migrations

Make sure your virtual environment is activated.

From `backend/`:

cd ~/Documents/webDev/protegrity_ai/backend
Create migrations (if you’ve changed models):

python manage.py makemigrations
Apply migrations:

python manage.py migrate
---

## 5. Run the Development Server

From `backend/`:

cd ~/Documents/webDev/protegrity_ai/backend
python manage.py runserver
By default, the backend will be available at:

- http://127.0.0.1:8000/

To stop the server, press: Ctrl + C in that terminal.

---

## 6. Running Tests

Make sure you are in the `backend/` directory with the virtual environment active:

cd ~/Documents/webDev/protegrity_ai/backend
Run tests with Django’s test runner:

python manage.py test
Or, if the project uses pytest:

pytest
(Check `pytest.ini` and your team’s conventions to confirm.)

---

## 7. Common Issues

### Virtualenv not activated

If you get “module not found” or similar errors:

- Ensure you ran:

  source ~/Documents/webDev/protegrity_ai/venv/bin/activate
before running manage.py commands.

### Port already in use (8000)

If something else is running on port 8000:- Stop the other process, or
- Run the server on a different port, for example:

  python manage.py runserver 8001
---

## 8. Quick TL;DR

From a fresh shell:

cd ~/Documents/webDev/protegrity_ai
source venv/bin/activate
cd backend
pip install -r requirements.txt   # first time only (or after deps change)
python manage.py migrate
python manage.py runserver
