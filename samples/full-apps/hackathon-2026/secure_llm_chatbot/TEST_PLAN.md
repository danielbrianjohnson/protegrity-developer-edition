# Comprehensive Test Plan

## Current Status
- **Backend:** 84% coverage (122 tests)
- **Frontend:** Minimal coverage (3 test files, 45 tests)

## Priority 1: Critical Backend Gaps

### 1. Conversation Views Tests (`test_conversation_views.py`)
**Coverage Gap:** 39% (39 lines missing)
**Test Cases:**
- [ ] List conversations for authenticated user
- [ ] Get conversation by ID (owner access)
- [ ] Get conversation by ID (unauthorized access)
- [ ] Delete conversation (owner)
- [ ] Delete conversation (unauthorized)
- [ ] Conversation filtering/pagination
- [ ] Error handling for non-existent conversations

### 2. Protegrity Service Tests (`test_protegrity_service_detailed.py`)
**Coverage Gap:** 63% (40 lines missing)
**Test Cases:**
- [ ] `check_guardrails()` - accepted input
- [ ] `check_guardrails()` - rejected input (high risk)
- [ ] `discover_pii()` - find entities
- [ ] `discover_pii()` - no entities found
- [ ] `classify_and_redact()` - redact PII
- [ ] `classify_and_protect()` - tokenize PII
- [ ] `unprotect_data()` - detokenize
- [ ] Service initialization with missing credentials
- [ ] API timeout handling
- [ ] Malformed API responses

### 3. Tool Router Tests (`test_tool_router_detailed.py`)
**Coverage Gap:** 72% (20 lines missing)
**Test Cases:**
- [ ] Route to classify tool with valid data
- [ ] Route to redact tool with valid data
- [ ] Route to protect tool with valid data
- [ ] Tool execution with missing parameters
- [ ] Tool execution with invalid tool name
- [ ] Tool execution error handling
- [ ] Tool permission checks for standard users

### 4. Views Edge Cases (`test_views_edge_cases.py`)
**Coverage Gap:** 82% (29 lines missing)
**Test Cases:**
- [ ] Chat endpoint with malformed protegrity_mode
- [ ] Chat endpoint with conversation owned by different user
- [ ] Poll endpoint race conditions
- [ ] Models endpoint with no available models
- [ ] Error responses for 500 errors
- [ ] Request validation edge cases

## Priority 2: Critical Frontend Tests

### 5. ChatMessage Component (`ChatMessage.test.jsx`)
**Test Cases:**
- [ ] Renders user message correctly
- [ ] Renders assistant message correctly
- [ ] Renders thinking state
- [ ] Renders error state
- [ ] Renders blocked message state
- [ ] Formats markdown content
- [ ] Handles code blocks
- [ ] Shows timestamps
- [ ] Copy message functionality
- [ ] PII redaction indicators

### 6. Sidebar Component (`Sidebar.test.jsx`)
**Test Cases:**
- [ ] Renders conversation list
- [ ] Creates new conversation
- [ ] Selects conversation
- [ ] Deletes conversation
- [ ] Shows confirmation modal on delete
- [ ] Filters conversations
- [ ] Handles empty state
- [ ] Shows loading state
- [ ] Keyboard navigation

### 7. ChatHeader Component (`ChatHeader.test.jsx`)
**Test Cases:**
- [ ] Displays model selector
- [ ] Changes model
- [ ] Shows Protegrity mode toggle
- [ ] Changes Protegrity mode (redact/protect/none)
- [ ] Shows conversation title
- [ ] Opens settings
- [ ] Mobile responsive menu

### 8. LoginForm Component (`LoginForm.test.jsx`)
**Test Cases:**
- [ ] Renders email and password fields
- [ ] Validates email format
- [ ] Validates required fields
- [ ] Submits login form
- [ ] Shows login errors
- [ ] Shows loading state during login
- [ ] Handles successful login
- [ ] Handles failed login

### 9. WelcomeScreen Component (`WelcomeScreen.test.jsx`)
**Test Cases:**
- [ ] Renders welcome message
- [ ] Shows quick start tips
- [ ] Displays sample prompts
- [ ] Clicking sample prompt triggers chat
- [ ] Shows feature highlights
- [ ] Displays user role-specific features

### 10. ErrorBanner Component (`ErrorBanner.test.jsx`)
**Test Cases:**
- [ ] Renders error message
- [ ] Renders warning message
- [ ] Renders info message
- [ ] Shows dismiss button
- [ ] Dismisses on button click
- [ ] Auto-dismisses after timeout
- [ ] Multiple error handling

## Priority 3: Integration & E2E Tests

### 11. Backend Integration Tests
**Test Cases:**
- [ ] Full chat flow: create conversation → send message → poll → receive response
- [ ] Protegrity flow: input with PII → protection → LLM → output protection → poll
- [ ] Agent flow: select agent → send message → tool execution → response
- [ ] Multi-turn conversation with context
- [ ] Role switching mid-conversation
- [ ] Conversation persistence across sessions

### 12. Frontend Integration Tests
**Test Cases:**
- [ ] Login → create conversation → send message → receive response
- [ ] Create conversation → send PII → verify redaction in UI
- [ ] Switch between conversations
- [ ] Delete conversation while active
- [ ] Network error recovery
- [ ] Token refresh flow

## Priority 4: API & Utility Tests

### 13. Frontend API Utils (`api.test.js`)
**Test Cases:**
- [ ] `login()` success
- [ ] `login()` failure
- [ ] `getCurrentUser()` with valid token
- [ ] `getCurrentUser()` with expired token
- [ ] `sendMessage()` success
- [ ] `sendMessage()` network error
- [ ] `pollConversation()` success
- [ ] `getModels()` success
- [ ] Token refresh logic
- [ ] Request retry logic

### 14. Frontend Hooks Tests
**Test Cases:**
- [ ] `useClickOutside` - detects outside clicks
- [ ] `useClickOutside` - ignores inside clicks
- [ ] Custom hooks for API calls
- [ ] Error handling hooks

## Implementation Order

### Week 1: Critical Backend Gaps
1. Create `test_conversation_views.py` (39% → 95%+)
2. Create `test_protegrity_service_detailed.py` (63% → 90%+)
3. Create `test_tool_router_detailed.py` (72% → 95%+)

**Expected:** Backend coverage 84% → 92%+

### Week 2: Critical Frontend Components
1. Create `ChatMessage.test.jsx`
2. Create `Sidebar.test.jsx`
3. Create `ChatHeader.test.jsx`
4. Create `LoginForm.test.jsx`

**Expected:** Frontend coverage ~15% → 60%+

### Week 3: Remaining Frontend & Integration
1. Create `WelcomeScreen.test.jsx`
2. Create `ErrorBanner.test.jsx`
3. Create `api.test.js`
4. Add integration tests

**Expected:** Frontend coverage 60% → 80%+

### Week 4: E2E & Edge Cases
1. E2E test suite with Playwright or Cypress
2. Edge case coverage
3. Performance tests
4. Accessibility tests

**Expected:** Overall coverage 85%+ with high confidence

## Success Metrics

- [ ] Backend: 92%+ line coverage
- [ ] Frontend: 80%+ line coverage
- [ ] All critical user flows covered
- [ ] All API endpoints tested
- [ ] All error paths tested
- [ ] All Protegrity integration flows tested
- [ ] Zero test flakiness
- [ ] CI/CD pipeline passing consistently

## Notes

- Focus on **behavior testing** over implementation details
- Test **user-facing functionality** first
- Mock external services (Protegrity, LLMs) appropriately
- Ensure tests are **fast and reliable**
- Document test setup requirements
