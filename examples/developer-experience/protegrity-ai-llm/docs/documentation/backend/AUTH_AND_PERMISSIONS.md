# Authentication and Permissions

## Overview

This document describes the authentication and authorization system for the Protegrity AI application. The system is designed with simplicity, security, and clear access control in mind.

## Authentication Methods

The application supports two authentication methods:

### 1. JWT (JSON Web Tokens) - For Web Users

**Use Case:** Interactive web application access

**How it works:**
- User logs in via `/api/auth/token/` with username and password
- Server returns access token and refresh token
- Client includes token in `Authorization: Bearer <token>` header
- Token expires after configured period (refresh for new token)

**Example:**
```bash
# Login
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhb...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhb..."
}

# Use token
curl http://localhost:8000/api/models/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhb..."
```

### 2. API Keys - For Programmatic Access

**Use Case:** Server-to-server, automation, CLI tools

**How it works:**
- User generates API key via Django admin or management command
- Key is shown only once (never stored plaintext)
- Client includes key in request header
- Key inherits user's role and permissions

**Supported Header Formats:**
```bash
# Option 1: Authorization header
Authorization: Api-Key <your_key_here>

# Option 2: Custom header
X-API-Key: <your_key_here>
```

**Example:**
```bash
curl http://localhost:8000/api/chat/ \
  -H "Authorization: Api-Key AbCd1234EfGh5678IjKl..." \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Role-Based Access Control (RBAC)

### User Roles

Every user has exactly one role (stored in `UserProfile.role`):

| Role | Access Level | Use Case |
|------|--------------|----------|
| **PROTEGRITY** | Full access to all active resources | Internal employees, admins, developers |
| **STANDARD** | Limited access (Fin AI only, no agents/tools) | External users, demo accounts |
| **ANONYMOUS** | No access (unauthenticated) | N/A |

### Resource-Level Permissions

Resources (LLMProvider, Agent, Tool) declare minimum required role via `min_role` field:

```python
# Example: LLMProvider
llm = LLMProvider.objects.get(id="fin")
llm.min_role  # "STANDARD" - any authenticated user can use

llm = LLMProvider.objects.get(id="bedrock-claude")
llm.min_role  # "PROTEGRITY" - only Protegrity users can use
```

### Access Matrix

| User Role | Fin AI Model | Other Models | Agents | Tools |
|-----------|--------------|--------------|--------|-------|
| PROTEGRITY | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| STANDARD | ✅ Yes | ❌ No | ❌ No | ❌ No |
| ANONYMOUS | ❌ No | ❌ No | ❌ No | ❌ No |

## Permission Enforcement Points

### 1. List Endpoints (GET)

**Endpoints:**
- `/api/models/` - List available LLM models
- `/api/agents/` - List available agents
- `/api/tools/` - List available tools

**Behavior:**
- Automatically filtered by user's role
- PROTEGRITY users see all active resources
- STANDARD users see only resources with `min_role="STANDARD"`
- No error returned - just filtered results

**Example:**
```bash
# PROTEGRITY user
GET /api/models/
{
  "models": [
    {"id": "fin", "name": "Fin AI", ...},
    {"id": "bedrock-claude", "name": "Claude 3.5", ...},
    {"id": "gpt-4", "name": "GPT-4", ...}
  ]
}

# STANDARD user (same request)
GET /api/models/
{
  "models": [
    {"id": "fin", "name": "Fin AI", ...}
  ]
}
```

### 2. Chat Endpoint (POST)

**Endpoint:** `/api/chat/`

**Behavior:**
- Validates `model_id` and `agent_id` against user's role
- Returns 403 Forbidden if user lacks permission
- Clear error message explains the denial

**Error Responses:**

```json
// Forbidden model
{
  "error": {
    "code": "forbidden_model",
    "message": "You are not allowed to use this model."
  }
}

// Forbidden agent
{
  "error": {
    "code": "forbidden_agent",
    "message": "You are not allowed to use this agent."
  }
}
```

**Example - STANDARD user trying to use restricted model:**
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "model_id": "gpt-4"
  }'

# Response: 403 Forbidden
{
  "error": {
    "code": "forbidden_model",
    "message": "You are not allowed to use this model."
  }
}
```

## Implementation Details

### User Profile Auto-Creation

Every User automatically gets a UserProfile via post_save signal:

```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)  # Default role: STANDARD
```

### Permission Checking Functions

**`get_user_role(user) -> str`**
- Returns user's role: "PROTEGRITY", "STANDARD", or "ANONYMOUS"
- Handles unauthenticated users safely

**`filter_by_role(queryset, user) -> QuerySet`**
- Filters queryset of resources based on user's role
- Applied in list endpoints

**`check_resource_access(user, resource) -> bool`**
- Checks if user can access specific resource instance
- Applied in chat endpoint when model_id/agent_id provided

## Security Principles

### 1. Least Privilege by Default

- New resources default to `min_role="PROTEGRITY"` (most restrictive)
- New users default to `role="STANDARD"` (least privileged)
- Explicit elevation required for broader access

### 2. No Plaintext Secrets

- API keys hashed using Django's password hashers (same as user passwords)
- Prefix stored for fast lookup (indexed)
- Full key shown only once at creation time
- No way to retrieve original key after creation

### 3. Clear Failure Modes

- Forbidden access returns 403 with clear error code and message
- No "hidden" access via side channels
- Failed authentication returns 401 with descriptive error

### 4. Fail Closed

- Unknown roles get no access (empty querysets)
- Missing permissions reject request (not bypass)
- Invalid keys rejected immediately

## Configuration & Seeding

### Setting Up Roles

**1. Promote user to PROTEGRITY:**
```python
# Django shell
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username="admin@example.com")
user.profile.role = "PROTEGRITY"
user.profile.save()
```

**2. Configure resource permissions:**
```python
# Make Fin AI available to all users
from apps.core.models import LLMProvider
fin = LLMProvider.objects.get(id="fin")
fin.min_role = "STANDARD"
fin.save()

# Keep other models PROTEGRITY-only (default)
claude = LLMProvider.objects.get(id="bedrock-claude")
claude.min_role = "PROTEGRITY"  # Default, but explicit
claude.save()
```

### Default Configuration

After running migrations and seed commands:

**Models:**
- Fin AI: `min_role="STANDARD"` ✅ Available to all
- All others: `min_role="PROTEGRITY"` 🔒 Internal only

**Agents:**
- All agents: `min_role="PROTEGRITY"` 🔒 Internal only

**Tools:**
- All tools: `min_role="PROTEGRITY"` 🔒 Internal only

## Testing Permissions

### Manual Testing

```bash
# 1. Create test users
python manage.py createsuperuser --username protegrity@example.com
python manage.py createsuperuser --username standard@example.com

# 2. Set roles (Django shell)
from django.contrib.auth import get_user_model
User = get_user_model()

pro_user = User.objects.get(username="protegrity@example.com")
pro_user.profile.role = "PROTEGRITY"
pro_user.profile.save()

std_user = User.objects.get(username="standard@example.com")
std_user.profile.role = "STANDARD"  # Already default, but explicit
std_user.profile.save()

# 3. Test via API
# Login as each user and try accessing different resources
```

### Automated Tests

See `backend/apps/core/tests/test_auth_permissions.py` for comprehensive test suite covering:
- Role filtering logic
- List endpoint filtering
- Chat endpoint permission enforcement
- API key authentication

Run tests:
```bash
cd backend
python -m pytest apps/core/tests/test_auth_permissions.py -v
```

## Future Enhancements

### Potential Additions (Not Implemented)

1. **Granular Scopes:** API keys with limited scopes (e.g., "chat:read" but not "chat:write")
2. **Per-User Model Access:** Override default min_role on per-user basis
3. **Rate Limiting:** Per-user or per-key rate limits
4. **Audit Logging:** Track all permission denials
5. **Time-Based Access:** Temporary elevated permissions
6. **Team/Group Support:** Multiple users sharing resources

These are **not planned** for current implementation. Keep it simple until proven necessary.

## Troubleshooting

### "You are not allowed to use this model"

**Cause:** User's role < resource's min_role

**Solution:**
1. Check user's role: `user.profile.role`
2. Check resource's min_role: `llm.min_role`
3. Either elevate user's role OR lower resource's min_role

### "Invalid API key"

**Causes:**
- Key prefix doesn't match any active key
- Key hash doesn't match stored hash
- Key is inactive (`is_active=False`)
- Key is expired (`expires_at < now`)

**Solution:**
1. Verify key is correct (copy-paste error?)
2. Check key status in Django admin
3. Regenerate key if lost

### User sees empty lists

**Expected behavior for STANDARD users:**
- `/api/agents/` returns `[]` (all agents are PROTEGRITY-only)
- `/api/tools/` returns `[]` (all tools are PROTEGRITY-only)
- `/api/models/` returns only Fin AI

**Not a bug** - this is least-privilege design.

---

**Last Updated:** 2025-12-11
**Maintained By:** Protegrity AI Team
