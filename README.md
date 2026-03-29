# 🏢 CRM Digital FTE - AI Customer Support Agent

## Hackathon 5: The CRM Digital FTE Factory

[![Status](https://img.shields.io/badge/status-complete-success)]()
[![Python](https://img.shields.io/badge/python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.104-green)]()
[![React](https://img.shields.io/badge/react-18-blue)]()
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)]()

---

## 📋 Overview

**CRM Digital FTE** is a complete AI-powered Customer Support Agent system that handles customer inquiries 24/7 across multiple channels (Email, WhatsApp, Web).

### ✨ Key Features

- 🤖 **AI Agent** - Powered by OpenAI GPT-4 with function calling
- 📧 **Multi-Channel** - Gmail, WhatsApp (Twilio), Web Form support
- 🧠 **Smart Responses** - Context-aware, sentiment-based responses
- ⚡ **Auto-Escalation** - Intelligent escalation to human agents
- 📊 **CRM Database** - Complete PostgreSQL-based CRM system
- 🔄 **Kafka Queue** - Scalable message processing pipeline
- ☸️ **Kubernetes** - Production-ready deployment configs

---

## 🏗️ Architecture

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
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    KAFKA MESSAGE QUEUE                       │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT (OpenAI)                         │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
crm-digital-fte/
├── context/                    # Knowledge base documents
│   ├── company-profile.md
│   ├── product-docs.md
│   ├── escalation-rules.md
│   ├── brand-voice.md
│   └── sample-tickets.json
│
├── prototype/                  # Phase 1 Prototype
│   ├── mcp_tools.py           # MCP tools implementation
│   ├── ai_agent.py            # Basic AI agent
│   ├── main.py                # FastAPI backend
│   └── requirements.txt
│
├── backend/                    # Phase 2 Production Backend
│   ├── production_agent.py    # OpenAI SDK agent
│   └── requirements.txt
│
├── frontend/                   # React Web Form
│   ├── src/
│   │   ├── components/
│   │   │   ├── SupportForm.tsx
│   │   │   ├── ChatWidget.tsx
│   │   │   └── Header.tsx
│   │   ├── utils/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   └── package.json
│
├── database/                   # Database Schema
│   ├── schema.sql             # PostgreSQL schema
│   └── models.py              # SQLAlchemy models
│
├── kafka/                      # Kafka Setup
│   ├── docker-compose.yml     # Kafka + Zookeeper
│   ├── producer.py            # Kafka producer
│   ├── consumer.py            # Kafka consumer
│   └── worker.py              # Message processor
│
├── integrations/               # Channel Integrations
│   ├── gmail.py               # Gmail API integration
│   └── whatsapp.py            # Twilio WhatsApp integration
│
├── kubernetes/                 # K8s Deployment
│   ├── deployment.yaml        # Main deployment config
│   └── zookeeper.yaml         # Zookeeper config
│
├── docker/                     # Docker Files
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docs/                       # Documentation
│   ├── discovery-log.md
│   └── specs.md
│
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Kafka (or use Docker Compose)
- OpenAI API Key

### 1. Clone & Setup

```bash
cd crm-digital-fte
```

### 2. Start Infrastructure (Docker)

```bash
# Start Kafka + Zookeeper
cd kafka
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Setup Database

```bash
# Create database
psql -U postgres -c "CREATE DATABASE crm_digital_fte;"

# Run schema
psql -U postgres -d crm_digital_fte -f database/schema.sql
```

### 4. Install Dependencies

```bash
# Backend
pip install -r prototype/requirements.txt

# Frontend
cd frontend
npm install
```

### 5. Configure Environment

```bash
# Copy .env.example
cp prototype/.env.example prototype/.env

# Edit with your credentials
# - OPENAI_API_KEY
# - DATABASE_URL
# - TWILIO credentials
# - Gmail credentials
```

### 6. Run the System

```bash
# Terminal 1: Start API Server
cd prototype
python main.py

# Terminal 2: Start Kafka Worker
cd kafka
python worker.py

# Terminal 3: Start Frontend
cd frontend
npm run dev
```

### 7. Access the Application

- **Web Form**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Kafka UI**: http://localhost:8080

---

## 📖 API Endpoints

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/message` | Process incoming message |
| GET | `/api/v1/message/{id}` | Get message status |

### Tickets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ticket` | List tickets |
| GET | `/api/v1/ticket/{id}` | Get ticket details |
| PUT | `/api/v1/ticket/{id}/status` | Update status |

### Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/customer/{id}/history` | Customer history |
| GET | `/api/v1/customer/{id}/sentiment` | Customer sentiment |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/webhook/{channel}` | Receive webhook |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/escalate` | Escalate ticket |
| POST | `/api/v1/sentiment` | Analyze sentiment |
| GET | `/api/v1/knowledge/search` | Search KB |
| GET | `/api/v1/stats` | System stats |
| GET | `/health` | Health check |

---

## 🧪 Testing

### Test with Sample Messages

```python
# Test via API
import requests

response = requests.post('http://localhost:8000/api/v1/message', json={
    "customer": "test@example.com",
    "channel": "email",
    "subject": "Cannot login",
    "message": "I forgot my password, please help!"
})

print(response.json())
```

### Test Scenarios

1. **Login Issue** (Email)
   - Customer: john@example.com
   - Message: "Cannot login to my account"
   - Expected: Password reset instructions

2. **Pricing Question** (WhatsApp)
   - Customer: +1234567890
   - Message: "What's the enterprise plan price?"
   - Expected: Pricing details

3. **Urgent Issue** (Web)
   - Customer: sarah@company.com
   - Message: "Data export not working, URGENT!"
   - Expected: Escalation to L2

---

## 📊 Database Schema

### Tables

- **customers** - Customer information
- **tickets** - Support tickets
- **messages** - Message history
- **conversations** - Conversation summaries
- **knowledge_base** - Knowledge articles
- **escalations** - Escalation records
- **channel_configs** - Channel settings
- **analytics** - Analytics events
- **agents** - Human support agents
- **sla_config** - SLA configurations

---

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/crm_digital_fte

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_INCOMING=incoming_messages
KAFKA_TOPIC_OUTGOING=outgoing_messages

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Gmail
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REDIRECT_URI=http://localhost:8000/auth/callback

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

---

## 🚢 Production Deployment

### Kubernetes

```bash
# Apply configurations
kubectl apply -f kubernetes/deployment.yaml

# Check status
kubectl get pods -n crm-digital-fte

# Scale workers
kubectl scale deployment worker --replicas=5 -n crm-digital-fte
```

### Docker Build

```bash
# Build API
docker build -f docker/Dockerfile.api -t crm-api:latest .

# Build Worker
docker build -f docker/Dockerfile.worker -t crm-worker:latest .

# Build Frontend
docker build -f docker/Dockerfile.frontend -t crm-frontend:latest .
```

---

## 📈 Monitoring

### Metrics to Track

- Messages processed per minute
- Average response time
- Escalation rate
- Customer satisfaction score
- Error rate
- System uptime

### Logs

```bash
# API logs
kubectl logs -f deployment/api -n crm-digital-fte

# Worker logs
kubectl logs -f deployment/worker -n crm-digital-fte
```

---

## 🔐 Security

- JWT authentication for API access
- TLS encryption for all communications
- PII encryption at rest
- Rate limiting
- Input validation
- Audit logging

---

## 📝 Documentation

- [Discovery Log](docs/discovery-log.md) - Development journey
- [Technical Specs](docs/specs.md) - Detailed specifications
- [API Docs](http://localhost:8000/docs) - Swagger/OpenAPI

---

## 🎯 Deliverables Checklist

- [x] Working AI Agent (Prototype + Production)
- [x] Web Support Form (React)
- [x] Database Schema (PostgreSQL)
- [x] Gmail Integration
- [x] WhatsApp Integration (Twilio)
- [x] API Backend (FastAPI)
- [x] Kafka Pipeline
- [x] Kubernetes Deployment
- [x] Documentation

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11, FastAPI |
| Frontend | React 18, TypeScript, Bootstrap |
| Database | PostgreSQL 15 |
| Queue | Kafka (Confluent) |
| AI | OpenAI GPT-4 |
| Email | Gmail API |
| WhatsApp | Twilio API |
| Deployment | Kubernetes, Docker |
| Monitoring | Prometheus, Grafana |

---

## 👥 Team

Built for **Hackathon 5: The CRM Digital FTE Factory**

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- OpenAI for GPT models
- FastAPI framework
- React community
- Twilio for WhatsApp API
- Confluent for Kafka

---

**Happy Coding! 🚀**




Step 1: Start Kafka (Docker)

     1 cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\kafka"
     2 docker-compose up -d

    Step 2: Create Database

     1 cd "C:\Program Files\PostgreSQL\15\bin"
     2 .\psql.exe -U postgres -c "CREATE DATABASE crm_digital_fte;"
     3 .\psql.exe -U postgres -d crm_digital_fte -f "C:\Users\Administrator\Desktop\Hackathon
       5\crm-digital-fte\database\schema.sql"

    Step 3: Install Python Dependencies

     1 cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte"
     2 python -m venv venv
     3 .\venv\Scripts\Activate.ps1
     4 pip install -r requirements.txt

    Step 4: Install Frontend Dependencies

     1 cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\frontend"
     2 npm install

    Step 5: Configure Environment

     1 cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\prototype"
     2 copy .env.example .env
     3 # Ab .env file edit karo with your API keys

    Step 6: Run Services (3 Terminals)

    Terminal 1 (API):

     1 cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\prototype"
     2 ..\venv\Scripts\Activate.ps1
     3 python main.py

    Terminal 2 (Worker):

     1 cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte"
     2 .\venv\Scripts\Activate.ps1
     3 python kafka\worker.py

    Terminal 3 (Frontend):

     1 cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\frontend"
     2 npm start

    ---

    📍 Access URLs:

    ┌──────────┬────────────────────────────┐
    │ Service  │ URL                        │
    ├──────────┼────────────────────────────┤
    │ Frontend │ http://localhost:3000      │
    │ API      │ http://localhost:8000      │
    │ API Docs │ http://localhost:8000/docs │
    │ Kafka UI │ http://localhost:8080  
    check      │ http://localhost:8080/
    └──────────┴────────────────────────────┘
"# TechCorp-Support-System" 
"# TechCorp-Support-System" 
