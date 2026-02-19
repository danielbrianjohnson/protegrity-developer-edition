# Protegrity AI - Architecture Overview

## What This Is

This is a conversational AI platform with enterprise-grade PII protection built in. Think ChatGPT, but every message gets scanned and scrubbed of sensitive data before it reaches the LLM.

## The Stack

**Backend:** Django 5.2.8 with Django REST Framework
- Handles all the business logic, data persistence, and orchestration
- Python 3.12 for modern language features
- SQLite for dev (easy to swap for Postgres in prod)

**Frontend:** React + Vite
- Fast, modern UI with hot module replacement
- Component-based architecture
- Real-time chat interface with file upload support

**Security Layer:** Protegrity Developer Edition
- Runs in Docker containers (ports 8580, 8581)
- Two main services: PII classification and semantic guardrails
- Industry-standard data protection

## How It Works

### The Flow of a Message

1. **User types a message** (or uploads a file)
   - Frontend: `ChatInput` component captures input
   - File uploads get validated (PDF, DOCX, TXT only, max 10MB)

2. **Message hits the backend** 
   - `POST /api/chat/` endpoint in `views.py`
   - If there's a file, `file_parser.py` extracts the text

3. **Protegrity scans everything**
   - `protegrity_service.py` sends text to classification API
   - Finds PII entities (SSN, credit cards, names, etc.)
   - Redacts or tokenizes based on mode

4. **Cleaned message goes to LLM**
   - Supports Azure OpenAI and AWS Bedrock
   - User never exposes sensitive data to the model
   - Response comes back, gets scanned again

5. **Frontend displays results**
   - Shows the conversation
   - Expandable "Protegrity Analysis" section
   - File attachments show scan results

## Key Components

### Backend Architecture

**`apps/core/models.py`** - The data models
- `Conversation` - Chat sessions with title, timestamps
- `Message` - Individual messages with role (user/assistant/system)
- `Attachment` - File metadata and extracted text
- `LLMProvider` - Configuration for different AI models
- `Agent` - Optional AI agents with specialized tools

**`apps/core/views.py`** - The API endpoints
- `/api/chat/` - Main chat endpoint, handles files and streaming
- `/api/conversations/` - CRUD for conversation history
- `/api/auth/token/` - JWT authentication
- `/api/health/` - Service health checks

**`apps/core/protegrity_service.py`** - Security integration
- `process_full_pipeline()` - Main function that scans text
- `classify_text()` - Finds PII entities
- `check_guardrails()` - Security policy checks
- Handles both input (user messages) and output (AI responses)

**`apps/core/file_parser.py`** - File processing
- Extracts text from PDFs (using pdfplumber)
- Extracts text from DOCX files (using python-docx)
- Plain text files pass through
- Custom error handling for corrupt files

### Frontend Architecture

**`src/App.jsx`** - The brain
- Manages all state (conversations, messages, loading states)
- Handles authentication
- Orchestrates API calls and polling
- Routes between welcome screen and chat

**`src/components/ChatInput/`** - Input interface
- Textarea with auto-resize
- File upload button (paperclip icon)
- Model & agent selection menu
- Real-time validation and error messages

**`src/components/ChatMessage/`** - Message display
- Renders user messages as plain text
- Renders AI messages as markdown
- Expandable Protegrity analysis section
- Shows file attachments with scan results

**`src/components/AttachmentDisplay/`** - File scan UI
- Shows file info (name, size, type)
- PII detection count
- Expandable detailed scan results
- Before/after redaction comparison

**`src/api/client.js`** - API communication
- Centralized API client with auth handling
- Automatic token refresh
- Error normalization
- FormData support for file uploads

## The File Upload Feature

This was recently added - here's how it works end-to-end:

1. User clicks paperclip → file dialog opens
2. Validation runs (type, size checks)
3. File preview shows with filename and size
4. User sends message
5. Frontend creates FormData with message + file
6. Backend extracts text from the file
7. Protegrity scans the extracted text
8. Scan results stored in database
9. Text combined with user's message
10. Everything sent to LLM together
11. Response includes attachment metadata
12. Frontend displays file with scan results

**Privacy Note:** We don't store the actual file binary - just the extracted text and scan results. Original file is discarded after extraction.

## Protegrity Integration

Two main APIs:

**Classification (port 8580)**
- `/pty/data-discovery/v1.1/classify`
- Detects PII entities with confidence scores
- Returns entity type, value, and position

**Guardrails (port 8581)**
- `/pty/semantic-guardrail/v1.1/conversations/messages/scan`
- Checks messages against security policies
- Returns risk scores (0-1)

**Three modes:**
- `redact` - Replaces PII with [REDACTED]
- `protect` - Tokenizes PII (reversible)
- `none` - Skip scanning (for testing)

## Database Schema

**Conversation**
- id (UUID), title, timestamps
- Links to: primary_agent, primary_llm, user

**Message**
- id (UUID), role, content
- protegrity_data (JSONField) - stores scan results
- Links to: conversation, agent, llm_provider

**Attachment**
- id, filename, file_type, file_size
- extracted_text (TextField)
- protegrity_scan (JSONField)
- Links to: message

## Authentication

JWT tokens with refresh mechanism:
- Login gets you access + refresh tokens
- Access token expires after 1 hour
- Refresh token good for 7 days
- Frontend stores in localStorage
- Auto-clears on 401 responses

## Error Handling

**Backend errors** return standardized format:
```json
{
  "error": {
    "code": "file_too_large",
    "message": "File exceeds 10MB limit"
  }
}
```

**Frontend shows:**
- Toast-style banners for file errors
- ErrorBanner component for API errors
- Loading spinners during async operations
- Disabled states to prevent double-submission

## What Makes This Different

Most chat apps just pipe your message straight to the LLM. This one:

1. **Scans everything first** - PII never reaches the model
2. **Handles files** - Upload documents and chat about them
3. **Multiple providers** - Switch between Azure and AWS
4. **Full audit trail** - Every scan stored in the database
5. **Role-based access** - Different users see different models/agents

## Development Workflow

Three services need to be running:

1. **Protegrity** - `docker compose up -d` (run from repo root)
2. **Backend** - `cd backend && python manage.py runserver`
3. **Frontend** - `cd frontend/console && npm run dev`

Default URLs:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Protegrity Classification: http://localhost:8580
- Protegrity Guardrails: http://localhost:8581

## Testing

Created a test file at `test_pii_sample.txt` with various PII types:
- Names, emails, phone numbers
- SSN, credit cards
- Addresses, account numbers

Upload this to verify the scanning works correctly.

## Next Steps / TODOs

- [ ] Add more file types (Excel, CSV)
- [ ] Implement conversation sharing
- [ ] Add export functionality
- [ ] Real-time streaming responses
- [ ] Conversation search/filtering
- [ ] Usage analytics dashboard
- [ ] Multi-language support
- [ ] Custom PII patterns

## Quick Reference

**Key Backend Files:**
- `apps/core/views.py:chat()` - Main chat endpoint (line ~180)
- `apps/core/protegrity_service.py` - All Protegrity integration
- `apps/core/file_parser.py` - File text extraction
- `apps/core/serializers.py` - API response formatting

**Key Frontend Files:**
- `src/App.jsx:handleSendMessage()` - Message submission (line ~240)
- `src/components/ChatInput/ChatInput.jsx` - Input UI
- `src/components/AttachmentDisplay/AttachmentDisplay.jsx` - File scans
- `src/api/client.js:sendChatMessage()` - API call (line ~136)

**Environment Variables:**
- Backend: Set in `backend/.env` or environment
- Frontend: `VITE_API_BASE_URL` for API endpoint
- Protegrity: Docker Compose manages service URLs

---

**TL;DR:** It's a chat app that scrubs PII before talking to AI, supports file uploads, and keeps a full audit trail of what got redacted.
