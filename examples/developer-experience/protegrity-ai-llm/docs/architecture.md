# Protegrity AI (LLM) Architecture

## Overview

This example is a secure chat application that applies Protegrity checks before and after LLM calls.

- **Frontend:** React + Vite
- **Backend:** Django + DRF
- **Security services:** Protegrity Developer Edition (classification + guardrails)

## Request Flow

1. User sends a prompt from the frontend.
2. Backend runs Protegrity input processing (guardrails + PII detection/redaction).
3. Sanitized prompt is sent to the configured LLM provider.
4. Backend runs Protegrity output processing on the model response.
5. Safe response (plus analysis metadata) is returned to the frontend.

## Main Components

### Backend

- `app/backend/apps/core/views.py`: API endpoints (`/api/chat/`, `/api/conversations/`, auth/health).
- `app/backend/apps/core/protegrity_service.py`: Protegrity pipeline integration.
- `app/backend/apps/core/models.py`: Conversation/message/provider/agent/tool models.
- `app/backend/apps/core/orchestrator.py`: Chat orchestration and tool routing flow.

### Frontend

- `app/frontend/console/src/App.jsx`: application state and API orchestration.
- `app/frontend/console/src/api/client.js`: API client and auth helpers.
- `app/frontend/console/src/components/`: chat, sidebar, auth, and settings UI.

## Runtime Topology

- Frontend dev server: `http://localhost:5173`
- Backend API: `http://127.0.0.1:8000`
- Protegrity services (via repo-root Docker Compose): ports `8580` and `8581`

## Data Handling Notes

- Sensitive input is scanned/redacted before LLM submission.
- Model output is scanned/redacted before UI rendering.
- Protegrity processing metadata is stored with messages for explainability/audit.
