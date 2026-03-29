"""
FastAPI Backend for CRM Digital FTE
Pure Python - NO compilation required
Works on Python 3.13 Windows
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CRM Digital FTE API",
    description="AI Customer Support Agent",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
tickets = {}
customers = {}
conversations = {}

# Grok API Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY", "demo-key")

# ============== Helper Functions ==============

def analyze_sentiment(text):
    """Simple keyword-based sentiment analysis"""
    text_lower = text.lower()
    
    negative_words = ['angry', 'hate', 'terrible', 'awful', 'worst', 'broken', 'not working']
    positive_words = ['happy', 'great', 'awesome', 'love', 'excellent', 'good', 'thanks']
    urgent_words = ['urgent', 'emergency', 'asap', 'immediately', 'critical']
    
    sentiment = 'neutral'
    score = 0.5
    
    for word in negative_words:
        if word in text_lower:
            sentiment = 'negative'
            score = 0.2
            break
    
    for word in positive_words:
        if word in text_lower:
            sentiment = 'positive'
            score = 0.8
            break
    
    for word in urgent_words:
        if word in text_lower:
            sentiment = 'urgent'
            score = 0.1
            break
    
    return {'sentiment': sentiment, 'confidence': score}

def determine_priority(sentiment, message):
    """Determine ticket priority"""
    if sentiment['sentiment'] == 'urgent':
        return 'high'
    if sentiment['sentiment'] == 'negative':
        return 'high'
    if 'urgent' in message.lower() or 'emergency' in message.lower():
        return 'high'
    return 'medium'

def generate_ticket_id():
    """Generate unique ticket ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"TKT-{timestamp}"

def get_demo_response(subject, message):
    """Generate demo responses"""
    text = f"{subject} {message}".lower()
    
    if 'login' in text or 'password' in text:
        return """I understand you're having trouble logging in. Let me help you with that.

**Steps to resolve:**

1. **Reset Your Password**: Click on "Forgot Password" on the login page
2. **Check Your Email**: You'll receive a password reset link within 5 minutes
3. **Create New Password**: Follow the link and create a new secure password
4. **Try Logging In**: Use your new password to access your account

**Still having issues?**
- Clear your browser cache and cookies
- Try incognito/private browsing mode
- Try a different browser

Is there anything else I can assist you with?"""

    elif 'pricing' in text or 'price' in text or 'cost' in text:
        return """Thank you for your interest in TechCorp CRM!

**Our Current Plans:**

📌 **Starter Plan - $19/user/month**
- Contact Management, Basic Pipeline, Email Integration

📌 **Professional Plan - $49/user/month**
- All Starter features, Sales Pipeline, Basic Reporting

📌 **Enterprise Plan - $99/user/month**
- All Professional features, Marketing Automation, Advanced Analytics, Priority Support

**All plans include:**
- 24/7 AI Support, 99.9% Uptime SLA, Secure Cloud Hosting

Would you like to schedule a personalized demo?"""

    elif 'import' in text or 'csv' in text or 'export' in text:
        return """I understand you're having trouble with data import/export.

**Common CSV Import Issues & Solutions:**

1. **File Format**: Ensure CSV has headers, UTF-8 encoding
2. **File Size**: Maximum 10MB, split larger files
3. **Data Validation**: Valid email format, phone with country code
4. **Duplicates**: System skips duplicates by default

**Quick Steps:**
1. Download CSV template from Import page
2. Copy data into template
3. Review and validate all fields
4. Upload and map columns

Would you like me to send you our CSV template?"""

    elif 'urgent' in text or 'emergency' in text or 'critical' in text:
        return """I understand this is urgent and I'm here to help!

I'm escalating your issue to our specialist team immediately.

**What happens next:**
- A support specialist will review your case within 1 hour
- You'll receive priority assistance
- For critical issues, we'll contact you via phone

We appreciate your patience and will resolve this quickly!"""

    else:
        return f"""Thank you for contacting TechCorp Support!

I've received your message regarding "{subject}" and I'm here to help.

**Your Message:**
{message}

**To help you better, could you please share:**
- Any error messages you're seeing
- Steps you've already tried
- Your browser and operating system

In the meantime, visit our Knowledge Base: www.techcorp.com/help

Best regards,
TechCorp Support Team"""

# ============== API Endpoints ==============

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CRM Digital FTE API",
        "version": "1.0.0",
        "status": "running",
        "ai_provider": "Grok API (xAI)"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent": "active",
        "grok_api": "configured" if GROK_API_KEY != "demo-key" else "demo-mode"
    }

@app.post("/api/v1/message")
async def process_message(data: dict):
    """Process incoming customer message"""
    try:
        # Extract data
        customer = data.get('customer', 'unknown')
        channel = data.get('channel', 'web')
        subject = data.get('subject', 'No Subject')
        message = data.get('message', '')
        
        # Analyze sentiment
        sentiment = analyze_sentiment(message)
        
        # Determine priority
        priority = determine_priority(sentiment, message)
        
        # Create ticket
        ticket_id = generate_ticket_id()
        ticket = {
            'id': ticket_id,
            'customer': customer,
            'channel': channel,
            'subject': subject,
            'message': message,
            'priority': priority,
            'status': 'open',
            'sentiment': sentiment,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Store ticket
        tickets[ticket_id] = ticket
        
        # Store customer info
        if customer not in customers:
            customers[customer] = {'email': customer, 'tickets': []}
        customers[customer]['tickets'].append(ticket_id)
        
        # Generate response
        response_text = get_demo_response(subject, message)
        
        # Check if escalation needed
        should_escalate = sentiment['sentiment'] in ['urgent', 'negative']
        
        if should_escalate:
            ticket['status'] = 'escalated'
            ticket['escalation_reason'] = f"Auto-escalated due to {sentiment['sentiment']} sentiment"
        
        # Store conversation
        if customer not in conversations:
            conversations[customer] = []
        conversations[customer].append({
            'ticket_id': ticket_id,
            'message': message,
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'ticket_id': ticket_id,
            'status': ticket['status'],
            'response': response_text,
            'sentiment': sentiment,
            'escalated': should_escalate,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ticket/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get ticket details"""
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return tickets[ticket_id]

@app.get("/api/v1/tickets")
async def list_tickets(status: str = None, limit: int = 50):
    """List all tickets"""
    result = list(tickets.values())
    if status:
        result = [t for t in result if t['status'] == status]
    return result[-limit:]

@app.get("/api/v1/customer/{customer}/history")
async def get_customer_history(customer: str):
    """Get customer conversation history"""
    if customer not in conversations:
        return {'customer': customer, 'history': [], 'total': 0}
    return {
        'customer': customer,
        'history': conversations[customer],
        'total': len(conversations[customer])
    }

@app.get("/api/v1/sentiment")
async def analyze_sentiment_endpoint(text: str):
    """Analyze sentiment of text"""
    return analyze_sentiment(text)

@app.get("/api/v1/stats")
async def get_stats():
    """Get system statistics"""
    total = len(tickets)
    open_count = len([t for t in tickets.values() if t['status'] == 'open'])
    escalated = len([t for t in tickets.values() if t['status'] == 'escalated'])
    
    return {
        'total_tickets': total,
        'open_tickets': open_count,
        'escalated_tickets': escalated,
        'resolved_tickets': total - open_count - escalated,
        'total_customers': len(customers),
        'timestamp': datetime.now().isoformat()
    }

# ============== Main ==============

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting CRM Digital FTE API Server")
    print("=" * 60)
    print(f"   AI Provider: Grok API (xAI)")
    print(f"   API Key: {'Configured' if GROK_API_KEY != 'demo-key' else 'Demo Mode'}")
    print(f"   URL: http://localhost:8000")
    print(f"   Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
