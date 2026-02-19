# Fix: "No LLM provider specified" Error

## Problem Summary

After login, when sending the first message in a new conversation, the app returned:
```
POST http://127.0.0.1:8000/api/chat/ 400 (Bad Request)
Error: No LLM provider specified and no default available
```

Additionally, the frontend console showed:
```
Icon "alert-circle" not found
```

## Root Causes

1. **Backend**: No fallback logic when `model_id` was not provided for new conversations
2. **Frontend**: Model selection not auto-initialized after login
3. **Frontend**: Missing validation to ensure model was selected before sending
4. **Frontend**: Icon name mismatch (`alert-circle` vs `alertCircle`)

## Solution Implemented

### Backend Changes

#### 1. Added `get_default_llm_for_user()` Helper
**File**: `backend/apps/core/utils.py`

```python
def get_default_llm_for_user(user):
    """
    Return a safe default LLM for the given user based on role.
    
    - STANDARD users: Only models with min_role="STANDARD" (Fin AI)
    - PROTEGRITY users: Any active model, ordered by display_order
    - Returns None if no models are available
    """
    from .models import LLMProvider
    from .permissions import filter_by_role
    
    qs = filter_by_role(LLMProvider.objects.all(), user)
    qs = qs.order_by("display_order", "name")
    
    return qs.first()
```

#### 2. Updated Chat View to Use Default LLM
**File**: `backend/apps/core/views.py`

Changed the new conversation logic from:
```python
# Old: Hard-coded fallback to "dummy" model
try:
    llm_provider = LLMProvider.objects.get(id="dummy", is_active=True)
except LLMProvider.DoesNotExist:
    return error_response("No LLM provider specified...", ...)
```

To:
```python
# New: Smart fallback based on user's role
if not llm_provider:
    from .utils import get_default_llm_for_user
    llm_provider = get_default_llm_for_user(request.user)
    
    if not llm_provider:
        return error_response(
            "No LLM providers are available for your account. Please contact an administrator.",
            code="no_available_llm",
            http_status=400
        )
    
    model_id = llm_provider.id
```

### Frontend Changes

#### 3. Fixed Icon Name
**Files**: 
- `frontend/console/src/components/common/Icon.jsx` - Added `alertCircle` icon
- `frontend/console/src/components/ErrorBanner/ErrorBanner.jsx` - Changed `alert-circle` to `alertCircle`

#### 4. Auto-Select First Model on Login
**File**: `frontend/console/src/App.jsx`

```javascript
useEffect(() => {
  if (!isAuthenticated) return;
  
  const fetchModels = async () => {
    const data = await fetch("http://127.0.0.1:8000/api/models/").json();
    setAvailableModels(data.models || []);
    
    // Always auto-select first model if none selected
    if (data.models && data.models.length > 0 && !selectedModel) {
      setSelectedModel(data.models[0]);
      console.log("Auto-selected default model:", data.models[0].name);
    }
  };
  
  fetchModels();
}, [isAuthenticated]);
```

#### 5. Added Model Validation Before Sending
**File**: `frontend/console/src/App.jsx`

```javascript
const handleSendMessage = async (content) => {
  // Validate model selection for new conversations
  if (!activeConversationId && !selectedModel) {
    setError({
      code: 'no_model_selected',
      message: 'Please select a model before starting a new chat.',
    });
    return;
  }
  
  // ... rest of send logic
};
```

## Test Coverage

Created comprehensive test suite: `backend/apps/core/tests/test_default_llm.py`

**6 tests, all passing:**
1. ✅ Standard user gets Fin AI as default
2. ✅ Protegrity user gets first model by display_order
3. ✅ User with no available models gets None
4. ✅ Inactive models are excluded
5. ✅ New conversation without model uses default
6. ✅ No available models returns proper error

## User Experience Flow

### Before Fix
1. User logs in
2. User types message and hits send
3. ❌ **Error**: "No LLM provider specified and no default available"
4. ❌ **Icon error**: "alert-circle" not found

### After Fix
1. User logs in
2. ✅ First model auto-selected (Fin AI for Standard users)
3. User types message and hits send
4. ✅ Backend uses selected model OR falls back to default
5. ✅ Message sent successfully
6. ✅ Error banner works if issues occur

## Role-Based Behavior

### Standard Users
- **Available models**: Only models with `min_role="STANDARD"` (typically Fin AI)
- **Default model**: Fin AI (first STANDARD model by display_order)
- **Validation**: Cannot access PROTEGRITY-only models

### Protegrity Users
- **Available models**: All active models
- **Default model**: First active model by display_order
- **Validation**: Full access to all models

## Testing the Fix

### Backend Tests
```bash
cd backend
python -m pytest apps/core/tests/test_default_llm.py -v
# Should show: 6 passed
```

### Manual Testing
1. Start backend: `cd backend && python manage.py runserver`
2. Start frontend: `cd frontend/console && npm run dev`
3. Log in with Standard user (e.g., username: `user`, password: `password`)
4. Verify model dropdown shows "Fin AI" selected
5. Type a message and send
6. ✅ Should work without errors
7. Check that conversation is created with Fin AI as the model

### Edge Cases to Test
1. **No models available**: Create user with role that has no accessible models
   - Expected: Clear error message asking to contact admin
2. **Multiple models**: Protegrity user with multiple models
   - Expected: First model by display_order is auto-selected
3. **Inactive models**: All models set to inactive
   - Expected: No models available, proper error message

## Files Changed

### Backend
- `backend/apps/core/utils.py` - Added `get_default_llm_for_user()`
- `backend/apps/core/views.py` - Updated chat view to use default LLM
- `backend/apps/core/tests/test_default_llm.py` - New test file (6 tests)

### Frontend
- `frontend/console/src/components/common/Icon.jsx` - Added `alertCircle` icon
- `frontend/console/src/components/ErrorBanner/ErrorBanner.jsx` - Fixed icon name
- `frontend/console/src/App.jsx` - Auto-select model + validation

## Benefits

1. **User-friendly**: Users never see "No LLM provider" error
2. **Role-aware**: Automatically selects appropriate model based on user permissions
3. **Fail-safe**: Multiple layers of fallback logic
4. **Clear errors**: If no models available, clear message to contact admin
5. **Test coverage**: Comprehensive tests prevent regression

## Future Enhancements

- [ ] Remember user's last selected model (localStorage or user preferences)
- [ ] Add "Default model" setting in user preferences
- [ ] Show model capabilities in dropdown (streaming, max tokens, etc.)
- [ ] Add model switching during conversation (with proper validation)
