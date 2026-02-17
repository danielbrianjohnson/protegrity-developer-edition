# Protegrity AI - 60 Second Overview

## What Is This?

A ChatGPT-style interface that automatically scrubs PII from every message before it reaches the AI. Built for enterprises that need to use LLMs without leaking sensitive data.

## The Stack (3 moving parts)

1. **Django Backend** - Orchestrates everything, stores conversations
2. **React Frontend** - Chat UI with file upload support  
3. **Protegrity Services** - Docker containers that scan for PII

## How a Message Flows

```
User types → Protegrity scans → Redacts PII → Sends to LLM → Scans response → Shows user
```

For file uploads (PDF/DOCX/TXT):
```
Upload → Extract text → Scan → Combine with message → Send to LLM
```

## Key Features

✅ **PII Detection** - SSN, credit cards, emails, names, addresses
✅ **File Uploads** - Chat about documents (scans them too)
✅ **Multi-Provider** - Works with Azure OpenAI and AWS Bedrock
✅ **Full Audit** - Every scan saved in the database
✅ **Smart UI** - Shows exactly what got redacted and why

## Code Layout

**Backend** (`backend/apps/core/`)
- `views.py` - API endpoints (/api/chat/, /api/conversations/)
- `protegrity_service.py` - Talks to Protegrity containers
- `file_parser.py` - Extracts text from uploaded files
- `models.py` - Database schema (Conversations, Messages, Attachments)

**Frontend** (`frontend/console/src/`)
- `App.jsx` - Main state management
- `components/ChatInput/` - Message input + file upload
- `components/ChatMessage/` - Message display + PII analysis
- `components/AttachmentDisplay/` - File scan results

## Running It

```bash
# Start Protegrity (Docker, from repo root)
docker compose up -d

# Start backend
cd backend && python manage.py runserver

# Start frontend  
cd frontend/console && npm run dev
```

Visit: http://localhost:5173

## The Magic Happens Here

**Backend:** `views.py:chat()` function - takes message/file, scans with Protegrity, sends to LLM
**Frontend:** `App.jsx:handleSendMessage()` - creates FormData, uploads file, handles response

## Privacy Win

Original files never stored - just extracted text and scan results. PII gets redacted before touching the LLM. Everything audited.

## Recent Addition

Just added file upload feature. Upload a PDF with sensitive data → system extracts text → scans for PII → redacts it → sends clean version to AI → shows you what was found.

Test it with `test_pii_sample.txt` in the root directory.

---

**Bottom line:** Chat with AI, upload files, never leak PII. All the good stuff happens in `protegrity_service.py` and gets displayed in `ChatMessage.jsx`.
