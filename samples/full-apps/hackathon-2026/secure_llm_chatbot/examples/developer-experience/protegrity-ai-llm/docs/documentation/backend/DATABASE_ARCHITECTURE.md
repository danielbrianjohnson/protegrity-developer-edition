# Database Architecture Documentation

## Overview

Enterprise-grade database design for the Protegrity AI Chat application using Django ORM with PostgreSQL (SQLite for development).

## Design Principles

1. **Scalability**: Indexed fields, efficient queries, pagination
2. **Data Integrity**: Foreign keys, constraints, soft deletes
3. **Flexibility**: JSON fields for metadata without schema changes
4. **Security**: UUID primary keys prevent enumeration attacks
5. **Auditability**: Timestamps on all records for compliance

---

## Database Schema

### Conversations Table

**Purpose**: Stores chat conversation threads.

**Table Name**: `conversations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier (prevents enumeration) |
| `title` | VARCHAR(255) | NOT NULL, INDEXED | Conversation title (auto-generated from first message) |
| `model_id` | VARCHAR(50) | NOT NULL, INDEXED | LLM model used (fin, bedrock-claude) |
| `created_at` | TIMESTAMP | NOT NULL, INDEXED | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, INDEXED | Last activity timestamp |
| `deleted_at` | TIMESTAMP | NULL, INDEXED | Soft delete timestamp (NULL if active) |

**Indexes**:
- `conv_active_idx`: Composite index on (`updated_at` DESC, `deleted_at`) for efficient active conversation queries

**Business Logic**:
- `deleted_at IS NULL` = Active conversation
- `updated_at` auto-updates on any message addition
- `title` defaults to "New chat", updated with first user message

---

### Messages Table

**Purpose**: Stores individual messages within conversations.

**Table Name**: `messages`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `conversation_id` | UUID | FOREIGN KEY → conversations.id, INDEXED | Parent conversation (CASCADE delete) |
| `role` | VARCHAR(20) | NOT NULL, INDEXED | Message role: 'user', 'assistant', 'system' |
| `content` | TEXT | NOT NULL | Message text content |
| `protegrity_data` | JSON | NULL | Protegrity metadata (PII detections, redactions) |
| `pending` | BOOLEAN | NOT NULL, DEFAULT false, INDEXED | Awaiting LLM response |
| `blocked` | BOOLEAN | NOT NULL, DEFAULT false, INDEXED | Blocked by guardrails |
| `created_at` | TIMESTAMP | NOT NULL, INDEXED | Message timestamp |
| `deleted_at` | TIMESTAMP | NULL | Soft delete timestamp |

**Indexes**:
- `msg_conv_time_idx`: Composite index on (`conversation_id`, `created_at`) for efficient message retrieval per conversation

**Business Logic**:
- Foreign key cascade: Deleting conversation hard-deletes all messages
- Soft delete: `soft_delete()` method on Conversation sets `deleted_at` on all messages
- `pending=true`: Used for async LLM responses (Fin AI)
- `blocked=true`: Message rejected by Protegrity guardrails

---

## Data Flow

### Creating a Conversation

```
1. Frontend: POST /api/conversations/
   Body: { "model_id": "fin" }

2. Backend: Creates Conversation record
   - id: auto-generated UUID
   - title: "New chat"
   - model_id: from request
   - created_at, updated_at: current timestamp

3. Response: Conversation object with empty messages array
```

### Adding Messages

```
1. Frontend: POST /api/chat/
   Body: { 
     "conversation_id": "uuid",
     "message": "Hello",
     "model_id": "fin"
   }

2. Backend: 
   a. Process message through Protegrity
   b. Create Message record (role='user')
   c. Call LLM API
   d. Create Message record (role='assistant')
   e. Update conversation.updated_at

3. Frontend: Polls /api/chat/poll/<id>/ for async responses
```

### Fetching Conversations

```
1. Frontend: GET /api/conversations/
   
2. Backend Query:
   SELECT * FROM conversations
   WHERE deleted_at IS NULL
   ORDER BY updated_at DESC
   LIMIT 50;

3. Response: Paginated list of conversations
```

### Fetching Single Conversation with Messages

```
1. Frontend: GET /api/conversations/<id>/

2. Backend Query (optimized with prefetch_related):
   SELECT * FROM conversations WHERE id = <id>;
   SELECT * FROM messages 
   WHERE conversation_id = <id> AND deleted_at IS NULL
   ORDER BY created_at ASC;

3. Response: Conversation with messages array
```

---

## Performance Optimizations

### Indexing Strategy

1. **Primary Lookups**: All UUID primary keys have implicit index
2. **Time-based Queries**: `created_at`, `updated_at` indexed for sorting
3. **Filtering**: `deleted_at`, `model_id`, `role`, `pending`, `blocked` indexed
4. **Composite Indexes**: Optimize multi-column queries
   - `(updated_at, deleted_at)` for active conversations
   - `(conversation_id, created_at)` for conversation messages

### Query Optimization

1. **select_related()**: Used for forward ForeignKey relationships
2. **prefetch_related()**: Used for reverse relationships (conversation → messages)
3. **only()**: Fetch only needed fields for list views
4. **Pagination**: Default 50 items per page, prevents large result sets

### Example Optimized Query

```python
# Fetch conversations with message counts (single query)
conversations = Conversation.objects.filter(
    deleted_at__isnull=True
).annotate(
    message_count=Count('messages', filter=Q(messages__deleted_at__isnull=True))
).order_by('-updated_at')[:50]

# Fetch conversation with messages (2 queries total)
conversation = Conversation.objects.prefetch_related(
    Prefetch(
        'messages',
        queryset=Message.objects.filter(deleted_at__isnull=True).order_by('created_at')
    )
).get(id=conversation_id)
```

---

## Soft Delete Pattern

### Why Soft Deletes?

1. **Data Recovery**: Restore accidentally deleted conversations
2. **Compliance**: Meet data retention requirements
3. **Analytics**: Analyze user behavior including deleted content
4. **Audit Trail**: Track what was deleted and when

### Implementation

```python
# Soft delete a conversation
conversation.soft_delete()
# Sets deleted_at on conversation and all messages

# Query active conversations
Conversation.objects.filter(deleted_at__isnull=True)

# Restore a conversation (admin only)
conversation.deleted_at = None
conversation.save()
```

---

## Scaling Considerations

### Current Implementation (Suitable for)

- **Users**: Up to 100,000
- **Conversations**: Up to 10 million
- **Messages**: Up to 100 million
- **Database**: PostgreSQL with 100GB storage

### Horizontal Scaling (Future)

1. **Read Replicas**: Distribute read queries across multiple databases
2. **Sharding**: Partition by user_id or date range
3. **Caching**: Redis for frequently accessed conversations
4. **Archival**: Move old conversations to cold storage (S3/Glacier)

### Vertical Scaling

1. **Connection Pooling**: PgBouncer (500+ concurrent connections)
2. **Query Caching**: Django cache framework
3. **Indexes**: Add specialized indexes based on query patterns
4. **Partitioning**: PostgreSQL table partitioning by created_at

---

## Security

### Protections Implemented

1. **UUID Primary Keys**: Prevent enumeration attacks
2. **No Sequential IDs**: Can't guess conversation IDs
3. **Soft Deletes**: Data recoverable but not visible to users
4. **JSON Validation**: Protegrity data sanitized before storage

### Future Enhancements

1. **User Authentication**: Add user_id foreign key to conversations
2. **Row-Level Security**: PostgreSQL RLS for multi-tenant isolation
3. **Encryption at Rest**: Encrypt sensitive fields (content, protegrity_data)
4. **Audit Logging**: Track all data access and modifications

---

## Maintenance

### Regular Tasks

1. **Hard Delete Old Data**: Archive conversations older than 2 years
2. **Vacuum/Analyze**: PostgreSQL maintenance for optimal performance
3. **Index Monitoring**: Check for unused indexes, add missing ones
4. **Backup**: Daily full backups, WAL archiving for point-in-time recovery

### Monitoring Queries

```sql
-- Count active conversations
SELECT COUNT(*) FROM conversations WHERE deleted_at IS NULL;

-- Average messages per conversation
SELECT AVG(message_count) FROM (
    SELECT conversation_id, COUNT(*) as message_count 
    FROM messages 
    WHERE deleted_at IS NULL 
    GROUP BY conversation_id
);

-- Top models by usage
SELECT model_id, COUNT(*) as count 
FROM conversations 
WHERE deleted_at IS NULL 
GROUP BY model_id 
ORDER BY count DESC;

-- Daily conversation creation trend
SELECT DATE(created_at) as date, COUNT(*) as count
FROM conversations
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;
```

---

## Migration Path

### Development → Production

1. **Switch Database**: Change `ENGINE` in settings.py from SQLite to PostgreSQL
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'protegrity_ai',
           'USER': 'app_user',
           'PASSWORD': os.getenv('DB_PASSWORD'),
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

2. **Install psycopg2**: `pip install psycopg2-binary`

3. **Run Migrations**: `python manage.py migrate`

4. **Create Indexes**: Already in migrations, applied automatically

5. **Load Fixtures** (if migrating data): `python manage.py loaddata`

---

## API Endpoints

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete REST API reference.

**Summary**:
- `GET /api/conversations/` - List conversations (paginated)
- `POST /api/conversations/` - Create conversation
- `GET /api/conversations/{id}/` - Get conversation with messages
- `PATCH /api/conversations/{id}/` - Update conversation (title)
- `DELETE /api/conversations/{id}/` - Soft delete conversation
- `POST /api/conversations/{id}/messages/` - Add message (internal)

---

## Testing

### Unit Tests

```bash
# Run all tests
python manage.py test apps.core

# Test specific model
python manage.py test apps.core.tests.test_models

# Test with coverage
coverage run manage.py test apps.core
coverage report
```

### Load Testing

```bash
# Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/conversations/

# Locust
locust -f load_test.py --host=http://localhost:8000
```

---

## Troubleshooting

### Common Issues

**Issue**: Slow conversation list queries
**Solution**: Check `conv_active_idx` index exists, verify `deleted_at IS NULL` filter

**Issue**: N+1 query problem when fetching messages
**Solution**: Use `prefetch_related('messages')` in view

**Issue**: Large JSON fields causing memory issues
**Solution**: Use `defer('protegrity_data')` if not needed, implement field-level compression

---

## Version History

- **v1.0** (2025-12-10): Initial implementation with UUID keys, soft deletes, indexes
