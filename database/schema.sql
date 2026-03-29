-- =====================================================
-- CRM Digital FTE - PostgreSQL Database Schema
-- Updated for asyncpg compatibility
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable vector extension (optional - for semantic search)
-- Skipping for basic setup - vector column will be TEXT instead

-- =====================================================
-- 1. CUSTOMERS TABLE
-- =====================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    country VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    customer_type VARCHAR(50) DEFAULT 'individual',
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for customers
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_status ON customers(status);
CREATE INDEX idx_customers_created_at ON customers(created_at);

-- =====================================================
-- 2. TICKETS TABLE
-- =====================================================
CREATE TABLE tickets (
    id VARCHAR(50) PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    subject VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'medium',
    escalation_level VARCHAR(10) DEFAULT 'L1',
    escalation_reason TEXT,
    assigned_to VARCHAR(255),
    resolved_by VARCHAR(255),
    resolution_summary TEXT,
    channel VARCHAR(20) NOT NULL,
    source VARCHAR(100),
    tags TEXT[],
    sla_deadline TIMESTAMP WITH TIME ZONE,
    sla_status VARCHAR(20) DEFAULT 'on_track',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for tickets
CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_escalation ON tickets(escalation_level);
CREATE INDEX idx_tickets_assigned ON tickets(assigned_to);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_status_priority ON tickets(status, priority);

-- =====================================================
-- 3. MESSAGES TABLE
-- =====================================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id VARCHAR(50) REFERENCES tickets(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL,
    sender_id VARCHAR(255),
    content TEXT NOT NULL,
    content_html TEXT,
    channel VARCHAR(20) NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    attachment_urls TEXT[],
    sentiment VARCHAR(20),
    sentiment_score DECIMAL(3,2),
    is_internal BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for messages
CREATE INDEX idx_messages_ticket ON messages(ticket_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- =====================================================
-- 4. CONVERSATIONS TABLE
-- =====================================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    ticket_id VARCHAR(50) REFERENCES tickets(id) ON DELETE SET NULL,
    summary TEXT,
    overall_sentiment VARCHAR(20),
    sentiment_trend TEXT,
    topics TEXT[],
    resolution_status VARCHAR(50) DEFAULT 'unresolved',
    customer_satisfaction INTEGER,
    feedback TEXT,
    duration_seconds INTEGER,
    message_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for conversations
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_ticket ON conversations(ticket_id);
CREATE INDEX idx_conversations_started ON conversations(started_at);

-- =====================================================
-- 5. KNOWLEDGE BASE TABLE
-- =====================================================
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE,
    content TEXT NOT NULL,
    content_html TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    tags TEXT[],
    author VARCHAR(255),
    status VARCHAR(20) DEFAULT 'draft',
    views INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    embedding TEXT,
    version INTEGER DEFAULT 1,
    parent_id UUID REFERENCES knowledge_base(id),
    metadata JSONB DEFAULT '{}',
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for knowledge base
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_status ON knowledge_base(status);
CREATE INDEX idx_knowledge_tags ON knowledge_base USING GIN(tags);
CREATE INDEX idx_knowledge_published ON knowledge_base(published_at);

-- =====================================================
-- 6. ESCALATIONS TABLE
-- =====================================================
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id VARCHAR(50) REFERENCES tickets(id) ON DELETE CASCADE,
    from_level VARCHAR(10) NOT NULL,
    to_level VARCHAR(10) NOT NULL,
    reason TEXT NOT NULL,
    triggered_by VARCHAR(50) NOT NULL,
    triggered_by_id VARCHAR(255),
    assigned_to VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    notes TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for escalations
CREATE INDEX idx_escalations_ticket ON escalations(ticket_id);
CREATE INDEX idx_escalations_status ON escalations(status);
CREATE INDEX idx_escalations_assigned ON escalations(assigned_to);
CREATE INDEX idx_escalations_created ON escalations(created_at);

-- =====================================================
-- 7. CHANNEL CONFIGURATIONS TABLE
-- =====================================================
CREATE TABLE channel_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_name VARCHAR(50) NOT NULL UNIQUE,
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL DEFAULT '{}',
    webhook_url VARCHAR(500),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active',
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default channel configs
INSERT INTO channel_configs (channel_name, config) VALUES
('gmail', '{"auto_reply": true, "signature": "TechCorp Support"}'),
('whatsapp', '{"auto_reply": true, "business_hours": "24/7"}'),
('webform', '{"auto_reply": true, "confirmation": true}');

-- =====================================================
-- 8. ANALYTICS TABLE
-- =====================================================
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    customer_id UUID REFERENCES customers(id),
    ticket_id VARCHAR(50) REFERENCES tickets(id),
    channel VARCHAR(20),
    metric_name VARCHAR(100),
    metric_value DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for analytics
CREATE INDEX idx_analytics_event ON analytics(event_type);
CREATE INDEX idx_analytics_customer ON analytics(customer_id);
CREATE INDEX idx_analytics_created ON analytics(created_at);
CREATE INDEX idx_analytics_metric ON analytics(metric_name);

-- =====================================================
-- 9. AGENTS TABLE
-- =====================================================
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'support',
    team VARCHAR(100),
    escalation_level VARCHAR(10) DEFAULT 'L2',
    max_concurrent_tickets INTEGER DEFAULT 10,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for agents
CREATE INDEX idx_agents_email ON agents(email);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_team ON agents(team);

-- =====================================================
-- 10. SLA_CONFIG TABLE
-- =====================================================
CREATE TABLE sla_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    priority VARCHAR(20) NOT NULL UNIQUE,
    first_response_minutes INTEGER NOT NULL,
    resolution_hours INTEGER NOT NULL,
    business_hours_only BOOLEAN DEFAULT FALSE,
    description TEXT
);

-- Insert default SLA configs
INSERT INTO sla_config (priority, first_response_minutes, resolution_hours, business_hours_only, description) VALUES
('low', 60, 48, FALSE, 'Low priority - 1 hour first response, 48 hour resolution'),
('medium', 30, 24, FALSE, 'Medium priority - 30 min first response, 24 hour resolution'),
('high', 15, 8, FALSE, 'High priority - 15 min first response, 8 hour resolution'),
('urgent', 5, 2, FALSE, 'Urgent priority - 5 min first response, 2 hour resolution');

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_channel_configs_updated_at BEFORE UPDATE ON channel_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS
-- =====================================================

-- Active tickets view
CREATE VIEW active_tickets AS
SELECT
    t.id,
    t.subject,
    t.status,
    t.priority,
    t.escalation_level,
    t.assigned_to,
    c.name AS customer_name,
    c.email AS customer_email,
    t.created_at,
    COUNT(m.id) AS message_count
FROM tickets t
LEFT JOIN customers c ON t.customer_id = c.id
LEFT JOIN messages m ON t.id = m.ticket_id
WHERE t.status NOT IN ('resolved', 'closed')
GROUP BY t.id, c.name, c.email;

-- Ticket statistics view
CREATE VIEW ticket_stats AS
SELECT
    status,
    priority,
    COUNT(*) AS count,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/3600) AS avg_resolution_hours
FROM tickets
GROUP BY status, priority;

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function to create ticket ID
CREATE OR REPLACE FUNCTION generate_ticket_id()
RETURNS TRIGGER AS $$
BEGIN
    NEW.id := 'TKT-' || TO_CHAR(NEW.created_at, 'YYYYMMDDHH24MISS');
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to get customer stats
CREATE OR REPLACE FUNCTION get_customer_stats(p_customer_id UUID)
RETURNS TABLE (
    total_tickets BIGINT,
    open_tickets BIGINT,
    resolved_tickets BIGINT,
    avg_satisfaction DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total_tickets,
        COUNT(*) FILTER (WHERE status IN ('open', 'in_progress')) AS open_tickets,
        COUNT(*) FILTER (WHERE status IN ('resolved', 'closed')) AS resolved_tickets,
        AVG(customer_satisfaction) AS avg_satisfaction
    FROM tickets t
    LEFT JOIN conversations c ON t.id = c.ticket_id
    WHERE t.customer_id = p_customer_id;
END;
$$ language 'plpgsql';

-- =====================================================
-- SEED DATA (For Testing)
-- =====================================================

-- Sample customers
INSERT INTO customers (email, phone, name, company, customer_type) VALUES
('john@example.com', '+1234567890', 'John Doe', 'Acme Corp', 'business'),
('sarah@company.com', '+9876543210', 'Sarah Smith', 'Tech Inc', 'enterprise'),
('mike@startup.io', '+1122334455', 'Mike Johnson', 'Startup IO', 'business');

-- =====================================================
-- END OF SCHEMA
-- =====================================================
