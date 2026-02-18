# REST API Documentation

## Base URL

```
http://localhost:8000/api
```

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/conversations/` | List all active conversations |
| POST | `/conversations/` | Create new conversation |
| GET | `/conversations/{id}/` | Get conversation with messages |
| PATCH | `/conversations/{id}/` | Update conversation |
| DELETE | `/conversations/{id}/` | Soft delete conversation |
| POST | `/conversations/{id}/messages/` | Add message to conversation |
| POST | `/chat/` | Send message (creates conversation + messages) |
| GET | `/chat/poll/{id}/` | Poll for async LLM response |
| GET | `/models/` | List available LLM models |
| GET | `/agents/` | List available AI agents |
| GET | `/tools/` | List available tools |
| GET | `/health/` | Health check |

---

## Conversations

### List Conversations

```http
GET /api/conversations/
```

**Query Parameters**:
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Results per page (default: 50, max: 100)

**Response**: 200 OK
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/conversations/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "How to protect PII data?",
      "model_id": "fin",
      "message_count": 8,
      "created_at": "2025-12-10T10:30:00Z",
      "updated_at": "2025-12-10T10:45:00Z"
    }
  ]
}
```

---

### Create Conversation

```http
POST /api/conversations/
```

**Request Body**:
```json
{
  "title": "New chat",  // optional, defaults to "New chat"
  "model_id": "fin"     // required: "fin" | "bedrock-claude"
}
```

**Response**: 201 Created
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "New chat",
  "model_id": "fin",
  "messages": [],
  "created_at": "2025-12-10T10:30:00Z",
  "updated_at": "2025-12-10T10:30:00Z"
}
```

**Errors**:
- `400`: Invalid model_id
- `500`: Database error

---

### Get Conversation

```http
GET /api/conversations/{id}/
```

**Response**: 200 OK
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "How to protect PII data?",
  "model_id": "fin",
  "messages": [
    {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "role": "user",
      "content": "How do I protect PII data?",
      "protegrity_data": {
        "input_processing": {
          "pii_detected": ["email"],
          "redacted_count": 0
        }
      },
      "pending": false,
      "blocked": false,
      "created_at": "2025-12-10T10:30:15Z"
    },
    {
      "id": "650e8400-e29b-41d4-a716-446655440002",
      "role": "assistant",
      "content": "To protect PII data, you should...",
      "pending": false,
      "blocked": false,
      "created_at": "2025-12-10T10:30:20Z"
    }
  ],
  "created_at": "2025-12-10T10:30:00Z",
  "updated_at": "2025-12-10T10:30:20Z"
}
```

**Errors**:
- `404`: Conversation not found or deleted

---

### Update Conversation

```http
PATCH /api/conversations/{id}/
```

**Request Body** (partial update):
```json
{
  "title": "Updated conversation title"
}
```

**Response**: 200 OK (same as GET response)

**Errors**:
- `404`: Conversation not found
- `400`: Invalid data

---

### Delete Conversation

```http
DELETE /api/conversations/{id}/
```

**Response**: 204 No Content

**Note**: This performs a soft delete. The conversation and all its messages are marked with `deleted_at` timestamp but remain in the database.

**Errors**:
- `404`: Conversation not found

---

## Messages

### Add Message to Conversation

```http
POST /api/conversations/{id}/messages/
```

**Note**: This endpoint is primarily for internal use. The `/chat/` endpoint handles message creation with LLM integration.

**Request Body**:
```json
{
  "role": "user",          // "user" | "assistant" | "system"
  "content": "Message text",
  "protegrity_data": {},   // optional
  "pending": false,        // optional
  "blocked": false         // optional
}
```

**Response**: 201 Created
```json
{
  "id": "750e8400-e29b-41d4-a716-446655440003",
  "role": "user",
  "content": "Message text",
  "pending": false,
  "blocked": false,
  "created_at": "2025-12-10T10:31:00Z"
}
```

**Errors**:
- `404`: Conversation not found
- `400`: Invalid data

---

## Chat (Legacy/Integrated Endpoint)

### Send Chat Message

```http
POST /api/chat/
```

**Request Body**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",  // optional, creates new if omitted
  "message": "What is data protection?",
  "model_id": "fin",                                          // optional, defaults to "fin"
  "protegrity_mode": "redact"                                 // optional: "redact" | "protect" | "none"
}
```

**Response Scenarios**:

#### 1. Blocked by Guardrails (200 OK)
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "blocked",
  "messages": [
    {
      "role": "user",
      "content": "Original message with PII"
    },
    {
      "role": "system",
      "content": "This prompt was blocked by security guardrails due to policy violations.",
      "blocked": true
    }
  ],
  "protegrity_data": {
    "input_processing": {
      "should_block": true,
      "guardrails": { /* ... */ }
    },
    "output_processing": null
  }
}
```

#### 2. Pending (Async - Fin AI) (200 OK)
```json
{
  "conversation_id": "215472210402122",
  "status": "pending",
  "messages": [
    {
      "role": "user",
      "content": "What is data protection?"
    },
    {
      "role": "assistant",
      "content": "response pending",
      "pending": true
    }
  ],
  "protegrity_data": {
    "input_processing": { /* ... */ },
    "output_processing": null
  }
}
```

**Follow-up**: Poll `/api/chat/poll/{conversation_id}/` for response

#### 3. Completed (Immediate - Bedrock) (200 OK)
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "messages": [
    {
      "role": "user",
      "content": "What is data protection?"
    },
    {
      "role": "assistant",
      "content": "Data protection involves securing sensitive information..."
    }
  ],
  "protegrity_data": {
    "input_processing": { /* ... */ },
    "output_processing": { /* ... */ }
  }
}
```

**Errors**:
- `400`: Missing message or invalid data
- `500`: LLM API error

---

### Poll for Response

```http
GET /api/chat/poll/{conversation_id}/
```

**Response - Still Pending**: 200 OK
```json
{
  "status": "pending"
}
```

**Response - Completed**: 200 OK
```json
{
  "status": "completed",
  "response": "Data protection involves securing sensitive information...",
  "protegrity_output": {
    "processed_text": "...",
    "pii_detected": []
  }
}
```

**Errors**:
- `404`: Conversation not found

---

## Models

### List Available Models

```http
GET /api/models/
```

**Response**: 200 OK
```json
{
  "models": [
    {
      "id": "fin",
      "name": "Fin AI",
      "description": "Intercom Fin AI with knowledge base",
      "provider": "intercom",
      "requires_polling": true,
      "supports_streaming": false,
      "max_tokens": 4096
    },
    {
      "id": "bedrock-claude",
      "name": "Claude 3.5 Sonnet",
      "description": "Amazon Bedrock - Anthropic Claude",
      "provider": "bedrock",
      "requires_polling": false,
      "supports_streaming": true,
      "max_tokens": 8192
    }
  ]
}
```

---

### List Available Agents

```http
GET /api/agents/
```

**Response**: 200 OK
```json
{
  "agents": [
    {
      "id": "data-protection-expert",
      "name": "Data Protection Expert",
      "description": "Specialized in data privacy, PII protection, and compliance",
      "default_llm": "fin",
      "icon": "shield",
      "color": "#FA5A25",
      "system_prompt": "You are a data protection expert..."
    },
    {
      "id": "general-assistant",
      "name": "General Assistant",
      "description": "Helpful AI assistant for general queries",
      "default_llm": "bedrock-claude",
      "icon": "chat",
      "color": "#4F46E5",
      "system_prompt": "You are a helpful, friendly AI assistant..."
    }
  ]
}
```

---

### List Available Tools

```http
GET /api/tools/
```

**Response**: 200 OK
```json
{
  "tools": [
    {
      "id": "protegrity-redact",
      "name": "Protegrity Data Redaction",
      "tool_type": "protegrity",
      "description": "Redacts sensitive PII data using Protegrity guardrails",
      "requires_auth": true,
      "function_schema": {
        "name": "redact_pii",
        "description": "Redact personally identifiable information from text",
        "parameters": {
          "type": "object",
          "properties": {
            "text": {
              "type": "string",
              "description": "Text to scan for PII"
            }
          }
        }
      }
    }
  ]
}
```

---

## Health Check

### System Health

```http
GET /api/health/
```

**Response**: 200 OK
```json
{
  "status": "ok"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request (validation error)
- `404`: Not Found
- `405`: Method Not Allowed
- `500`: Internal Server Error

---

## Data Types

### Conversation Object

```typescript
{
  id: string (UUID),
  title: string,
  model_id: string,
  message_count?: number,      // Only in list view
  messages?: Message[],        // Only in detail view
  created_at: string (ISO 8601),
  updated_at: string (ISO 8601)
}
```

### Message Object

```typescript
{
  id: string (UUID),
  role: "user" | "assistant" | "system",
  content: string,
  protegrity_data?: object,
  pending: boolean,
  blocked: boolean,
  created_at: string (ISO 8601)
}
```

---

## Rate Limiting

**Current**: No rate limiting implemented

**Recommended for Production**:
- 100 requests per minute per IP
- 1000 conversations per hour per user
- Use Django Ratelimit or API Gateway throttling

---

## Authentication

**Current**: No authentication required (development)

**Production Implementation**:
1. Add User model
2. JWT tokens or session auth
3. User-based conversation filtering
4. Per-user rate limits

---

## CORS

**Allowed Origins** (development):
- `http://localhost:5173` (Vite dev server)

**Production**: Configure allowed origins in settings.py

---

## Examples

### Full Conversation Flow

```bash
# 1. Create conversation
curl -X POST http://localhost:8000/api/conversations/ \
  -H "Content-Type: application/json" \
  -d '{"model_id": "fin"}'

# Response: {"id": "550e8400...", ...}

# 2. Send message
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "550e8400...",
    "message": "Hello",
    "model_id": "fin"
  }'

# Response: {"status": "pending", "conversation_id": "215472..."}

# 3. Poll for response
curl http://localhost:8000/api/chat/poll/215472.../

# Response: {"status": "completed", "response": "..."}

# 4. Get full conversation
curl http://localhost:8000/api/conversations/550e8400.../

# Response: Full conversation with all messages
```

---

## Changelog

- **v1.0** (2025-12-10): Initial API implementation
