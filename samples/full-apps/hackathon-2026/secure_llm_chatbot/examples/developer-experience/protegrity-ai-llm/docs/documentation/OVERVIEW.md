# Protegrity AI Chat System - Overview

## System Architecture

### Backend (Django/DRF)

**Core Components:**
- **Django REST Framework**: RESTful API endpoints with JWT authentication
- **Chat Orchestrator**: Central coordination layer managing the complete chat flow
- **Provider Abstraction**: Unified interface for multiple LLM providers (Fin AI, Bedrock, OpenAI)
- **Protegrity Integration**: Input/output protection with PII detection, redaction, and semantic guardrails
- **RBAC System**: Role-based access control with PROTEGRITY and STANDARD user roles
- **Tool Router**: Extensible system for LLM tool calls (Protegrity redact/unprotect)

**Key Features:**
- Standardized error responses: `{"error": {"code": "...", "message": "..."}}`
- API key authentication with secure hashing and prefix-based lookup
- Conversation management with soft deletes
- Message tracking with agent/LLM metadata
- Protegrity data preservation for audit and compliance

### Frontend (React/Vite)

**Architecture:**
- **React 18**: Modern component-based UI
- **Vite**: Fast development and optimized production builds
- **Centralized API Client**: Single source for all backend communication
- **JWT Authentication**: Token-based auth with refresh mechanism
- **Error Handling**: Consistent error display from standardized backend responses

**Key Features:**
- Real-time chat interface with streaming support
- Conversation history sidebar
- Model and agent selection
- Protegrity analysis display
- Responsive design

## Security Posture

### Authentication & Authorization

**Web Users (JWT):**
- Secure JWT tokens with refresh mechanism
- HttpOnly cookies for token storage
- Session-based authentication via Django

**API Users (API Keys):**
- Hashed keys (never stored in plaintext)
- Prefix-based lookup for performance
- Expiration and audit tracking
- Keys inherit user's role and permissions

### Role-Based Access Control (RBAC)

**PROTEGRITY Role:**
- Full access to all active resources
- Can use all LLM providers, agents, and tools
- Admin-level permissions
- Default min_role for all new resources

**STANDARD Role:**
- Limited access to resources marked with `min_role="STANDARD"`
- Designed for Fin AI access only
- No access to agents or advanced tools
- Default role for new users

**Implementation:**
- Resource-level gating via `min_role` field on LLMProvider, Agent, Tool
- Filtering applied in `permissions.filter_by_role()`
- Access checks in `permissions.check_resource_access()`
- Fail-closed design (unknown roles = no access)

### Data Protection (Protegrity)

**Input Protection:**
- PII detection and redaction before sending to LLM
- Semantic guardrails for policy violations
- Blocked inputs never reach LLM
- Protected text sent to LLM (not original)

**Output Protection:**
- PII detection in LLM responses
- Redaction of sensitive data
- Guardrail checks for policy violations
- Blocked outputs replaced with safe message

**Data Preservation:**
- Original and processed text stored in `protegrity_data` field
- Audit trail for compliance
- Structure: `{"input_processing": {...}, "output_processing": {...}}`

## API Structure

### Error Format

All errors return consistent structure:
```json
{
  "error": {
    "code": "machine_friendly_code",
    "message": "Human readable message"
  }
}
```

Common error codes:
- `message_required`: Missing required field
- `forbidden_model`: Insufficient permissions
- `invalid_model`: Model not found
- `conversation_not_found`: Resource not found
- `no_llm_provider`: Configuration error

### Key Endpoints

**Chat:**
- `POST /api/chat/` - Send message, get response
- `GET /api/chat/poll/{conversation_id}/` - Poll for async responses

**Conversations:**
- `GET /api/conversations/` - List conversations (paginated)
- `POST /api/conversations/` - Create conversation
- `GET /api/conversations/{id}/` - Get conversation with messages
- `PATCH /api/conversations/{id}/` - Update conversation
- `DELETE /api/conversations/{id}/` - Soft delete conversation

**Resources:**
- `GET /api/models/` - List available LLM providers (role-filtered)
- `GET /api/agents/` - List available agents (role-filtered)
- `GET /api/tools/` - List available tools (role-filtered)

**Health:**
- `GET /api/health/` - Health check (public, no auth)

## Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend/console
npm install
npm run dev
```

**Tests:**
```bash
cd backend
pytest apps/core/tests/
```

## Documentation Structure

- `/documentation/OVERVIEW.md` - This file (system overview)
- `/documentation/backend/` - Backend-specific documentation
  - `ARCHITECTURE.md` - Detailed backend architecture
  - `AUTH_AND_PERMISSIONS.md` - RBAC implementation guide
  - `API_KEYS.md` - API key management and usage
  - `PROTEGRITY_INPUT_OUTPUT_PROTECTION.md` - Protegrity integration details
  - `CHAT_ORCHESTRATOR_AND_TOOL_ROUTING.md` - Orchestrator flow
  - `PROVIDER_ABSTRACTION.md` - LLM provider system
  - `API_DOCUMENTATION.md` - Complete API reference
- `/documentation/frontend/` - Frontend-specific documentation
  - `RUN.md` - Frontend setup and development
  - `FRONTEND_AGENT_MODEL_INTEGRATION.md` - Agent/model UI integration

## Design Principles

1. **Security First**: Fail closed, explicit permissions, no plaintext secrets
2. **Simplicity**: No magic, clear patterns, obvious behavior
3. **Auditability**: Comprehensive logging and data preservation
4. **Maintainability**: Standard patterns, good documentation, consistent style
5. **Testability**: 106+ tests covering core functionality
6. **Type Safety**: Type hints on critical paths
7. **Error Clarity**: Consistent error format with codes and messages

## Terminology Consistency

- **PROTEGRITY** (all caps): User role name
- **STANDARD** (all caps): User role name
- **min_role**: Field name on resources controlling access
- **API key**: Authentication mechanism (not "api-key" or "ApiKey")
- **LLM provider**: System that provides LLM access (not "model" or "provider" alone)
- **Agent**: AI assistant configuration with system prompt and tools
- **Tool**: Callable function LLM can request (e.g., Protegrity redact)
- **Conversation**: Chat session with messages
- **Message**: Single turn in conversation (user or assistant)
