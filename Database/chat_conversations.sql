-- Chat Conversations and Messages Tables
-- This enables persistent conversation history similar to Claude/ChatGPT

CREATE TABLE IF NOT EXISTS chat_conversations (
    conversation_id  TEXT        PRIMARY KEY,
    user_id          TEXT        NOT NULL,
    title            VARCHAR(200) NOT NULL DEFAULT 'New Conversation',
    is_titled        BOOLEAN     NOT NULL DEFAULT FALSE,
    message_count    INT         NOT NULL DEFAULT 0,
    created_at       TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    deleted          BOOLEAN     NOT NULL DEFAULT FALSE,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    message_id       TEXT        PRIMARY KEY,
    conversation_id  TEXT        NOT NULL,
    role             VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content          TEXT        NOT NULL,
    created_at       TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id)
        REFERENCES chat_conversations(conversation_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_user
    ON chat_conversations(user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_messages_conversation
    ON chat_messages(conversation_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_conversations_deleted
    ON chat_conversations(user_id, deleted)
    WHERE deleted = FALSE;

-- Function to auto-update updated_at and message_count on new message
CREATE OR REPLACE FUNCTION update_conversation_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_conversations
    SET updated_at    = CURRENT_TIMESTAMP,
        message_count = message_count + 1
    WHERE conversation_id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to fire on every new message insert
DROP TRIGGER IF EXISTS trigger_update_conversation_on_message ON chat_messages;
CREATE TRIGGER trigger_update_conversation_on_message
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_on_message();
