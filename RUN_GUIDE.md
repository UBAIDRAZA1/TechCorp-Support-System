# 🚀 CRM Digital FTE - Complete Setup Guide (Windows)

## Step-by-Step Instructions to Run the Project

---

## 📋 Prerequisites Check

Install these if not already installed:

1. **Python 3.11+**: https://www.python.org/downloads/
2. **Node.js 18+**: https://nodejs.org/
3. **Docker Desktop**: https://www.docker.com/products/docker-desktop/
4. **PostgreSQL 15+**: https://www.postgresql.org/download/windows/
5. **Git**: https://git-scm.com/download/win

---

## 🔧 Step 1: Open PowerShell as Administrator

```powershell
# Navigate to project directory
cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte"
```

---

## 🐳 Step 2: Start Kafka & Zookeeper (Docker)

```powershell
# Navigate to kafka folder
cd kafka

# Start Docker containers
docker-compose up -d

# Check if containers are running
docker-compose ps

# Expected output: Both zookeeper and kafka should show "Up" status
```

**Wait 30 seconds** for Kafka to fully start.

**Verify Kafka is running:**
```powershell
docker-compose logs kafka
```

---

## 🗄️ Step 3: Setup PostgreSQL Database

### Option A: Using pgAdmin (GUI)

1. Open **pgAdmin 4**
2. Connect to PostgreSQL (usually localhost:5432)
3. Right-click on **Databases** → **Create** → **Database**
4. Database name: `crm_digital_fte`
5. Click **Save**
6. Open **Query Tool** for the new database
7. Open file: `C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\database\schema.sql`
8. Copy entire content and paste in Query Tool
9. Click **Execute** (▶️ button)

### Option B: Using Command Line

```powershell
# Navigate to PostgreSQL bin folder (adjust path if different)
cd "C:\Program Files\PostgreSQL\15\bin"

# Create database (replace 'postgres' with your username if different)
.\psql.exe -U postgres -c "CREATE DATABASE crm_digital_fte;"

# Run schema
.\psql.exe -U postgres -d crm_digital_fte -f "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\database\schema.sql"
```

**If you get password prompt:**
- Default password is usually: `postgres`
- Or the password you set during PostgreSQL installation

---

## 📦 Step 4: Install Python Dependencies

```powershell
# Navigate back to project root
cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**This will take 2-5 minutes.** Wait for completion.

---

## 🌐 Step 5: Install Frontend Dependencies

```powershell
# Navigate to frontend folder
cd frontend

# Install Node.js dependencies
npm install

# This will take 1-3 minutes
```

---

## ⚙️ Step 6: Configure Environment Variables

```powershell
# Navigate to prototype folder
cd ..\prototype

# Copy .env.example to .env
copy .env.example .env
```

**Now edit the .env file:**

1. Open `C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\prototype\.env` in Notepad
2. Update these values:

```env
# OpenAI API Key (Get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-actual-api-key-here

# Database (Update if you changed password)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crm_digital_fte

# Kafka (Keep as is)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_INCOMING=incoming_messages
KAFKA_TOPIC_OUTGOING=outgoing_messages

# Twilio (Optional - for WhatsApp, get from https://twilio.com)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Gmail (Optional - for Email integration)
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=http://localhost:8000/auth/callback

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Logging
LOG_LEVEL=INFO
```

**Minimum required for testing:**
- `OPENAI_API_KEY` (for AI features)
- `DATABASE_URL` (for database connection)

**For demo/testing without API keys, you can use:**
```env
OPENAI_API_KEY=demo-key
```

---

## 🚀 Step 7: Run the Services

### **Terminal 1: Start API Server**

```powershell
# Open new PowerShell window

# Navigate to prototype folder
cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\prototype"

# Activate virtual environment
..\venv\Scripts\Activate.ps1

# Start API server
python main.py
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ API is running at: http://localhost:8000**

---

### **Terminal 2: Start Kafka Worker**

```powershell
# Open new PowerShell window

# Navigate to project root
cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Kafka worker
python kafka\worker.py
```

**Expected output:**
```
INFO:     ✅ Connected to Kafka at localhost:9092
INFO:     🚀 Starting Kafka Worker...
INFO:     📬 Subscribed to topics: ['incoming_messages']
```

**✅ Worker is processing messages**

---

### **Terminal 3: Start Frontend (React)**

```powershell
# Open new PowerShell window

# Navigate to frontend folder
cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\frontend"

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**✅ Frontend is running at: http://localhost:3000**

---

## ✅ Step 8: Verify Everything is Working

### 1. Check API Health

Open browser: **http://localhost:8000/health**

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-03-26T12:00:00",
  "agent": "active",
  "tools": "active"
}
```

### 2. Check API Documentation

Open browser: **http://localhost:8000/docs**

You should see Swagger UI with all API endpoints.

### 3. Check Frontend

Open browser: **http://localhost:3000**

You should see the TechCorp Support form.

### 4. Check Kafka UI

Open browser: **http://localhost:8080**

You should see Kafka UI with topics.

---

## 🧪 Step 9: Test the System

### Test via API (PowerShell)

```powershell
# Test message endpoint
$body = @{
    customer = "test@example.com"
    channel = "email"
    subject = "Cannot login"
    message = "I forgot my password, please help!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/message" -Method Post -Body $body -ContentType "application/json"

$response | ConvertTo-Json
```

### Test via Web Form

1. Open **http://localhost:3000**
2. Fill the form:
   - **Name**: John Doe
   - **Email**: john@example.com
   - **Subject**: Cannot login to my account
   - **Message**: I've been trying to login but keep getting error
   - **Priority**: Medium
3. Click **Submit Ticket**
4. You should see a success message with ticket ID

### Test via Swagger UI

1. Open **http://localhost:8000/docs**
2. Click on **POST /api/v1/message**
3. Click **Try it out**
4. Fill the request body:
```json
{
  "customer": "test@example.com",
  "channel": "email",
  "subject": "Test Issue",
  "message": "Testing the system"
}
```
5. Click **Execute**

---

## 🛠️ Troubleshooting

### Issue: Docker containers not starting

```powershell
# Check Docker is running
docker ps

# Restart Docker Desktop
# Right-click Docker icon in system tray → Quit Docker Desktop
# Then open Docker Desktop again

# Recreate containers
cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\kafka"
docker-compose down
docker-compose up -d
```

### Issue: PostgreSQL connection error

```powershell
# Check PostgreSQL is running
# Open Services (services.msc)
# Find "postgresql-x64-15" and ensure it's "Running"

# Test connection
cd "C:\Program Files\PostgreSQL\15\bin"
.\psql.exe -U postgres -c "\l"
```

### Issue: Port already in use

```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in prototype/.env
PORT=8001
```

### Issue: Python module not found

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: npm install fails

```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules
cd frontend
Remove-Item -Recurse -Force node_modules

# Reinstall
npm install
```

---

## 📊 System Architecture (Running)

```
┌─────────────────────────────────────────────────────┐
│                  YOUR BROWSER                        │
│         http://localhost:3000 (Frontend)            │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│           Terminal 3: Frontend (Port 3000)           │
│              npm run dev                             │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│           Terminal 1: API (Port 8000)                │
│           python prototype/main.py                   │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  PostgreSQL  │        │    Kafka     │
│  (Port 5432) │        │  (Port 9092) │
└──────────────┘        └──────┬───────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Terminal 2:     │
                    │  Kafka Worker    │
                    └──────────────────┘
```

---

## 🎯 Quick Reference

| Service | URL | Status Check |
|---------|-----|--------------|
| Frontend | http://localhost:3000 | Open in browser |
| API | http://localhost:8000 | http://localhost:8000/health |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Kafka UI | http://localhost:8080 | Open in browser |
| PostgreSQL | localhost:5432 | pgAdmin |

---

## 📝 Commands Summary

```powershell
# Full setup from scratch (run in order):

# 1. Start Kafka
cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\kafka"
docker-compose up -d

# 2. Create Database
cd "C:\Program Files\PostgreSQL\15\bin"
.\psql.exe -U postgres -c "CREATE DATABASE crm_digital_fte;"
.\psql.exe -U postgres -d crm_digital_fte -f "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte\database\schema.sql"

# 3. Install Python dependencies
cd "C:\Users\Administrator\Desktop\Hackathon 5\crm-digital-fte"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 4. Install Frontend dependencies
cd frontend
npm install

# 5. Configure environment
cd ..\prototype
copy .env.example .env
# Edit .env with your settings

# 6. Run services (in 3 separate terminals)
# Terminal 1: API
cd ..\prototype
.\venv\Scripts\Activate.ps1
python main.py

# Terminal 2: Worker
cd ..
.\venv\Scripts\Activate.ps1
python kafka\worker.py

# Terminal 3: Frontend
cd frontend
npm run dev
```

---

## ✅ Success Checklist

- [ ] Docker containers running (kafka, zookeeper)
- [ ] PostgreSQL database created with schema
- [ ] Python dependencies installed
- [ ] Frontend dependencies installed
- [ ] .env file configured
- [ ] API running on port 8000
- [ ] Worker running and connected to Kafka
- [ ] Frontend running on port 3000
- [ ] Health check returns healthy
- [ ] Can submit ticket via web form

---

**🎉 Congratulations! Your CRM Digital FTE is now running!**

For any issues, check the logs in each terminal window.
