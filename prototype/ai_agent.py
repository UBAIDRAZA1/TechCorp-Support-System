"""
AI Agent for CRM Digital FTE
Core agent that processes messages and generates responses
Now using Grok API (xAI) instead of OpenAI
"""

import json
import os
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any
from mcp_tools import MCPTools


class AIAgent:
    """
    AI Customer Support Agent
    Handles incoming messages, searches knowledge base, and generates responses
    Using Grok API (xAI) for AI responses
    """

    def __init__(self, model: str = "grok-beta"):
        self.model = model
        self.tools = MCPTools()
        self.memory = {}  # In-memory conversation storage
        self.system_prompt = self._build_system_prompt()

        # Grok API Configuration
        self.grok_api_key = os.getenv("GROK_API_KEY", "demo-key")
        self.grok_api_url = "https://api.x.ai/v1/chat/completions"

        # Load API key from .env if exists
        from dotenv import load_dotenv
        load_dotenv()
        self.grok_api_key = os.getenv("GROK_API_KEY", self.grok_api_key)

    def _call_grok_api(self, user_message: str, context: str = "") -> str:
        """Call Grok API to generate response"""

        # If using demo key, return template responses
        if self.grok_api_key == "demo-key":
            return self._get_demo_response(user_message)

        try:
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"{context}\n\nCustomer Message: {user_message}"}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }

            response = httpx.post(self.grok_api_url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"Grok API Error: {e}")
            return self._get_demo_response(user_message)

    def _get_demo_response(self, user_message: str) -> str:
        """Return demo responses when API key is not configured"""
        message_lower = user_message.lower()

        if 'login' in message_lower or 'password' in message_lower:
            return """I understand you're having trouble logging in. Let me help you with that.

Here are the steps to resolve this issue:

1. **Reset Your Password**: Click on "Forgot Password" on the login page
2. **Check Your Email**: You'll receive a password reset link within 5 minutes
3. **Create New Password**: Follow the link and create a new secure password
4. **Try Logging In**: Use your new password to access your account

If you're still unable to log in after resetting your password, please try:
- Clearing your browser cache and cookies
- Using an incognito/private browsing window
- Trying a different browser

Your account security is important to us. If you continue experiencing issues, please don't hesitate to reach out.

Is there anything else I can assist you with?"""

        elif 'pricing' in message_lower or 'price' in message_lower:
            return """Thank you for your interest in TechCorp CRM! I'd be happy to share our pricing information.

Here are our current plans:

**📌 Starter Plan - $19/user/month**
- Contact Management
- Basic Pipeline
- Email Integration
- Perfect for small businesses

**📌 Professional Plan - $49/user/month**
- All Starter features
- Sales Pipeline
- Basic Reporting
- Great for growing teams

**📌 Enterprise Plan - $99/user/month**
- All Professional features
- Marketing Automation
- Advanced Analytics
- Priority Support
- Custom Integrations
- Ideal for large organizations

All plans include:
- 24/7 AI Support
- 99.9% Uptime SLA
- Secure Cloud Hosting
- Regular Updates

Would you like to schedule a personalized demo? I'd be happy to connect you with our sales team.

Looking forward to helping you find the perfect plan for your business!"""

        elif 'import' in message_lower or 'csv' in message_lower:
            return """I understand you're having trouble with data import. Let me help you with that.

**Common CSV Import Issues & Solutions:**

1. **File Format**
   - Ensure your CSV has headers in the first row
   - Check that columns match our template (Name, Email, Phone, Company, etc.)
   - Save as UTF-8 encoding

2. **File Size**
   - Maximum file size is 10MB
   - For larger files, split into multiple CSVs

3. **Data Validation**
   - Email addresses must be valid format
   - Phone numbers should include country code
   - Remove any special characters from names

4. **Duplicate Records**
   - Check for duplicate emails in your file
   - Our system will skip duplicates by default

**Quick Steps:**
1. Download our CSV template from the Import page
2. Copy your data into the template
3. Review and validate all fields
4. Upload and map columns
5. Preview before confirming import

Would you like me to send you our CSV template? Or if you're seeing a specific error message, please share it and I can provide more targeted assistance.

Is there anything else I can help you with?"""

        elif 'urgent' in message_lower or 'emergency' in message_lower:
            return """I understand this is urgent and I'm here to help!

I'm escalating your issue to our specialist team immediately.

**What happens next:**
- A support specialist will review your case within 1 hour
- You'll receive priority assistance
- For critical issues, we'll contact you via phone if available

**Your Ticket Reference:** I've marked this as high priority

We appreciate your patience and will resolve this matter as quickly as possible.

Is there anything else I should know about this issue?"""

        else:
            return f"""Thank you for contacting TechCorp Support!

I've received your message and I'm here to help you with your inquiry.

Based on your message, let me offer some assistance:

**Next Steps:**
1. I've reviewed your inquiry
2. I'm gathering relevant information from our knowledge base
3. I'll provide you with actionable solutions

**To help you better, could you please share:**
- Any error messages you're seeing
- Steps you've already tried
- Your browser and operating system

In the meantime, you might find helpful resources in our Knowledge Base at www.techcorp.com/help.

I'm committed to resolving this for you. Please let me know if you have any questions.

Best regards,
TechCorp Support Team"""
        
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI agent"""
        return """You are an AI Customer Support Agent for TechCorp Solutions, a CRM software company.

YOUR ROLE:
- Provide 24/7 customer support
- Answer questions using the knowledge base
- Be professional, friendly, and helpful
- Escalate complex issues to human support when needed

BRAND VOICE:
- Professional yet friendly
- Clear and concise
- Empathetic to customer issues
- Solution-oriented

RESPONSE GUIDELINES:
1. Acknowledge the customer's issue
2. Search knowledge base for relevant information
3. Provide clear, actionable steps
4. Ask if they need further assistance
5. Escalate when:
   - Customer is angry or frustrated
   - Technical bug or data loss
   - Billing/refund issues
   - Feature requests
   - Multiple failed solutions

CHANNEL FORMATTING:
- Email: Formal, detailed
- WhatsApp: Casual, short, use emojis
- Web: Medium formality

Remember: Your goal is to resolve issues quickly and keep customers happy!"""

    def process_message(self, customer: str, channel: str, subject: str, 
                       message: str) -> Dict:
        """
        Process incoming customer message
        
        Args:
            customer: Customer email/phone
            channel: email, whatsapp, or web
            subject: Message subject
            message: Customer message
            
        Returns:
            Processing result with response
        """
        print(f"\n📨 INCOMING MESSAGE:")
        print(f"   Customer: {customer}")
        print(f"   Channel: {channel}")
        print(f"   Subject: {subject}")
        print(f"   Message: {message[:50]}...")
        
        # Step 1: Analyze sentiment
        sentiment = self.tools.analyze_sentiment(message)
        print(f"\n📊 SENTIMENT: {sentiment['sentiment']} (confidence: {sentiment['confidence']:.2f})")
        
        # Step 2: Create ticket
        priority = self._determine_priority(sentiment, message)
        ticket = self.tools.create_ticket(
            customer=customer,
            channel=channel,
            subject=subject,
            message=message,
            priority=priority
        )
        print(f"\n🎫 TICKET CREATED: {ticket['id']}")
        
        # Step 3: Get customer history
        history = self.tools.get_customer_history(customer)
        if history:
            print(f"\n📜 CUSTOMER HISTORY: {len(history)} previous tickets")
        
        # Step 4: Search knowledge base
        kb_results = self.tools.search_knowledge_base(f"{subject} {message}")
        print(f"\n🔍 KNOWLEDGE BASE: Found {len(kb_results)} relevant documents")
        
        # Step 5: Decide escalation
        escalation_decision = self.tools.decide_escalation(ticket, sentiment)
        print(f"\n⚖️  ESCALATION DECISION: {escalation_decision['should_escalate']}")
        print(f"   Reason: {escalation_decision['reason']}")
        print(f"   Level: {escalation_decision['level']}")
        
        # Step 6: Generate response
        if escalation_decision['should_escalate']:
            response = self._generate_escalation_response(
                ticket, escalation_decision, channel
            )
        else:
            response = self._generate_ai_response(
                ticket, kb_results, history, channel, sentiment
            )
        
        # Step 7: Send response
        send_result = self.tools.send_response(
            ticket_id=ticket['id'],
            channel=channel,
            customer=customer,
            message=response
        )
        
        # Step 8: Store in memory
        self._store_in_memory(customer, ticket, response, sentiment)
        
        # Step 9: Escalate if needed
        if escalation_decision['should_escalate']:
            self.tools.escalate_to_human(
                ticket_id=ticket['id'],
                reason=escalation_decision['reason'],
                priority=escalation_decision['level']
            )
        
        return {
            'ticket': ticket,
            'sentiment': sentiment,
            'escalation_decision': escalation_decision,
            'response': response,
            'send_result': send_result
        }
    
    def _determine_priority(self, sentiment: Dict, message: str) -> str:
        """Determine ticket priority based on sentiment and content"""
        message_lower = message.lower()
        
        # High priority indicators
        high_priority_keywords = ['down', 'critical', 'emergency', 'urgent', 
                                  'data loss', 'security', 'cancel', 'refund']
        
        if sentiment['sentiment'] == 'urgent':
            return 'high'
        
        if sentiment['sentiment'] == 'negative' and sentiment['confidence'] > 0.8:
            return 'high'
        
        for keyword in high_priority_keywords:
            if keyword in message_lower:
                return 'high'
        
        if sentiment['sentiment'] == 'neutral':
            return 'medium'
        
        return 'low'
    
    def _generate_ai_response(self, ticket: Dict, kb_results: List,
                             history: List, channel: str, sentiment: Dict) -> str:
        """Generate AI response using Grok API"""

        # Build context from knowledge base
        context = ""
        if kb_results:
            for result in kb_results[:2]:
                context += f"\n\nFrom {result['document']}:\n{result['snippet']}"

        # Build user message
        user_message = f"""
Customer: {ticket['customer']}
Channel: {channel}
Subject: {ticket['subject']}
Message: {ticket['message']}
Sentiment: {sentiment['sentiment']}
Priority: {ticket['priority']}
"""

        # Call Grok API to generate response
        response = self._call_grok_api(user_message, context)

        return response
    
    def _generate_email_response(self, ticket: Dict, kb_results: List, context: str) -> str:
        """Generate formal email response"""
        subject = ticket['subject'].lower()
        message = ticket['message'].lower()
        
        # Determine response based on content
        if 'login' in subject or 'password' in message:
            return """I understand you're having trouble logging in. Let me help you with that.

Here are the steps to resolve this issue:

1. **Reset Your Password**: Click on "Forgot Password" on the login page
2. **Check Your Email**: You'll receive a password reset link within 5 minutes
3. **Create New Password**: Follow the link and create a new secure password
4. **Try Logging In**: Use your new password to access your account

If you're still unable to log in after resetting your password, please try:
- Clearing your browser cache and cookies
- Using an incognito/private browsing window
- Trying a different browser

Your account security is important to us. If you continue experiencing issues, please don't hesitate to reach out.

Is there anything else I can assist you with?"""

        elif 'pricing' in subject or 'price' in message:
            return """Thank you for your interest in TechCorp CRM! I'd be happy to share our pricing information.

Here are our current plans:

**📌 Starter Plan - $19/user/month**
- Contact Management
- Basic Pipeline
- Email Integration
- Perfect for small businesses

**📌 Professional Plan - $49/user/month**
- All Starter features
- Sales Pipeline
- Basic Reporting
- Great for growing teams

**📌 Enterprise Plan - $99/user/month**
- All Professional features
- Marketing Automation
- Advanced Analytics
- Priority Support
- Custom Integrations
- Ideal for large organizations

All plans include:
- 24/7 AI Support
- 99.9% Uptime SLA
- Secure Cloud Hosting
- Regular Updates

Would you like to schedule a personalized demo? I'd be happy to connect you with our sales team.

Looking forward to helping you find the perfect plan for your business!"""

        elif 'import' in message or 'csv' in message:
            return """I understand you're having trouble with data import. Let me help you with that.

**Common CSV Import Issues & Solutions:**

1. **File Format**
   - Ensure your CSV has headers in the first row
   - Check that columns match our template (Name, Email, Phone, Company, etc.)
   - Save as UTF-8 encoding

2. **File Size**
   - Maximum file size is 10MB
   - For larger files, split into multiple CSVs

3. **Data Validation**
   - Email addresses must be valid format
   - Phone numbers should include country code
   - Remove any special characters from names

4. **Duplicate Records**
   - Check for duplicate emails in your file
   - Our system will skip duplicates by default

**Quick Steps:**
1. Download our CSV template from the Import page
2. Copy your data into the template
3. Review and validate all fields
4. Upload and map columns
5. Preview before confirming import

Would you like me to send you our CSV template? Or if you're seeing a specific error message, please share it and I can provide more targeted assistance.

Is there anything else I can help you with?"""

        else:
            return f"""Thank you for contacting TechCorp Support regarding "{ticket['subject']}".

I've reviewed your message and I'm here to help. Based on the information you've provided, let me offer some assistance.

{context if context else "Let me look into this matter for you."}

To better assist you, could you please provide:
1. Any error messages you're seeing (screenshots help!)
2. Steps you've already tried
3. Your browser and operating system

In the meantime, you might find helpful resources in our Knowledge Base at www.techcorp.com/help.

I'm committed to resolving this for you. Please let me know if you have any questions.

Best regards,
TechCorp Support Team"""

    def _generate_whatsapp_response(self, ticket: Dict, kb_results: List, context: str) -> str:
        """Generate casual WhatsApp response"""
        subject = ticket['subject'].lower()
        message = ticket['message'].lower()
        
        if 'login' in subject or 'password' in message:
            return "Hi! 👋 Having login trouble? No worries!\n\nTry this:\n1. Click 'Forgot Password' 🔐\n2. Check your email\n3. Reset & login!\n\nStill stuck? Reply here! 😊"
        
        elif 'pricing' in subject or 'price' in message:
            return "Hey! 💰 Here's our pricing:\n\n📌 Starter: $19/user/mo\n📌 Pro: $49/user/mo\n📌 Enterprise: $99/user/mo\n\nAll include 24/7 support! 🎉\n\nWant a demo? Just say the word! 👍"
        
        elif 'import' in message or 'csv' in message:
            return "Hi! 📊 CSV import issues? Let's fix it!\n\n✅ Check headers\n✅ Max 10MB file\n✅ UTF-8 format\n✅ No duplicates\n\nNeed our template? I can send it! 📩"
        
        else:
            return f"Hi there! 👋 Got your message about \"{ticket['subject']}\".\n\nLet me help you with this! {context[:100] if context else ''}\n\nNeed more info? Just ask! 😊"

    def _generate_web_response(self, ticket: Dict, kb_results: List, context: str) -> str:
        """Generate medium-formality web response"""
        subject = ticket['subject'].lower()
        message = ticket['message'].lower()
        
        if 'login' in subject or 'password' in message:
            return """Hello,

Thanks for reaching out about your login issue. I understand how frustrating this can be.

Here's how to resolve it:

**Step 1:** Reset Your Password
- Go to the login page
- Click "Forgot Password"
- Enter your email address

**Step 2:** Check Your Email
- Look for the reset link (check spam folder too)
- Link expires in 1 hour

**Step 3:** Create New Password
- Use 8+ characters
- Include numbers and symbols

**Still Having Issues?**
- Clear browser cache
- Try incognito mode
- Contact us with error details

We're here to help if you need anything else!

Regards,
TechCorp Team"""

        elif 'pricing' in subject or 'price' in message:
            return """Hello,

Thank you for your interest in TechCorp CRM!

**Our Pricing Plans:**

| Plan | Price | Best For |
|------|-------|----------|
| Starter | $19/user/month | Small businesses |
| Professional | $49/user/month | Growing teams |
| Enterprise | $99/user/month | Large organizations |

**All Plans Include:**
- 24/7 AI Support
- Secure Cloud Hosting
- Regular Updates
- 99.9% Uptime SLA

**Need Help Choosing?**
I'd be happy to connect you with our sales team for a personalized recommendation and demo.

Let me know how I can assist further!

Regards,
TechCorp Team"""

        else:
            return f"""Hello,

Thanks for reaching out! I see you're having trouble with "{ticket['subject']}".

{context if context else "Let me help you resolve this issue."}

To assist you better, could you share:
1. Any error messages you're seeing
2. What you've already tried
3. Your browser/OS details

In the meantime, check our Help Center: www.techcorp.com/help

Feel free to contact us if you have questions.

Regards,
TechCorp Team"""

    def _generate_escalation_response(self, ticket: Dict, escalation: Dict, 
                                      channel: str) -> str:
        """Generate escalation response"""
        
        if channel == 'email':
            return f"""Dear Valued Customer,

Thank you for contacting TechCorp Support.

I understand the importance of your concern regarding "{ticket['subject']}". I want to ensure you receive the best possible assistance.

I'm escalating your ticket (Reference: {ticket['id']}) to our specialized support team who will be able to provide you with more detailed assistance.

**What happens next:**
- A support specialist will review your case
- You'll receive a response within 4 hours (during business hours)
- For urgent matters, we'll contact you within 1 hour

**Your Ticket Details:**
- Ticket ID: {ticket['id']}
- Priority: {ticket['priority']}
- Status: Escalated to specialist team

We appreciate your patience and will resolve this matter as quickly as possible.

Best regards,
TechCorp Support Team"""

        elif channel == 'whatsapp':
            return f"Hi! 👋 I've escalated your issue to our specialist team.\n\n📋 Ticket: {ticket['id']}\n⏱️ Response within 4 hours\n\nWe'll contact you soon! Thanks for your patience! 🙏"

        else:
            return f"""Hello,

Thanks for reaching out! I understand your concern regarding "{ticket['subject']}".

I'm escalating your ticket to our specialist team for detailed assistance.

**Ticket Reference:** {ticket['id']}
**Expected Response:** Within 4 hours

We'll get back to you soon with a resolution.

Regards,
TechCorp Team"""

    def _store_in_memory(self, customer: str, ticket: Dict, response: str, 
                        sentiment: Dict):
        """Store conversation in memory"""
        if customer not in self.memory:
            self.memory[customer] = []
        
        self.memory[customer].append({
            'ticket': ticket,
            'response': response,
            'sentiment': sentiment,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 conversations per customer
        if len(self.memory[customer]) > 10:
            self.memory[customer] = self.memory[customer][-10:]
    
    def get_conversation_history(self, customer: str) -> List[Dict]:
        """Get conversation history for a customer"""
        return self.memory.get(customer, [])
    
    def clear_memory(self, customer: str = None):
        """Clear memory (all or for specific customer)"""
        if customer:
            self.memory.pop(customer, None)
        else:
            self.memory = {}


# ============== CLI Interface for Testing ==============
def main():
    """Test the AI Agent via CLI"""
    print("=" * 60)
    print("🤖 CRM Digital FTE - AI Agent Test Interface")
    print("=" * 60)
    
    agent = AIAgent()
    
    # Test scenarios
    test_cases = [
        {
            'customer': 'john@example.com',
            'channel': 'email',
            'subject': 'Cannot login to my account',
            'message': "I've been trying to login for the past hour but keep getting 'Invalid credentials' error. I'm sure my password is correct."
        },
        {
            'customer': '+1234567890',
            'channel': 'whatsapp',
            'subject': 'Pricing question',
            'message': "Hi, what's the price for enterprise plan?"
        },
        {
            'customer': 'sarah@company.com',
            'channel': 'web',
            'subject': 'Data export not working',
            'message': "I've tried exporting my data multiple times but the download never starts. This is urgent as I need it for a board meeting tomorrow."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"📝 TEST CASE {i}")
        print('=' * 60)
        
        result = agent.process_message(
            customer=test['customer'],
            channel=test['channel'],
            subject=test['subject'],
            message=test['message']
        )
        
        print(f"\n✅ TEST CASE {i} COMPLETED")
    
    print(f"\n{'='*60}")
    print("🎉 ALL TESTS COMPLETED!")
    print('=' * 60)


if __name__ == '__main__':
    main()
