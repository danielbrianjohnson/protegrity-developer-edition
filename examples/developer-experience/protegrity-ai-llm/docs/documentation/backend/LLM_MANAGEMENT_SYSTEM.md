# LLM, Agent, and Tool Management System

## Overview

The application now uses a **database-driven configuration system** for managing LLMs, AI agents, and tools instead of hardcoded constants. This provides flexibility, scalability, and easy management through Django Admin.

---

## What Was Created

### 1. **Database Models** (`models.py`)

#### **LLMProvider**
- Stores all available LLM configurations (Fin AI, Bedrock Claude, GPT-4, etc.)
- Fields: name, provider_type, model_identifier, pricing, capabilities
- Enable/disable models without code changes
- Track costs, token limits, streaming support

#### **Agent**
- Pre-configured AI assistants with specific roles
- Links to default LLM and allowed LLMs
- System prompts define personality and expertise
- Access to specific tools
- Examples: "Data Protection Expert", "General Assistant"

#### **Tool**
- External tools/APIs agents can use
- Protegrity data protection tools
- Function schemas for tool calling
- Per-tool authentication and configuration
- Examples: "Protegrity Redaction", "Data Classification"

### 2. **Django Admin Interface** (`admin.py`)

**Comprehensive management for all entities:**

- **LLMProviderAdmin**: Manage models, pricing, enable/disable
- **AgentAdmin**: Configure agents, assign tools, set prompts
- **ToolAdmin**: Manage tool definitions and permissions
- Visual status indicators (● active, ○ inactive)
- Bulk actions (activate, deactivate)
- Search and filtering capabilities

### 3. **API Endpoints** (`views.py`, `urls.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models/` | GET | List all active LLM providers |
| `/api/agents/` | GET | List all active AI agents |
| `/api/tools/` | GET | List all available tools |

All endpoints fetch from database dynamically.

### 4. **Data Seeding Command**

```bash
python manage.py seed_llm_data
python manage.py seed_llm_data --clear  # Clear and reseed
```

**Seeds:**
- 3 LLM providers (Fin AI, Bedrock Claude, GPT-4)
- 3 Protegrity tools (Redact, Classify, Guardrails)
- 2 AI agents (Data Protection Expert, General Assistant)

---

## Usage Instructions

### Step 1: Run Seeding Command

```bash
cd backend
python manage.py seed_llm_data
```

**Output:**
```
Seeding LLM Providers...
  ✓ Created: Fin AI
  ✓ Created: Claude 3.5 Sonnet
  ○ Created: GPT-4

Seeding Tools...
  ✓ Created: Protegrity Data Redaction
  ✓ Created: Protegrity Data Classification
  ✓ Created: Protegrity Semantic Guardrails

Seeding Agents...
  ✓ Created: Data Protection Expert (3 tools)
  ✓ Created: General Assistant (0 tools)

✓ Database seeded successfully!
```

### Step 2: Access Django Admin

```bash
python manage.py runserver
```

Navigate to: **http://localhost:8000/admin/**

**Management Options:**
1. **LLM Providers** - Add new models, adjust pricing, enable/disable
2. **Agents** - Create specialized assistants, assign tools
3. **Tools** - Add new integrations, update function schemas

### Step 3: Frontend Integration

The frontend now fetches from these APIs:
- Models are loaded from `/api/models/`
- Future: Agents from `/api/agents/`
- Future: Tools from `/api/tools/`

---

## Benefits

### 1. **No Code Changes for Model Management**
- Add GPT-4, Gemini, or any new LLM via admin
- No deployment required

### 2. **Role-Based Agents**
- Create domain-specific assistants
- Each agent has unique capabilities and tools

### 3. **Tool Ecosystem**
- Agents can access different tools
- Easy to add new integrations

### 4. **Cost Tracking**
- Per-model pricing stored in database
- Future: Usage analytics and billing

### 5. **Multi-Tenancy Ready**
- Can restrict models/agents per user
- Per-organization tool access

---

## Example: Adding a New LLM

**Via Django Admin:**

1. Go to **LLM Providers** → **Add LLM Provider**
2. Fill in:
   - **ID**: `gpt-4-turbo`
   - **Name**: `GPT-4 Turbo`
   - **Provider Type**: `OpenAI`
   - **Model Identifier**: `gpt-4-turbo-preview`
   - **Is Active**: ✓
   - **Max Tokens**: `128000`
   - **Requires Polling**: ✗
   - **Supports Streaming**: ✓
3. Save

**Result:** Immediately available in frontend model selector!

---

## Database Schema

```
llm_providers
├── id (PK, varchar)
├── name
├── provider_type (openai, anthropic, bedrock, etc.)
├── model_identifier
├── is_active
├── requires_polling
├── supports_streaming
├── max_tokens
├── cost_per_1k_input_tokens
├── cost_per_1k_output_tokens
├── configuration (JSON)
└── display_order

agents
├── id (PK, varchar)
├── name
├── description
├── system_prompt
├── default_llm (FK → llm_providers)
├── allowed_llms (M2M → llm_providers)
├── is_active
├── icon
├── color
└── configuration (JSON)

tools
├── id (PK, varchar)
├── name
├── tool_type (protegrity, api, function, etc.)
├── description
├── function_schema (JSON)
├── is_active
├── requires_auth
├── configuration (JSON)
└── agents (M2M → agents)
```

---

## Next Steps

1. ✅ **Run the seed command** to populate initial data
2. ✅ **Test the APIs** - `/api/models/`, `/api/agents/`, `/api/tools/`
3. ⏭️ **Update frontend** - Fetch agents and tools dynamically
4. ⏭️ **Add agent selector** - Let users choose specialized assistants
5. ⏭️ **Implement tool calling** - Enable agents to use Protegrity tools

---

## API Examples

### Fetch Models
```bash
curl http://localhost:8000/api/models/
```

### Fetch Agents
```bash
curl http://localhost:8000/api/agents/
```

### Fetch Tools
```bash
curl http://localhost:8000/api/tools/
```

---

## Architecture

```
┌─────────────┐
│   Django    │
│   Admin     │ ← Manage LLMs, Agents, Tools
└─────────────┘
      │
      ↓
┌─────────────┐
│  Database   │
│  (Models)   │ ← Single source of truth
└─────────────┘
      │
      ↓
┌─────────────┐
│  REST API   │ ← `/api/models/`, `/api/agents/`, `/api/tools/`
└─────────────┘
      │
      ↓
┌─────────────┐
│   React     │
│  Frontend   │ ← Dynamically fetches configuration
└─────────────┘
```

---

## Summary

You now have a **production-grade, database-driven LLM management system** that:
- ✅ Stores all configuration in PostgreSQL/SQLite
- ✅ Provides admin interface for easy management
- ✅ Exposes REST APIs for frontend consumption
- ✅ Supports multiple models, agents, and tools
- ✅ Enables rapid expansion without code changes
- ✅ Ready for multi-tenancy and advanced features

**All managed through Django Admin - no code deployments needed!**
