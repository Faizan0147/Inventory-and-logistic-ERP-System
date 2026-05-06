# Conversational Memory Implementation Plan

## Overview
Transform the ERP chat system from in-memory sessions to persistent conversation history with a side panel UI similar to Claude/ChatGPT.

---

## 🎯 Goals
1. **Persistent Storage**: Store all conversations and messages in PostgreSQL
2. **Conversation Management**: List, view, delete, and rename conversations
3. **Side Panel UI**: Display conversation history with search and filtering
4. **Memory Context**: Load previous messages when resuming a conversation
5. **Auto-titling**: Generate meaningful conversation titles from first message
6. **User Isolation**: Each user sees only their own conversations

---

## 📊 Database Changes

### New Tables

#### 1. `chat_conversations`
```sql
- conversation_id (TEXT, PK)
- user_id (TEXT, FK -> users)
- title (VARCHAR(200), default: 'New Conversation')
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP) -- auto-updates on new messages
- deleted (BOOLEAN, default: FALSE) -- soft delete
```

**Purpose**: Store conversation metadata and enable conversation listing

#### 2. `chat_messages`
```sql
- message_id (TEXT, PK)
- conversation_id (TEXT, FK -> chat_conversations)
- role (VARCHAR(20)) -- 'user', 'assistant', 'system'
- content (TEXT)
- created_at (TIMESTAMP)
```

**Purpose**: Store individual messages in chronological order

### Indexes
- `idx_conversations_user`: Fast user conversation listing (user_id, updated_at DESC)
- `idx_messages_conversation`: Fast message retrieval (conversation_id, created_at ASC)
- `idx_conversations_deleted`: Filter out deleted conversations

### Triggers
- `trigger_update_conversation_timestamp`: Auto-update conversation.updated_at when new message added

---

## 🔧 Backend Changes

### 1. Repository Layer (NEW)

**File**: `app/repositories/chat_repo.py`

**Functions**:
```python
# Conversation Management
- create_conversation(user_id, title) -> dict
- get_conversation(conversation_id, user_id) -> dict | None
- list_conversations(user_id, limit, offset) -> list[dict]
- update_conversation_title(conversation_id, user_id, title) -> bool
- delete_conversation(conversation_id, user_id) -> bool
- conversation_exists(conversation_id, user_id) -> bool

# Message Management
- add_message(conversation_id, role, content) -> dict
- get_messages(conversation_id, limit) -> list[dict]
- get_message_count(conversation_id) -> int
- delete_all_messages(conversation_id) -> bool

# Utilities
- generate_conversation_title(first_message) -> str
```

**Key Features**:
- All queries scoped by `user_id` for security
- Soft delete support
- Pagination for large conversation lists
- Transaction support for atomic operations

---

### 2. DTO Updates

**File**: `app/dto/chat.py`

**New Models**:
```python
# Request Models
- ChatRequest (existing, enhanced with conversation_id)
- CreateConversationRequest(title: str | None)
- UpdateConversationRequest(title: str)

# Response Models
- ChatResponse (existing)
- MessageResponse(message_id, role, content, created_at)
- ConversationResponse(conversation_id, title, created_at, updated_at, message_count)
- ConversationListResponse(conversations: list, total: int, page: int, page_size: int)
- ConversationDetailResponse(conversation, messages: list)
```

---

### 3. Chat Agent Updates

**File**: `app/langchain_agent/chat.py`

**Changes**:
```python
# REMOVE: In-memory _conversation_store dict

# UPDATE: chat_with_langchain()
1. Load message history from database (not memory)
2. After agent response, save both user message and assistant reply to DB
3. Auto-generate conversation title if it's the first message
4. Return conversation_id in response

# UPDATE: clear_session()
- Now calls chat_repo.delete_conversation() instead of dict.pop()

# NEW: load_conversation_history()
- Fetch messages from database
- Format for LangChain agent
- Support message limit (e.g., last 50 messages)
```

**Flow**:
```
1. User sends message with conversation_id (or None for new)
2. If conversation_id is None:
   - Create new conversation in DB
   - Generate conversation_id
3. Load message history from DB (last N messages)
4. Append new user message to history
5. Send to LangChain agent
6. Save user message to DB
7. Save assistant reply to DB
8. If first message, generate and update title
9. Return reply + conversation_id
```

---

### 4. API Routes

**File**: `app/routes/langchain_chat.py`

**Endpoints**:

#### Chat Operations
```
POST   /chat/message
  - Send message (create new conversation or continue existing)
  - Body: { prompt, conversation_id? }
  - Returns: { reply, conversation_id }

POST   /chat/conversations
  - Create new empty conversation
  - Body: { title? }
  - Returns: { conversation_id, title, created_at }
```

#### Conversation Management
```
GET    /chat/conversations
  - List user's conversations (paginated)
  - Query: page=1, page_size=20, search?
  - Returns: { conversations[], total, page, page_size }

GET    /chat/conversations/{conversation_id}
  - Get conversation details with messages
  - Returns: { conversation, messages[] }

PATCH  /chat/conversations/{conversation_id}
  - Update conversation title
  - Body: { title }
  - Returns: { success: true }

DELETE /chat/conversations/{conversation_id}
  - Soft delete conversation
  - Returns: 204 No Content
```

#### Message Operations
```
GET    /chat/conversations/{conversation_id}/messages
  - Get messages for a conversation
  - Query: limit=50
  - Returns: { messages[] }

DELETE /chat/conversations/{conversation_id}/messages
  - Clear all messages in conversation
  - Returns: 204 No Content
```

---

## 🎨 Frontend/UI Changes

### 1. Chat UI Structure

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  [☰] GodaamX ERP Chat              [User Menu]  │
├──────────────┬──────────────────────────────────┤
│              │                                   │
│  Sidebar     │     Chat Area                    │
│  (300px)     │     (Flex)                       │
│              │                                   │
│  [+ New]     │  ┌─────────────────────────┐    │
│              │  │ User: Show me invoices  │    │
│  Today       │  └─────────────────────────┘    │
│  • Conv 1    │  ┌─────────────────────────┐    │
│  • Conv 2    │  │ AI: Here are your...    │    │
│              │  └─────────────────────────┘    │
│  Yesterday   │                                   │
│  • Conv 3    │  [Type your message...]          │
│              │                                   │
└──────────────┴──────────────────────────────────┘
```

### 2. Sidebar Components

**Conversation List**:
- Group by date (Today, Yesterday, Last 7 days, Last 30 days, Older)
- Show conversation title (truncated)
- Highlight active conversation
- Hover actions: Rename, Delete
- Search/filter conversations
- Infinite scroll or pagination

**New Conversation Button**:
- Creates empty conversation
- Switches to new chat view
- Clears current chat area

### 3. Chat Area Components

**Message Display**:
- User messages (right-aligned, different color)
- Assistant messages (left-aligned)
- Timestamp on hover
- Copy message button
- Regenerate response button (future)

**Input Area**:
- Text input with auto-resize
- Send button
- Character count
- File upload (future)

### 4. Conversation Actions

**Rename**:
- Click title or use context menu
- Inline edit or modal
- Auto-save on blur/enter

**Delete**:
- Confirmation dialog
- Soft delete (can be recovered by admin)
- Remove from sidebar immediately

**Clear Messages**:
- Keep conversation but delete all messages
- Confirmation required

---

## 🔄 API Integration Flow

### Starting New Conversation
```javascript
// Frontend
1. User clicks "New Chat"
2. Frontend generates temp conversation_id (optional)
3. User types first message
4. POST /chat/message { prompt, conversation_id: null }
5. Backend creates conversation, saves messages, returns conversation_id
6. Frontend updates URL: /chat/{conversation_id}
7. Frontend adds conversation to sidebar
```

### Continuing Conversation
```javascript
// Frontend
1. User clicks conversation in sidebar
2. GET /chat/conversations/{conversation_id}/messages
3. Display messages in chat area
4. User types new message
5. POST /chat/message { prompt, conversation_id }
6. Backend loads history, gets AI response, saves messages
7. Frontend appends new messages to chat
```

### Loading Sidebar
```javascript
// Frontend (on page load)
1. GET /chat/conversations?page=1&page_size=20
2. Group conversations by date
3. Render in sidebar
4. Implement infinite scroll for more
```

---

## 🔐 Security Considerations

### Access Control
- All queries filtered by `current_user.user_id`
- Users can only access their own conversations
- Conversation ownership verified on every request

### Data Privacy
- Messages contain business data - ensure proper encryption at rest
- Consider adding `is_sensitive` flag for PII detection
- Implement data retention policies

### Rate Limiting
- Limit messages per minute per user
- Limit conversation creation rate
- Prevent abuse of title generation

---

## 📝 Implementation Steps

### Phase 1: Database & Repository (Backend Foundation)
1. ✅ Create `Database/chat_conversations.sql`
2. Run migration to create tables
3. Create `app/repositories/chat_repo.py`
4. Test repository functions with sample data

### Phase 2: DTO & Models
1. Update `app/dto/chat.py` with new models
2. Add validation rules
3. Test serialization/deserialization

### Phase 3: Chat Agent Integration
1. Update `app/langchain_agent/chat.py`
2. Replace in-memory storage with DB calls
3. Implement conversation history loading
4. Add auto-title generation
5. Test with existing chat flow

### Phase 4: API Routes
1. Update `app/routes/langchain_chat.py`
2. Add new endpoints for conversation management
3. Add pagination and filtering
4. Test all endpoints with Postman/curl

### Phase 5: Frontend UI (Separate Task)
1. Create sidebar component
2. Create conversation list component
3. Update chat area to load from conversation
4. Add conversation actions (rename, delete)
5. Implement search and filtering
6. Add loading states and error handling

### Phase 6: Testing & Optimization
1. Test concurrent users
2. Test large conversation histories
3. Optimize database queries
4. Add caching if needed
5. Load testing

### Phase 7: Polish & Features
1. Add conversation search
2. Add export conversation feature
3. Add conversation sharing (optional)
4. Add conversation templates
5. Add analytics (message count, usage stats)

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] Create conversation
- [ ] Add messages to conversation
- [ ] Load conversation history
- [ ] List conversations with pagination
- [ ] Update conversation title
- [ ] Delete conversation (soft delete)
- [ ] User isolation (can't access other user's conversations)
- [ ] Handle non-existent conversation_id
- [ ] Handle deleted conversations
- [ ] Auto-title generation
- [ ] Timestamp updates

### API Tests
- [ ] POST /chat/message (new conversation)
- [ ] POST /chat/message (existing conversation)
- [ ] GET /chat/conversations (list)
- [ ] GET /chat/conversations/{id} (detail)
- [ ] PATCH /chat/conversations/{id} (rename)
- [ ] DELETE /chat/conversations/{id} (delete)
- [ ] GET /chat/conversations/{id}/messages
- [ ] Pagination works correctly
- [ ] Authentication required
- [ ] Authorization enforced

### Frontend Tests
- [ ] Sidebar loads conversations
- [ ] Click conversation loads messages
- [ ] Send message updates chat
- [ ] New conversation button works
- [ ] Rename conversation works
- [ ] Delete conversation works
- [ ] Search conversations works
- [ ] Responsive design
- [ ] Loading states
- [ ] Error handling

---

## 📦 Dependencies

### Backend (Already Installed)
- FastAPI
- asyncpg (PostgreSQL driver)
- LangChain
- Pydantic

### Frontend (To Be Determined)
- React/Vue/Vanilla JS
- HTTP client (fetch/axios)
- Date formatting library (date-fns/dayjs)
- UI components (optional: shadcn, MUI, etc.)

---

## 🚀 Deployment Considerations

### Database Migration
```bash
# Run migration
psql -U your_user -d your_db -f Database/chat_conversations.sql

# Verify tables created
psql -U your_user -d your_db -c "\dt chat_*"
```

### Environment Variables
- No new env vars needed (uses existing DATABASE_URL)

### Monitoring
- Track conversation creation rate
- Monitor message volume
- Alert on failed message saves
- Track average conversation length

---

## 🔮 Future Enhancements

### Phase 2 Features
1. **Conversation Folders/Tags**: Organize conversations by project/topic
2. **Conversation Search**: Full-text search across messages
3. **Export Conversations**: Download as PDF/JSON
4. **Conversation Sharing**: Share read-only link with team
5. **Message Reactions**: Like/dislike messages for feedback
6. **Conversation Templates**: Pre-defined prompts for common tasks
7. **Voice Input**: Speech-to-text for messages
8. **Multi-modal**: Support images in conversations
9. **Conversation Analytics**: Usage stats, popular queries
10. **Conversation Archiving**: Auto-archive old conversations

### Advanced Features
1. **Conversation Branching**: Fork conversation at any point
2. **Collaborative Conversations**: Multiple users in one conversation
3. **Conversation Summaries**: AI-generated summary of long conversations
4. **Smart Suggestions**: Suggest next questions based on context
5. **Conversation Insights**: Extract action items, decisions, data points

---

## 📚 API Documentation Examples

### Example: Send Message
```bash
POST /api/v1/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "Show me all pending invoices",
  "conversation_id": "conv_abc123"  # null for new conversation
}

Response:
{
  "reply": "Here are your pending invoices...",
  "conversation_id": "conv_abc123"
}
```

### Example: List Conversations
```bash
GET /api/v1/chat/conversations?page=1&page_size=20
Authorization: Bearer <token>

Response:
{
  "conversations": [
    {
      "conversation_id": "conv_abc123",
      "title": "Invoice Analysis",
      "created_at": "2026-05-06T10:30:00Z",
      "updated_at": "2026-05-06T14:22:00Z",
      "message_count": 12
    },
    ...
  ],
  "total": 45,
  "page": 1,
  "page_size": 20
}
```

### Example: Rename Conversation
```bash
PATCH /api/v1/chat/conversations/conv_abc123
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Q1 Invoice Review"
}

Response:
{
  "success": true
}
```

---

## 🎯 Success Metrics

### Technical Metrics
- Message save latency < 100ms
- Conversation load time < 500ms
- Support 1000+ messages per conversation
- Support 100+ concurrent users

### User Experience Metrics
- Users can find previous conversations easily
- Conversation context maintained across sessions
- No data loss
- Intuitive UI similar to Claude/ChatGPT

---

## 📋 Summary

This plan transforms your ERP chat from a stateless, session-based system to a fully persistent, conversation-based system with:

✅ **Database persistence** for all conversations and messages  
✅ **User-scoped access** for security and privacy  
✅ **RESTful API** for conversation management  
✅ **Side panel UI** for easy navigation  
✅ **Auto-titling** for better organization  
✅ **Scalable architecture** for future enhancements  

The implementation follows your existing patterns (repositories, DTOs, routes) and integrates seamlessly with your current LangChain agent setup.

---

**Next Steps**: 
1. Review and approve this plan
2. Run database migration
3. Implement backend (Phases 1-4)
4. Test backend thoroughly
5. Implement frontend UI (Phase 5)
6. Deploy and monitor

**Estimated Timeline**: 
- Backend: 2-3 days
- Frontend: 2-3 days  
- Testing & Polish: 1-2 days
- **Total: 5-8 days** (for one developer)
