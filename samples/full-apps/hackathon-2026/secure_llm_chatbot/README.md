# Secure LLM Chatbot (Sample App)

Lightweight sample app for testing secure LLM chat workflows with Protegrity scanning/redaction.

## What this sample includes

- Django backend with chat + conversation APIs
- React frontend chat UI
- Protegrity guardrail and classification integration
- Vendor-neutral LLM provider config via `backend/.env`

## Quick start

1. Create env file:

```bash
cp backend/.env.example backend/.env
```

2. Configure one provider in `backend/.env` (Azure OpenAI is the fastest path).

3. Run the app:

```bash
./run.sh
```

4. Open:

- Frontend: `http://localhost:5173`
- Backend: `http://127.0.0.1:8000`

5. Stop:

```bash
./stop.sh
```

## Important notes

- Use `./run.sh` (not `./run`).
- The only runtime env file is `backend/.env`.
- Startup auto-validates providers and syncs active models from env.
- For Azure-only setups, use `AZURE_OPENAI_DEPLOYMENTS` to limit visible models.

## Minimal structure

```text
secure_llm_chatbot/
├── backend/
│   ├── .env.example
│   └── apps/core/
├── frontend/console/
├── documentation/
├── run.sh
└── stop.sh
```

## Additional docs

- [documentation/OVERVIEW.md](documentation/OVERVIEW.md)
- [documentation/backend/RUN.md](documentation/backend/RUN.md)
- [documentation/frontend/RUN.md](documentation/frontend/RUN.md)
