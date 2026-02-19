# User Experience - Account Features

## Overview

This document describes the user-facing account features in the Protegrity AI console, including user profile display, settings modal, and logout functionality.

## Features

### 1. User Menu (Bottom-Left Sidebar)

**Location:** Bottom of the sidebar (when expanded)

**Appearance:**
- User avatar with initials (circular badge with Protegrity orange gradient)
- User display name (first + last name, or username if names not set)
- User role badge (PROTEGRITY or STANDARD)
- Click to open dropdown menu

**Dropdown Options:**
- ⚙️ Settings - Opens user settings modal
- 🚪 Logout - Logs out and clears all state

**Behavior:**
- Click outside to close
- Only visible when sidebar is expanded
- Hidden when sidebar is collapsed

### 2. User Settings Modal

**Trigger:** Click "Settings" in user menu dropdown

**Sections:**

#### Profile Section
Displays read-only user information:
- Name (first + last name)
- Username
- Email

#### Role & Permissions Section
Displays user's role and capabilities:
- **Role Badge:** Visual indicator (orange for PROTEGRITY, grey for STANDARD)
- **Description:** Explains what the role allows
- **Permissions List:** Bullet points of specific capabilities

**PROTEGRITY Role:**
- Access all LLM models (Fin AI, Claude, GPT-4, etc.)
- Use custom agents and tools
- Enable Protegrity data protection modes
- View and manage all conversations

**STANDARD Role:**
- Access Fin AI model only
- Basic chat functionality
- View own conversations

#### Security Notice (PROTEGRITY users only)
Shows special notice for users with Protegrity access:
- 🔒 Icon indicator
- Explains data protection capabilities
- Highlights input/output tokenization features

**Actions:**
- Close button (X in top-right)
- Click backdrop to close
- Close button in footer

### 3. Logout Functionality

**Trigger:** Click "Logout" in user menu dropdown

**Behavior:**
1. Clears JWT tokens from localStorage (`access_token`, `refresh_token`)
2. Clears user state (`currentUser` set to null)
3. Clears all conversation data
4. Resets chat UI to initial state
5. Clears model/agent selections
6. User returns to unauthenticated state

**Console Log:** "User logged out successfully"

## Authentication Flow

### Initial Load (Bootstrap)
1. App checks for `access_token` in localStorage
2. If token exists, calls `/api/me/` to fetch current user
3. Sets `currentUser` state with user data
4. If token is invalid, clears tokens and shows login screen
5. Sets `authLoading` to false after check completes
6. If no token, shows login screen immediately

### Login Flow
1. User enters username and password in LoginForm
2. App calls `POST /api/auth/token/` with credentials
3. Backend validates credentials and returns JWT tokens:
   ```json
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   }
   ```
4. App stores `access` token in localStorage
5. App immediately calls `/api/me/` to fetch user data
6. Sets `currentUser` state and `isAuthenticated` to true
7. Main app UI is rendered with user menu visible

### Auto-Logout on 401
- Any API call that returns 401 triggers automatic logout
- Implemented in `apiFetch` - clears tokens when 401 detected
- `handleSendMessage` checks for 401 and calls `handleLogout()`
- User sees "Your session has expired. Please log in again." message
- Returns to login screen

### Token Management
- **Storage:** localStorage keys `access_token` and `refresh_token`
- **API Requests:** All API calls include `Authorization: Bearer <token>` header via `apiFetch`
- **Token Lifetime:** Access tokens expire after 1 hour, refresh tokens after 7 days
- **Automatic Clearing:** 401 responses trigger token removal
- **Manual Logout:** User can click logout to clear tokens and reset state

## API Integration

### GET /api/me/
Returns current authenticated user information.

**Request:**
```http
GET /api/me/
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": 1,
  "username": "user@example.com",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "PROTEGRITY",
  "is_protegrity": true
}
```

**Error Responses:**
- 401 Unauthorized: Token missing or invalid
- 403 Forbidden: Token valid but user lacks permissions

## Component Architecture

### App.jsx
- **State:**
  - `currentUser` - Current user object or null
  - `authLoading` - Boolean for auth check in progress
  - `userSettingsOpen` - Boolean for modal visibility
- **Effects:**
  - `useEffect()` on mount to load current user
- **Handlers:**
  - `handleLogout()` - Clears tokens and resets state

### Sidebar.jsx
- **Props:**
  - `currentUser` - User object to display
  - `onOpenSettings` - Callback to open settings modal
  - `onLogout` - Callback to logout
- **Renders:** UserMenu component at bottom (when not collapsed)

### UserMenu.jsx
- **Props:**
  - `user` - User object
  - `onOpenSettings` - Settings click callback
  - `onLogout` - Logout click callback
- **State:** `isOpen` - Dropdown visibility
- **Features:**
  - Click-outside-to-close
  - Keyboard accessible
  - Initials generation
  - Display name fallback

### UserSettingsModal.jsx
- **Props:**
  - `isOpen` - Modal visibility
  - `onClose` - Close callback
  - `user` - User object
- **Features:**
  - Backdrop click to close
  - Scrollable content
  - Role-specific descriptions
  - Permissions list
  - Security notice for PROTEGRITY users

## Styling

### Colors
- **Protegrity Orange:** `#ff6b35` (primary accent)
- **Gradient:** `linear-gradient(135deg, #ff6b35 0%, #ff8c5a 100%)`
- **Background:** `#1a1a1a` (dark theme)
- **Text:** `#ffffff` (primary), `rgba(255, 255, 255, 0.6)` (secondary)

### Component Files
- `UserMenu.jsx` + `UserMenu.css`
- `UserSettingsModal.jsx` + `UserSettingsModal.css`
- Sidebar updates in `Sidebar.jsx`

## Testing Checklist

### Manual Testing - Login Flow
- [ ] Load app with no token → Login screen appears
- [ ] Enter invalid credentials → Error message displays
- [ ] Enter valid credentials → Redirects to main app
- [ ] User menu appears after successful login
- [ ] App shows loading spinner during initial auth check
- [ ] Invalid token on page load → Shows login screen

### Manual Testing - User Menu & Settings
- [ ] User menu appears in sidebar when logged in
- [ ] Click user menu opens dropdown
- [ ] Click outside closes dropdown
- [ ] Settings button opens modal
- [ ] Modal displays correct user information
- [ ] Modal shows correct role badge and permissions
- [ ] PROTEGRITY users see security notice
- [ ] STANDARD users do not see security notice
- [ ] Close button closes modal
- [ ] Backdrop click closes modal

### Manual Testing - Logout
- [ ] Logout button clears tokens
- [ ] Logout returns to login screen
- [ ] Logout clears all conversations
- [ ] Logout logs console message
- [ ] Cannot access main app after logout without re-login

### Manual Testing - Session Expiry
- [ ] Expired token triggers auto-logout
- [ ] 401 error shows "session expired" message
- [ ] User is returned to login screen
- [ ] Can log back in after session expiry

### Integration Testing
- [ ] Login → API call → Token stored → /api/me/ called → Main app renders
- [ ] Valid token on page load → Auto-authenticated
- [ ] Invalid token on page load → Login screen shown
- [ ] Logout → All state cleared, tokens removed
- [ ] Settings modal shows correct permissions for each role
- [ ] Chat message with 401 → Auto-logout triggered

## Implementation Summary

### Completed Features
✅ **LoginForm Component** - Clean login UI with username/password  
✅ **JWT Token Management** - Helper functions in client.js  
✅ **Centralized apiFetch** - All API calls use consistent auth headers  
✅ **Auth State Management** - Bootstrap check, login, logout handlers  
✅ **Auth Gating** - Shows login screen when not authenticated  
✅ **Auto-Logout on 401** - Expired tokens trigger automatic logout  
✅ **Loading State** - Spinner during initial auth check  
✅ **User Menu** - Shows authenticated user with logout option  
✅ **User Settings Modal** - Displays user profile and permissions  

### Backend Endpoints
✅ **POST /api/auth/token/** - Login with username/password (SimpleJWT)  
✅ **POST /api/auth/token/refresh/** - Refresh access token  
✅ **GET /api/me/** - Get current user information (requires auth)  

### Token Configuration
- **Access Token:** 1 hour lifetime
- **Refresh Token:** 7 days lifetime
- **Algorithm:** HS256
- **Header Type:** Bearer

## Future Enhancements

### Potential Additions
1. **Token Refresh Flow:** Auto-refresh expired access tokens using refresh token
2. **Password Change:** Allow users to update password
3. **Profile Editing:** Allow users to update name/email
4. **Session Timeout:** Auto-logout after inactivity
5. **Remember Me:** Option to persist login longer
6. **Avatar Upload:** Custom user avatars
7. **Theme Preferences:** Light/dark mode toggle
8. **Notification Settings:** Email/push notification controls
9. **API Key Management:** Generate/revoke personal API keys in UI
10. **Two-Factor Authentication:** Add 2FA for enhanced security

### Security Considerations
- ✅ Never log or display JWT tokens
- ✅ Clear sensitive data on logout
- ✅ Validate tokens server-side on every request
- ✅ Use HTTPS in production (required for JWT)
- ⚠️ Implement rate limiting on auth endpoints (recommended)
- ⚠️ Add CSRF protection for token refresh (recommended)
- ⚠️ Consider token blacklisting on logout (optional)
- ⚠️ Add account lockout after failed login attempts (recommended)
