# Task 1: Agent & LLM Tracking - Implementation Summary

## ✅ Completed

### 1. Model Changes (`models.py`)

**Conversation Model:**
- Added `primary_agent` FK to Agent (nullable, SET_NULL on delete)
- Added `primary_llm` FK to LLMProvider (nullable, SET_NULL on delete)
- Keeps `model_id` string for backward compatibility and analytics

**Message Model:**
- Added `agent` FK to Agent (nullable, SET_NULL on delete)
- Added `llm_provider` FK to LLMProvider (nullable, SET_NULL on delete)
- Added indexes: `msg_llm_time_idx` and `msg_agent_time_idx` for analytics queries

**Semantics:**
- `role="user"` → agent and llm_provider are NULL
- `role="assistant"` → both fields populated with actual generator
- Conversation-level fields track user's initial selection
- Message-level fields track actual generators (supports future multi-agent conversations)

### 2. Migrations

Created and applied migration `0003_conversation_primary_agent_conversation_primary_llm_and_more.py`:
```bash
python manage.py makemigrations  # ✅ Created
python manage.py migrate         # ✅ Applied
```

### 3. Serializers (`serializers.py`)

**MessageSerializer:**
- Added `agent` field (SlugRelatedField with id)
- Added `llm_provider` field (SlugRelatedField with id)

**ConversationListSerializer:**
- Added `primary_agent` field
- Added `primary_llm` field

**ConversationDetailSerializer:**
- Added `primary_agent` field
- Added `primary_llm` field
- Nested messages include their agent/llm_provider

### 4. Chat Endpoint (`views.py`)

**Updated `chat()` function:**
- Accepts `agent_id` parameter (optional)
- Accepts `model_id` parameter (optional)
- Looks up Agent and LLMProvider on new conversation creation
- Returns 400 error for invalid agent_id or model_id
- Sets `conversation.primary_agent` and `conversation.primary_llm`
- Documentation updated to reflect new parameters

**Updated message creation:**
- `chat_with_fin()`: Sets agent and llm_provider on assistant messages
- `chat_with_bedrock()`: Sets agent and llm_provider on assistant messages
- Uses `conversation.primary_agent` and `conversation.primary_llm`

**Request Format:**
```json
{
  "message": "user message",
  "conversation_id": "optional-uuid",
  "model_id": "fin",
  "agent_id": "data-protection-expert",
  "protegrity_mode": "redact"
}
```

### 5. Conversation Endpoints (`conversation_views.py`)

**Optimized Queries:**
- `conversation_list_create()`: Added `select_related('primary_agent', 'primary_llm')`
- `conversation_detail()`: Added `select_related` for conversation and nested messages
- Prevents N+1 queries when serializing agent/LLM relationships

**Response Format:**
```json
{
  "id": "uuid",
  "title": "Chat title",
  "model_id": "fin",
  "primary_agent": "data-protection-expert",
  "primary_llm": "fin",
  "messages": [
    {
      "role": "assistant",
      "content": "Response",
      "agent": "data-protection-expert",
      "llm_provider": "fin"
    }
  ]
}
```

### 6. Tests (`test_agent_llm_tracking.py`)

**Test Coverage:**
- ✅ Conversation creation with agent and LLM
- ✅ Message tracking of agent and llm_provider
- ✅ User messages have NULL agent/llm_provider
- ✅ SET_NULL cascade behavior on deletion
- ✅ Serializer field inclusion
- ✅ Analytics queries using indexes
- ✅ Invalid agent_id/model_id validation
- ✅ Multiple agents across conversations

**Run Tests:**
```bash
cd backend
pytest apps/core/tests/test_agent_llm_tracking.py -v
```

## 🎯 Benefits

1. **Analytics**: Track which agents/models users prefer
2. **Billing**: Calculate costs per LLM provider
3. **Audit Trails**: Know exactly which AI generated each response
4. **Performance**: Indexed queries for fast analytics
5. **Future-Proof**: Supports agent/model switching mid-conversation
6. **Data Integrity**: SET_NULL prevents orphaned records

## 📊 Database Schema Changes

```sql
-- Conversation table
ALTER TABLE conversations 
  ADD COLUMN primary_agent_id VARCHAR(50) REFERENCES agents(id) ON DELETE SET NULL,
  ADD COLUMN primary_llm_id VARCHAR(50) REFERENCES llm_providers(id) ON DELETE SET NULL;

-- Message table
ALTER TABLE messages
  ADD COLUMN agent_id VARCHAR(50) REFERENCES agents(id) ON DELETE SET NULL,
  ADD COLUMN llm_provider_id VARCHAR(50) REFERENCES llm_providers(id) ON DELETE SET NULL;

-- Indexes
CREATE INDEX msg_llm_time_idx ON messages (llm_provider_id, created_at);
CREATE INDEX msg_agent_time_idx ON messages (agent_id, created_at);
```

## 🔄 Backward Compatibility

- All new fields are nullable (no data migration required)
- Existing conversations work without agent/LLM
- `model_id` string field preserved for legacy code
- API accepts requests without agent_id/model_id

## 📝 Next Steps

**Frontend Integration:**
- Update `App.jsx` to send `agent_id` and `model_id` in chat requests
- Display "Talking to [Agent] using [Model]" in UI
- Show per-message agent/LLM in hover tooltips (optional)

**Analytics Dashboard (Future):**
- Most popular agents
- LLM usage by time
- Cost breakdown by model
- Agent performance metrics

## 🧪 Testing Example

```python
# Create conversation with agent and LLM
conversation = Conversation.objects.create(
    title="Security Chat",
    model_id="fin",
    primary_agent=data_protection_expert,
    primary_llm=fin_provider
)

# User message (no agent/LLM)
Message.objects.create(
    conversation=conversation,
    role="user",
    content="How do I protect PII?"
)

# Assistant message (tracks generator)
Message.objects.create(
    conversation=conversation,
    role="assistant",
    content="Use Protegrity...",
    agent=conversation.primary_agent,
    llm_provider=conversation.primary_llm
)

# Analytics query
messages_by_agent = Message.objects.filter(
    agent=data_protection_expert
).count()
```

## ✨ Summary

Task 1 successfully implements comprehensive agent and LLM tracking across conversations and messages. The system now records:
- Which agent/model the user selected (conversation level)
- Which agent/model generated each response (message level)
- Full audit trail for compliance and analytics
- Optimized queries for performance

All existing functionality preserved with full backward compatibility.
