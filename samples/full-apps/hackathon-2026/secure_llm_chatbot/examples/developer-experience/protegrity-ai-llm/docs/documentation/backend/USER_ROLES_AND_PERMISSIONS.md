# User Roles & Permissions System

## Overview

The system uses **Django Groups** for role-based access control (RBAC), providing flexible and scalable user permission management.

## Architecture

### Django Groups (Role Management)
- **"Protegrity Users"** - Full access to all active models, agents, and tools
- **"Standard Users"** - Limited access to STANDARD-tier resources only

### Benefits of Groups-Based System
- ✅ **Scalable**: Add new roles without code changes
- ✅ **Flexible**: Users can belong to multiple groups
- ✅ **Standard**: Uses Django's built-in permission system
- ✅ **Extensible**: Easy to add granular permissions later

## User Roles

### PROTEGRITY Role
**Group**: `Protegrity Users`

**Access**:
- ✅ All active LLM models (Fin AI, Claude, GPT-4, etc.)
- ✅ All active agents
- ✅ All active tools
- ✅ Full API access

**Use Cases**:
- Protegrity employees
- Internal administrators
- Power users requiring full AI capabilities

### STANDARD Role
**Group**: `Standard Users`

**Access**:
- ✅ LLM models with `min_role="STANDARD"` (typically Fin AI)
- ❌ No access to agents
- ❌ No access to tools
- ✅ Basic chat API access

**Use Cases**:
- External customers
- Basic tier users
- Trial accounts

### No Role (Default)
**Groups**: None

**Access**:
- ✅ Same as STANDARD role (safe default)
- ✅ Can be upgraded by adding to a group

## Managing User Roles

### Via Django Admin
1. Navigate to `/admin/auth/user/`
2. Click on a user to edit
3. Scroll to "Groups" section
4. Add user to "Protegrity Users" or "Standard Users" group
5. Save

**Admin UI Features**:
- User list shows current role in "Role" column
- User list shows all groups in "Groups" column
- User edit page shows role status in "User Profile" inline
- Color-coded role display (green=PROTEGRITY, blue=STANDARD)

### Via Management Command
```bash
# Set user as PROTEGRITY
python manage.py set_user_role username@example.com PROTEGRITY

# Set user as STANDARD
python manage.py set_user_role username@example.com STANDARD
```

### Programmatically
```python
from django.contrib.auth.models import User, Group

# Get user
user = User.objects.get(username="user@example.com")

# Add to Protegrity Users
protegrity_group = Group.objects.get(name="Protegrity Users")
user.groups.add(protegrity_group)

# Remove from all role groups
user.groups.clear()

# Add to Standard Users
standard_group = Group.objects.get(name="Standard Users")
user.groups.add(standard_group)
```

## Initial Setup

### First-Time Setup
Run this command to create groups and migrate existing users:

```bash
python manage.py setup_user_groups
```

This will:
1. Create "Protegrity Users" and "Standard Users" groups
2. Migrate users from old `UserProfile.role` field to groups
3. Display migration summary

### Creating New Users

#### Via Django Admin (createsuperuser)
```bash
python manage.py createsuperuser
# Then assign to group via admin or CLI
python manage.py set_user_role admin@example.com PROTEGRITY
```

#### Via Management Command
```bash
# Create user + assign role in one step
python manage.py shell << 'EOF'
from django.contrib.auth.models import User, Group
user = User.objects.create_user('newuser@example.com', password='temp123')
protegrity_group = Group.objects.get(name='Protegrity Users')
user.groups.add(protegrity_group)
print(f"Created {user.username} as PROTEGRITY user")
EOF
```

## How It Works

### Role Detection
The `get_user_role()` function checks group membership:

```python
from apps.core.utils import get_user_role

role = get_user_role(request.user)
# Returns: "PROTEGRITY", "STANDARD", or "ANONYMOUS"
```

**Logic**:
1. If unauthenticated → `"ANONYMOUS"`
2. If in "Protegrity Users" group → `"PROTEGRITY"`
3. Otherwise → `"STANDARD"` (safe default)

### Resource Filtering
The `filter_by_role()` function filters querysets by role:

```python
from apps.core.permissions import filter_by_role
from apps.core.models import LLMProvider

# Get models user can access
models = filter_by_role(LLMProvider.objects.all(), request.user)
```

**Filtering Rules**:
- **PROTEGRITY**: All active resources
- **STANDARD**: Only resources with `min_role="STANDARD"`
- **ANONYMOUS**: Empty queryset

### Default Model Selection
The `get_default_llm_for_user()` function returns appropriate default:

```python
from apps.core.utils import get_default_llm_for_user

llm = get_default_llm_for_user(request.user)
# Returns first accessible model by display_order
```

## Migration from Old System

### Old System (Deprecated)
```python
# UserProfile.role field (CharField)
user.profile.role = "PROTEGRITY"  # Don't use this anymore
```

### New System
```python
# Django Groups
user.groups.add(protegrity_group)  # Use this instead
```

### Backward Compatibility
- Old `UserProfile.role` field still exists but is **deprecated**
- `get_user_role()` now checks groups, not profile
- Run `setup_user_groups` to migrate existing data

## Extending the System

### Adding New Roles
```python
# Create new group
enterprise_group, _ = Group.objects.get_or_create(name="Enterprise Users")

# Update get_user_role() to recognize it
if user.groups.filter(name="Enterprise Users").exists():
    return "ENTERPRISE"
```

### Adding Granular Permissions
```python
# Define custom permissions in models.py
class LLMProvider(models.Model):
    class Meta:
        permissions = [
            ("can_use_gpt4", "Can use GPT-4"),
            ("can_use_claude", "Can use Claude"),
        ]

# Assign permissions to groups
from django.contrib.auth.models import Permission
perm = Permission.objects.get(codename="can_use_gpt4")
protegrity_group.permissions.add(perm)

# Check permissions in code
if user.has_perm("core.can_use_gpt4"):
    # Allow access to GPT-4
    pass
```

## Testing

### Test with Different Roles
```python
import pytest
from django.contrib.auth.models import User, Group

@pytest.mark.django_db
def test_protegrity_user_access():
    user = User.objects.create_user("test", password="test")
    protegrity_group = Group.objects.get(name="Protegrity Users")
    user.groups.add(protegrity_group)
    
    from apps.core.utils import get_user_role
    assert get_user_role(user) == "PROTEGRITY"
```

## Troubleshooting

### User Can't See Models
1. Check user's groups: `user.groups.all()`
2. Check model's `min_role`: `LLMProvider.objects.values('id', 'name', 'min_role')`
3. Verify user is in correct group: `user.groups.filter(name="Protegrity Users").exists()`

### Groups Not Created
Run setup command:
```bash
python manage.py setup_user_groups
```

### User Has No Access After Login
- Make sure user is in at least one group
- STANDARD users only see models with `min_role="STANDARD"`
- Check that Fin AI has `min_role="STANDARD"`

## Security Considerations

1. **Default to STANDARD**: Authenticated users without groups get STANDARD role (least privilege)
2. **Group Assignment**: Only staff/superusers can assign groups via admin
3. **API Validation**: All API endpoints check permissions via `filter_by_role()`
4. **No Bypass**: Even if user guesses model ID, permission check prevents access

## Summary

| Aspect | Old System | New System |
|--------|-----------|------------|
| Storage | `UserProfile.role` field | Django Groups |
| Scalability | Limited (hardcoded choices) | Excellent (dynamic groups) |
| Flexibility | Single role per user | Multiple groups per user |
| Standard | Custom implementation | Django built-in |
| Migration | Code changes needed | Admin changes only |
| Granular Permissions | Not supported | Fully supported |

The Groups-based system provides a more scalable, flexible, and maintainable approach to user permissions that aligns with Django best practices.
