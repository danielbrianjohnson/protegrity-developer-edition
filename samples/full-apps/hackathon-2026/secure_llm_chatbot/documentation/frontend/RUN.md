---
# Running the Frontend

This document explains how to run the **Protegrity AI frontend** for local development.
---
## 1. Prerequisites

- Node.js and npm (or yarn) installed

Repo layout (simplified):

- `protegrity_ai/`
  - `backend/` – Django backend
  - `frontend/` – Frontend app (this folder)
  - `documentation/`
  - `venv/` – Python venv (only needed for backend)

---

## 2. Install Frontend Dependencies

From anywhere:

cd ~/Documents/webDev/protegrity_ai/frontend
First time (or whenever dependencies change):

npm install
or:

yarn
This installs all required packages defined in package.json.

---

## 3. Run the Frontend Dev Server

From `frontend/`:

cd ~/Documents/webDev/protegrity_ai/frontend
npm start
or:

yarn start
By default, the frontend dev server typically runs at:

- http://localhost:3000/

(If your project configuration specifies a different port, use that.)

To stop the dev server, press: Ctrl + C in that terminal.

You can run the frontend dev server in one terminal and the backend (Django) dev server in another.

---

## 4. Environment Variables (if used)

If your frontend relies on environment variables (for example, API URLs), they usually live in files such as:

- .env
- .env.development

Common example:

REACT_APP_API_BASE_URL=http://127.0.0.1:8000/
Consult the project README or your team for the exact variable names and values.

After changing environment variables, stop and restart npm start or yarn start.

---

## 5. Building for Production (optional)

To create a production build:

cd ~/Documents/webDev/protegrity_ai/frontend
npm run build
or:

yarn build
This produces an optimized build in the build/ directory.

---

## 6. Common Issues

### "command not found: npm" or "command not found: yarn"

- Install Node.js (which includes npm) and/or yarn, then retry:
  - For example, on macOS with Homebrew:

    brew install node
### Port already in use (3000)

If something else is running on port 3000:- Stop the other process (another dev server), or
- When prompted by npm start, allow it to run on another port (for example, 3001).


---

## 7. Quick TL;DR

From a fresh shell:

cd ~/Documents/webDev/protegrity_ai/frontend
npm install      # first time only (or after deps change)
npm start

---
