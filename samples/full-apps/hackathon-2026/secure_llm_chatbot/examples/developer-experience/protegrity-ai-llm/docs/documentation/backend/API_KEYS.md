# API Keys

## Overview

API keys provide secure, programmatic access to the Protegrity AI chat API. They allow servers, automation scripts, and CLI tools to interact with the API without requiring interactive login.

**Key Features:**
- Per-user keys that inherit user's role and permissions
- Cryptographically secure generation
- Hashed storage (never plaintext)
- Revocable and expirable
- Audit trail via `last_used_at`

## Why API Keys?

### Use Cases

**✅ Good for:**
- Server-to-server integration
- CI/CD pipelines and automation
- CLI tools and scripts
- Scheduled jobs and background tasks
- Third-party integrations
- Mobile apps (with secure storage)

**❌ Not for:**
- Interactive web applications (use JWT instead)
- Client-side JavaScript (exposes key to users)
- Sharing between multiple people (each person should have their own)

### vs JWT Tokens

| Feature | API Keys | JWT Tokens |
|---------|----------|------------|
| **Use Case** | Programmatic access | Interactive web sessions |
| **Lifetime** | Long-lived (days/months/never) | Short-lived (minutes/hours) |
| **Revocation** | Instant via `is_active` flag | Requires blacklist or expiration |
| **Storage** | Secure environment variables | Memory (browser/app) |
| **Rotation** | Manual (generate new, revoke old) | Automatic (refresh tokens) |

## Security Design

### Generation

Keys are generated using Python's `secrets` module (cryptographically secure):

```python
import secrets
key = secrets.token_urlsafe(32)  # 43 URL-safe characters
```

**Properties:**
- 32 bytes of entropy (256 bits)
- Base64 URL-safe encoding (no special chars)
- Format: `AbCd1234EfGh5678IjKl9012MnOp3456QrSt7890Uv`

### Storage

Keys are **never stored in plaintext**. Storage uses same security as Django User passwords:

1. **Prefix Extraction:** First 8 characters stored for fast lookup
   - Indexed for O(1) lookups
   - Example: `AbCd1234` from `AbCd1234EfGh5678...`

2. **Hash Generation:** Full key hashed using Django's password hashers
   - PBKDF2 with SHA256 by default
   - Configurable via Django settings
   - Format: `pbkdf2_sha256$600000$...`

3. **Database Storage:**
   ```sql
   | prefix   | hashed_key                              |
   |----------|-----------------------------------------|
   | AbCd1234 | pbkdf2_sha256$600000$salt$hash          |
   ```

4. **Verification:** Constant-time comparison via `check_password()`
   - Prevents timing attacks
   - Same function used for user login

### Lookup Process

```python
# 1. Client sends key
Authorization: Api-Key AbCd1234EfGh5678IjKl...

# 2. Server extracts prefix
prefix = key[:8]  # "AbCd1234"

# 3. Fast database lookup
key_obj = ApiKey.objects.filter(prefix="AbCd1234", is_active=True).first()

# 4. Hash verification (constant-time)
if key_obj.check_key(full_key):
    # Authenticated!
    request.user = key_obj.user
```

**Why this design?**
- Prefix index enables fast lookup without full table scan
- Hash verification ensures security (attacker can't forge keys)
- Constant-time comparison prevents timing attacks

## Creating API Keys

### Method 1: Django Shell

```python
# python manage.py shell

from django.contrib.auth import get_user_model
from apps.core.models import ApiKey

User = get_user_model()
user = User.objects.get(username="admin@example.com")

# Create key
api_key, raw_key = ApiKey.create_for_user(
    user=user,
    name="Production Server",
    scopes=["chat"]
)

print(f"API Key created!")
print(f"Key ID: {api_key.id}")
print(f"Name: {api_key.name}")
print(f"Key (save this, shown only once): {raw_key}")
```

**Output:**
```
API Key created!
Key ID: 550e8400-e29b-41d4-a716-446655440000
Name: Production Server
Key (save this, shown only once): AbCd1234EfGh5678IjKl9012MnOp3456QrSt7890Uv
```

### Method 2: Django Admin

1. Navigate to Django Admin: `http://localhost:8000/admin/`
2. Go to "Api Keys" section
3. Click "Add Api Key"
4. Select user, enter name, set scopes
5. Save
6. **Copy the displayed key immediately** (never shown again)

### Method 3: Management Command (Future)

```bash
# Not yet implemented, but planned
python manage.py create_api_key \
  --user admin@example.com \
  --name "CI/CD Pipeline" \
  --expires 30d
```

## Using API Keys

### Option 1: Authorization Header (Recommended)

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Authorization: Api-Key AbCd1234EfGh5678IjKl9012MnOp3456QrSt7890Uv" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

**Format:** `Authorization: Api-Key <your_key>`
- Standard HTTP authentication pattern
- Easily filtered from logs
- Supported by most HTTP clients

### Option 2: Custom Header

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "X-API-Key: AbCd1234EfGh5678IjKl9012MnOp3456QrSt7890Uv" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

**Format:** `X-API-Key: <your_key>`
- Alternative if Authorization header conflicts
- Some tools prefer custom headers

### Python Example

```python
import requests

API_KEY = "AbCd1234EfGh5678IjKl9012MnOp3456QrSt7890Uv"
API_URL = "http://localhost:8000/api/chat/"

response = requests.post(
    API_URL,
    headers={
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "message": "What is Protegrity?"
    }
)

print(response.json())
```

### JavaScript Example (Node.js)

```javascript
const axios = require('axios');

const API_KEY = 'AbCd1234EfGh5678IjKl9012MnOp3456QrSt7890Uv';
const API_URL = 'http://localhost:8000/api/chat/';

async function chat(message) {
  const response = await axios.post(API_URL, 
    { message },
    {
      headers: {
        'Authorization': `Api-Key ${API_KEY}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  return response.data;
}

chat('Hello!').then(console.log);
```

## Role and Permission Inheritance

API keys **inherit** the user's role and permissions:

```python
# User has STANDARD role
user.profile.role  # "STANDARD"

# Create API key for this user
api_key, raw_key = ApiKey.create_for_user(user, name="My Key")

# Key inherits STANDARD permissions
# Can only access:
# - Fin AI model (min_role="STANDARD")
# - No agents (all min_role="PROTEGRITY")
# - No tools (all min_role="PROTEGRITY")
```

**No separate permission system for API keys.** This simplifies security:
- One role system to audit
- Role changes immediately affect all user's keys
- No confusion about "key permissions" vs "user permissions"

## Managing API Keys

### Listing Keys

```python
# Django shell
from apps.core.models import ApiKey

# All keys for a user
user_keys = ApiKey.objects.filter(user=user)
for key in user_keys:
    print(f"{key.name}: {key.prefix}... (active: {key.is_active})")
```

### Revoking Keys

**Instant revocation via `is_active` flag:**

```python
# Django shell
key = ApiKey.objects.get(id="key-uuid-here")
key.is_active = False
key.save()

# Key immediately invalid - next request will return 401
```

**OR via Django Admin:**
1. Find key in "Api Keys" section
2. Uncheck "Is active"
3. Save

### Rotating Keys

**Best practice: Generate new, revoke old**

```python
# 1. Generate new key
new_key, raw_key = ApiKey.create_for_user(user, name="Production Server v2")
print(f"New key: {raw_key}")

# 2. Update your application to use new key

# 3. Revoke old key once confirmed working
old_key = ApiKey.objects.get(name="Production Server")
old_key.is_active = False
old_key.save()
```

**Rotation schedule:**
- **High security:** Every 30-90 days
- **Medium security:** Every 6-12 months
- **On breach:** Immediately

### Expiration

Set `expires_at` for time-limited keys:

```python
from django.utils import timezone
from datetime import timedelta

# Key expires in 30 days
api_key, raw_key = ApiKey.create_for_user(user, name="Temp Key")
api_key.expires_at = timezone.now() + timedelta(days=30)
api_key.save()
```

**Expired keys:**
- Rejected with 401 error: "API key expired"
- Can be re-activated by updating `expires_at`

## Audit and Monitoring

### Last Used Tracking

Every successful authentication updates `last_used_at`:

```python
key = ApiKey.objects.get(id="key-uuid")
print(f"Last used: {key.last_used_at}")
# Output: Last used: 2025-12-11 10:30:45 UTC
```

**Use cases:**
- Identify unused keys for cleanup
- Detect suspicious activity (key used from unexpected location)
- Enforce "keys not used in 90 days must be rotated" policy

### Audit Queries

```python
# Keys not used in 90 days
from django.utils import timezone
from datetime import timedelta

stale_threshold = timezone.now() - timedelta(days=90)
stale_keys = ApiKey.objects.filter(
    last_used_at__lt=stale_threshold,
    is_active=True
)

# Keys never used
never_used = ApiKey.objects.filter(
    last_used_at__isnull=True,
    is_active=True
)

# Keys created recently
recent_keys = ApiKey.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=7)
)
```

## Scopes (Future Extension)

Currently, all keys have `scopes=["chat"]` but aren't enforced. Future versions may implement granular scopes:

**Potential scopes:**
- `chat:read` - Read conversation history
- `chat:write` - Send messages
- `models:read` - List models
- `admin:write` - Modify resources

**Implementation pattern:**
```python
# In authentication
def authenticate(self, request):
    # ... existing auth ...
    
    # Check scope (future)
    required_scope = self.get_required_scope(request)
    if required_scope not in key_obj.scopes:
        raise exceptions.PermissionDenied(f"Key lacks scope: {required_scope}")
    
    return (key_obj.user, None)
```

**Not implemented yet** - keep it simple until proven necessary.

## Error Handling

### Common Errors

**401 Unauthorized: "Invalid API key"**
- Prefix doesn't exist in database
- Hash doesn't match stored hash
- Key was copied incorrectly

**401 Unauthorized: "API key expired"**
- Key's `expires_at` < current time
- Update expiration or generate new key

**401 Unauthorized: "Invalid API key format"**
- Key too short (< 8 chars)
- Key contains invalid characters
- Check copy-paste for truncation

**403 Forbidden: "You are not allowed..."**
- Key authenticated successfully
- But user's role insufficient for requested resource
- Check user's role: `key.user.profile.role`

### Example Error Response

```json
{
  "detail": "Invalid API key."
}
```

**Note:** Errors are intentionally vague to avoid leaking information to attackers.

## Best Practices

### Storage

✅ **DO:**
- Store in environment variables
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- Restrict file permissions (chmod 600)
- Use `.env` files (never commit to git)

❌ **DON'T:**
- Hardcode in source code
- Commit to version control
- Share via email or chat
- Log keys in application logs

### Security

✅ **DO:**
- Rotate keys periodically
- Use separate keys per environment (dev, staging, prod)
- Revoke keys immediately on breach
- Set expiration for temporary access
- Monitor `last_used_at` for anomalies

❌ **DON'T:**
- Share keys between users
- Use same key across multiple applications
- Expose keys in URLs (query parameters)
- Send keys over unencrypted connections

### Organization

✅ **DO:**
- Use descriptive names ("Production API Server", "CI/CD Pipeline")
- Document which keys are used where
- Track key ownership and purpose
- Clean up unused keys

❌ **DON'T:**
- Create keys without labels
- Keep old unused keys active
- Lose track of where keys are deployed

## Troubleshooting

### I lost my API key

**There is no way to retrieve the original key.** You must generate a new one:

1. Generate new key for same user
2. Update your application with new key
3. Revoke lost key for security

### Key works from localhost but not production

**Possible causes:**
- Key not synced to production database
- Different database between environments
- Key accidentally revoked
- Network/firewall blocking requests

**Solution:**
1. Verify key exists in production database
2. Check `is_active=True` and `expires_at > now`
3. Test with curl from production server

### How do I know which key was used?

Keys are not logged by default (security). To add tracking:

```python
# In ApiKeyAuthentication.authenticate()
import logging
logger = logging.getLogger(__name__)

# After successful authentication
logger.info(f"API key {key_obj.id} ({key_obj.name}) used by {key_obj.user.username}")
```

**Warning:** Never log the full key value.

---

**Last Updated:** 2025-12-11
**Maintained By:** Protegrity AI Team
