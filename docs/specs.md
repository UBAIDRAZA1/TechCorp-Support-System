# Technical Specifications - CRM Digital FTE

## 1. System Overview

### 1.1 Purpose
Build an AI-powered Customer Support Agent (Digital FTE) that handles customer inquiries 24/7 across multiple channels.

### 1.2 Scope
- Email support (Gmail)
- WhatsApp support (Twilio)
- Web form support (Custom React form)
- Automatic response generation
- Intelligent escalation
- Complete CRM database

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CUSTOMER CHANNELS                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│     Gmail       │    WhatsApp     │      Web Form           │
│    (Email)      │   (Twilio)      │    (React/Next.js)      │
└────────┬────────┴────────┬────────┴──────────┬──────────────┘
         │                 │                    │
         ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                     │
│              /api/v1/message  /api/v1/webhook                │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    KAFKA MESSAGE QUEUE                       │
│         incoming_messages  │  outgoing_messages              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT WORKER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Sentiment  │  │  Knowledge  │  │   Response          │  │
│  │  Analysis   │  │   Search    │  │   Generation        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                       │
│  customers | conversations | messages | tickets | kb        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      PHASE 1 (Prototype)                      │
├──────────────────────────────────────────────────────────────┤
│  context/          - Knowledge base documents                │
│  mcp_tools.py      - MCP protocol tools                      │
│  ai_agent.py       - Core AI agent logic                     │
│  main.py           - FastAPI backend                         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    PHASE 2 (Production)                       │
├──────────────────────────────────────────────────────────────┤
│  database/         - PostgreSQL schema & migrations          │
│  backend/          - Production FastAPI application          │
│  frontend/         - React/Next.js web form                  │
│  kafka/            - Kafka consumers/producers               │
│  integrations/     - Gmail & WhatsApp connectors             │
│  kubernetes/       - K8s deployment configs                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Database Schema

### 3.1 ERD

```
┌─────────────────┐       ┌─────────────────┐
│   customers     │       │   tickets       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ email           │       │ customer_id(FK) │
│ phone           │       │ subject         │
│ name            │       │ status          │
│ created_at      │       │ priority        │
│ updated_at      │       │ escalation_level│
└─────────────────┘       │ created_at      │
         │                │ updated_at      │
         │                └─────────────────┘
         │                         │
         │                ┌─────────────────┐
         │                │   messages      │
         │                ├─────────────────┤
         │                │ id (PK)         │
         │                │ ticket_id (FK)  │
         │                │ sender          │
         │                │ content         │
         │                │ channel         │
         │                │ created_at      │
         │                └─────────────────┘
         │
         │                ┌─────────────────┐
         └───────────────▶│ conversations   │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ customer_id(FK) │
                          │ summary         │
                          │ sentiment       │
                          │ created_at      │
                          └─────────────────┘

┌─────────────────┐
│ knowledge_base  │
├─────────────────┤
│ id (PK)         │
│ title           │
│ content         │
│ category        │
│ tags            │
│ created_at      │
└─────────────────┘
```

### 3.2 SQL Schema

```sql
-- Customers Table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    name VARCHAR(255),
    company VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tickets Table
CREATE TABLE tickets (
    id VARCHAR(50) PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    subject VARCHAR(500),
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'medium',
    escalation_level VARCHAR(10) DEFAULT 'L1',
    escalation_reason TEXT,
    assigned_to VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages Table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) REFERENCES tickets(id),
    sender VARCHAR(50), -- 'customer' or 'agent' or 'ai'
    content TEXT,
    channel VARCHAR(20), -- 'email', 'whatsapp', 'web'
    sentiment VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations Table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    summary TEXT,
    sentiment VARCHAR(20),
    resolution VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge Base Table
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    category VARCHAR(100),
    tags TEXT[],
    embedding VECTOR(1536), -- For vector search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_messages_ticket ON messages(ticket_id);
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
```

---

## 4. API Specifications

### 4.1 REST API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | / | Root endpoint | No |
| GET | /health | Health check | No |
| POST | /api/v1/message | Process message | No |
| GET | /api/v1/message/{id} | Get message status | No |
| GET | /api/v1/ticket | List tickets | Yes |
| GET | /api/v1/ticket/{id} | Get ticket | Yes |
| PUT | /api/v1/ticket/{id}/status | Update status | Yes |
| GET | /api/v1/customer/{id}/history | Customer history | Yes |
| POST | /api/v1/webhook/{channel} | Receive webhook | No |
| POST | /api/v1/escalate | Escalate ticket | Yes |
| POST | /api/v1/sentiment | Analyze sentiment | No |
| GET | /api/v1/knowledge/search | Search KB | No |
| GET | /api/v1/stats | System stats | Yes |
| WS | /ws | WebSocket updates | No |

### 4.2 Request/Response Examples

#### POST /api/v1/message
```json
// Request
{
    "customer": "john@example.com",
    "channel": "email",
    "subject": "Cannot login",
    "message": "I forgot my password",
    "priority": "medium"
}

// Response
{
    "ticket_id": "TKT-20240326120000",
    "status": "open",
    "response": "Dear Customer, Let me help you reset your password...",
    "sentiment": {"sentiment": "neutral", "confidence": 0.7},
    "escalated": false,
    "timestamp": "2024-03-26T12:00:00Z"
}
```

---

## 5. Integration Specifications

### 5.1 Gmail Integration

**Setup:**
1. Create Google Cloud Project
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Configure redirect URI

**Webhook Events:**
- New email received
- Email labeled as support

**Payload Format:**
```json
{
    "from": {"email": "customer@example.com", "name": "John"},
    "to": "support@techcorp.com",
    "subject": "Issue with login",
    "body": "Email content here",
    "received_at": "2024-03-26T12:00:00Z"
}
```

### 5.2 WhatsApp Integration (Twilio)

**Setup:**
1. Create Twilio account
2. Get Account SID and Auth Token
3. Configure WhatsApp sandbox
4. Set webhook URL

**Webhook Events:**
- Incoming message
- Message delivered
- Message read

**Payload Format:**
```json
{
    "from": "whatsapp:+1234567890",
    "to": "whatsapp:+14155238886",
    "text": "Hi, I need help",
    "timestamp": "2024-03-26T12:00:00Z"
}
```

### 5.3 Web Form Integration

**Frontend:** React/Next.js form
**Backend:** POST to /api/v1/webhook/webform

**Form Fields:**
- Name (required)
- Email (required)
- Subject (required)
- Message (required)
- Priority (optional)

---

## 6. Kafka Configuration

### 6.1 Topics

| Topic | Purpose | Partitions | Retention |
|-------|---------|------------|-----------|
| incoming_messages | Receive messages | 3 | 7 days |
| outgoing_messages | Send responses | 3 | 7 days |
| escalations | Escalated tickets | 1 | 30 days |
| analytics | Analytics events | 3 | 90 days |

### 6.2 Message Format

```json
{
    "message_id": "msg_123456",
    "type": "incoming",
    "channel": "email",
    "customer": "john@example.com",
    "subject": "Login issue",
    "content": "I cannot login...",
    "timestamp": "2024-03-26T12:00:00Z",
    "metadata": {
        "ip": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    }
}
```

---

## 7. AI Agent Specifications

### 7.1 Processing Pipeline

```
1. Receive Message
   ↓
2. Parse & Validate
   ↓
3. Analyze Sentiment
   ↓
4. Search Knowledge Base
   ↓
5. Get Customer History
   ↓
6. Decide Escalation
   ↓
7. Generate Response
   ↓
8. Format for Channel
   ↓
9. Send Response
   ↓
10. Save to Database
```

### 7.2 Escalation Rules

| Condition | Action | Level |
|-----------|--------|-------|
| Angry sentiment | Escalate | L2 |
| Billing/Refund | Escalate | L2 |
| Technical bug | Escalate | L2/L3 |
| Feature request | Escalate | L3 |
| Security issue | Escalate | L4 |
| Data loss | Escalate | L4 |

### 7.3 Response Templates

See `context/brand-voice.md` for detailed templates.

---

## 8. Deployment Specifications

### 8.1 Kubernetes Resources

| Resource | Count | CPU | Memory |
|----------|-------|-----|--------|
| API Pod | 2 | 500m | 512Mi |
| Worker Pod | 3 | 1000m | 1Gi |
| PostgreSQL | 1 | 1000m | 2Gi |
| Kafka | 3 | 500m | 1Gi |

### 8.2 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/crm_digital_fte

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_INCOMING=incoming_messages
KAFKA_TOPIC_OUTGOING=outgoing_messages

# OpenAI
OPENAI_API_KEY=sk-...

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...

# Gmail
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
```

---

## 9. Security Considerations

1. **Authentication:** JWT tokens for API access
2. **Authorization:** Role-based access control
3. **Encryption:** TLS for all communications
4. **Data Protection:** Encrypt PII at rest
5. **Rate Limiting:** Prevent abuse
6. **Input Validation:** Sanitize all inputs
7. **Logging:** Audit all actions

---

## 10. Monitoring & Observability

### 10.1 Metrics to Track
- Messages processed per minute
- Average response time
- Escalation rate
- Customer satisfaction score
- Error rate
- System uptime

### 10.2 Tools
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for logs
- Jaeger for tracing

---

## 11. Testing Strategy

### 11.1 Unit Tests
- MCP tools
- Sentiment analysis
- Response generation
- Database operations

### 11.2 Integration Tests
- API endpoints
- Webhook handlers
- Channel integrations

### 11.3 E2E Tests
- Complete message flow
- Escalation flow
- Multi-channel scenarios

---

**Version:** 1.0.0
**Last Updated:** March 26, 2024
**Status:** Ready for Implementation
