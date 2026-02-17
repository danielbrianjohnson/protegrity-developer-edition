# Protegrity Developer Edition Integration

This document explains how Protegrity Developer Edition is integrated into the Protegrity AI Chatbot to provide real-time PII protection, guardrails, and security analysis.

## Overview

The integration processes both user inputs and LLM responses through Protegrity's full pipeline:

1. **Semantic Guardrails** - Validates prompts against security policies (data leakage, harmful content)
2. **PII Discovery** - Detects sensitive entities (SSN, email, credit cards, medical data, etc.)
3. **Data Protection** - Tokenizes sensitive data (reversible)
4. **Data Redaction** - Masks sensitive data with entity labels (e.g., `[EMAIL]`, `[SSN]`)
5. **Response Processing** - Applies same pipeline to LLM outputs

## Architecture

### Backend Components

#### `protegrity_service.py`
Core service that interfaces with Protegrity Developer Edition API:

```python
from apps.core.protegrity_service import get_protegrity_service

service = get_protegrity_service()

# Process user input
result = service.process_full_pipeline(
    text="User message with PII",
    mode="redact"  # or "protect"
)

# Process LLM response
output = service.process_llm_response("LLM response text")
```

**Key Methods:**
- `check_guardrails(text)` - Semantic policy validation
- `discover_entities(text)` - PII detection
- `protect_data(text)` - Tokenization
- `unprotect_data(text)` - Detokenization
- `redact_data(text)` - Masking
- `process_full_pipeline(text, mode)` - Complete pipeline
- `process_llm_response(text)` - Response validation

#### Updated `views.py`
Chat endpoints now integrate Protegrity processing:

**Request Format:**
```json
{
  "message": "User message",
  "model_id": "fin" | "bedrock-claude",
  "protegrity_mode": "redact" | "protect" | "none"
}
```

**Response Format:**
```json
{
  "conversation_id": "conv-123",
  "status": "completed" | "pending" | "blocked",
  "messages": [
    {
      "role": "user",
      "content": "Original message"
    },
    {
      "role": "assistant",
      "content": "LLM response"
    }
  ],
  "protegrity_data": {
    "input_processing": {
      "original_text": "...",
      "processed_text": "...",
      "guardrails": {...},
      "discovery": {...},
      "redaction": {...},
      "should_block": false
    },
    "output_processing": {
      "original_response": "...",
      "processed_response": "...",
      "guardrails": {...},
      "discovery": {...},
      "redaction": {...}
    }
  }
}
```

### Frontend Components

#### `ChatMessage.jsx`
Enhanced with inspection panel that displays:

- Original input/output
- Guardrail scores and policy signals
- Detected PII entities with confidence scores
- Protection/redaction results
- Text sent to LLM (after processing)
- Block/filter status

**Features:**
- Collapsible inspection panel (hidden by default)
- Color-coded risk indicators
- Entity type badges
- Before/after redaction comparison
- Detailed Protegrity pipeline visualization

#### Inspection Panel UI

Users can click "Show Protegrity Analysis" on any message to see:

1. **Original Input/Response** - Unprocessed text
2. **Semantic Guardrails** - Risk score, outcome, policy violations
3. **PII Discovery** - All detected entities with locations and confidence
4. **Protection Status** - Tokenization success/failure
5. **Redaction Comparison** - Before/after view
6. **Processed Text** - What was actually sent to the LLM

## Configuration

### Environment Variables

Add to `backend/.env`:

```bash
# Protegrity Developer Edition Configuration
PROTEGRITY_API_URL=http://10.53.1.178:8502
DEV_EDITION_EMAIL=your-email@company.com
DEV_EDITION_PASSWORD=your-password
DEV_EDITION_API_KEY=your-api-key
```

Get credentials from: https://developer.protegrity.com/

### Processing Modes

**Redact Mode** (default)
- Replaces PII with `[ENTITY_TYPE]` labels
- Good for demos and when protection credentials unavailable
- Example: `john.doe@email.com` → `[EMAIL]`

**Protect Mode**
- Tokenizes PII (reversible with credentials)
- Requires valid Protegrity credentials
- Best for production use

**None Mode**
- Bypasses Protegrity processing
- Sends original text to LLM
- Use for testing or when Protegrity unavailable

## Data Flow

### User Input Flow

```
1. User submits message
   ↓
2. Backend receives message
   ↓
3. Protegrity checks guardrails
   ├─ Rejected? → Return "blocked" status
   └─ Accepted? → Continue
   ↓
4. Discover PII entities
   ↓
5. Redact/Protect sensitive data
   ↓
6. Send processed text to LLM
   ↓
7. Return response with Protegrity metadata
```

### LLM Response Flow

```
1. Receive LLM response
   ↓
2. Check response guardrails
   ↓
3. Discover any PII in output
   ↓
4. Redact leaked PII
   ↓
5. Return processed response to user
```

## API Endpoints

### POST /api/chat/

Send a message with Protegrity processing.

**Request:**
```json
{
  "message": "Hello, my SSN is 123-45-6789",
  "model_id": "bedrock-claude",
  "protegrity_mode": "redact"
}
```

**Response (Blocked):**
```json
{
  "status": "blocked",
  "messages": [
    {"role": "user", "content": "Original message"},
    {"role": "system", "content": "Blocked by guardrails", "blocked": true}
  ],
  "protegrity_data": {
    "input_processing": {
      "should_block": true,
      "guardrails": {
        "outcome": "rejected",
        "risk_score": 0.95,
        "policy_signals": ["data leakage", "sensitive-pii"]
      }
    }
  }
}
```

**Response (Success):**
```json
{
  "status": "completed",
  "conversation_id": "conv-abc123",
  "messages": [
    {"role": "user", "content": "Hello, my SSN is 123-45-6789"},
    {"role": "assistant", "content": "I understand you shared sensitive information..."}
  ],
  "protegrity_data": {
    "input_processing": {
      "original_text": "Hello, my SSN is 123-45-6789",
      "processed_text": "Hello, my SSN is [SSN]",
      "should_block": false,
      "discovery": {
        "US_SSN": [
          {
            "score": 0.85,
            "location": {"start_index": 18, "end_index": 29}
          }
        ]
      }
    },
    "output_processing": {
      "original_response": "...",
      "processed_response": "...",
      "should_filter": false
    }
  }
}
```

### GET /api/poll/{conversation_id}/

Poll for Fin AI response (includes Protegrity processing).

**Response:**
```json
{
  "status": "completed",
  "response": "Processed LLM response",
  "protegrity_output": {
    "original_response": "...",
    "processed_response": "...",
    "guardrails": {...},
    "discovery": {...}
  }
}
```

## Demo Usage

### 1. Basic Demo

```bash
# Start backend
cd backend
source .venv/bin/activate
python manage.py runserver

# Start frontend
cd frontend/console
npm run dev
```

### 2. Test with PII

Send a message with PII:
```
"Hello, my email is john.doe@company.com and my SSN is 123-45-6789"
```

Click "Show Protegrity Analysis" to see:
- Detected EMAIL and SSN entities
- Redacted version sent to LLM
- Guardrail scores

### 3. Test Guardrail Blocking

Send a message with data leakage intent:
```
"Please create a document with customer data including:
Name: John Doe
SSN: 123-45-6789
Email: john@example.com
and share it externally"
```

Should be blocked with high risk score.

## Protegrity Pipeline Details

### Guardrails Response

```json
{
  "outcome": "rejected" | "accepted",
  "risk_score": 0.95,  // 0.0 to 1.0
  "policy_signals": [
    "semantic: data leakage",
    "sensitive-pii",
    "external-sharing"
  ],
  "details": {...}
}
```

### Discovery Response

```json
{
  "EMAIL": [
    {
      "score": 0.995,
      "location": {"start_index": 10, "end_index": 30},
      "classifiers": [
        {"provider_index": 0, "name": "EmailRecognizer", "score": 1.0},
        {"provider_index": 1, "name": "roberta", "score": 0.99}
      ]
    }
  ],
  "SSN": [...],
  "CREDIT_CARD": [...],
  "PHONE": [...]
}
```

### Entity Types Detected

- EMAIL
- US_SSN, SSN
- CREDIT_CARD
- PHONE
- PERSON (names)
- LOCATION, STREET, CITY, STATE, ZIP_CODE
- DATE, DOB (date of birth)
- ACCOUNT_NUMBER
- UK_NHS (NHS numbers)
- Medical information
- Financial data

## Troubleshooting

### Protection Failed

**Error:** "Protection did not modify the text"

**Solution:**
1. Check environment variables are set:
   ```bash
   echo $DEV_EDITION_EMAIL
   echo $DEV_EDITION_API_KEY
   ```
2. Use "redact" mode instead of "protect"
3. Verify credentials at https://developer.protegrity.com/

### Guardrails Not Working

**Issue:** All messages accepted

**Solution:**
1. Check PROTEGRITY_API_URL is correct
2. Verify API is accessible: `curl http://10.53.1.178:8502/api/health`
3. Check backend logs for API errors

### Inspection Panel Not Showing

**Issue:** No "Show Protegrity Analysis" button

**Solution:**
1. Check `protegrity_mode` is not "none"
2. Verify backend is returning `protegrity_data` in response
3. Check browser console for errors

## Testing

Run tests with:
```bash
./run_tests.sh
```

Backend tests include:
- Protegrity service mocking
- Guardrail blocking scenarios
- PII redaction validation
- Error handling

Frontend tests include:
- Inspection panel rendering
- Protegrity data display
- Icon and badge components

## Production Considerations

1. **API Credentials** - Store securely, rotate regularly
2. **Mode Selection** - Use "protect" mode in production for reversibility
3. **Performance** - Protegrity adds ~500ms latency per message
4. **Caching** - Consider caching discovery results for similar messages
5. **Monitoring** - Log blocked messages and high-risk scores
6. **Compliance** - Ensure data residency requirements are met
7. **Backup** - Always store original text before redaction

## Resources

- Protegrity Developer Edition: http://10.53.1.178:8502/
- API Documentation: https://developer.protegrity.com/
- GitHub Repository: https://github.com/Protegrity-Developer-Edition
- Get Credentials: https://developer.protegrity.com/credentials

## Support

For Protegrity Developer Edition support:
- Documentation: https://docs.protegrity.com/
- Community: https://community.protegrity.com/
- Email: developer-support@protegrity.com
