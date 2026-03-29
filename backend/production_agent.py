"""
Production AI Agent with OpenAI SDK
Enhanced agent with function calling, vector search, and production features
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionAIAgent:
    """
    Production AI Agent using OpenAI SDK
    Features:
    - Function calling for tool use
    - Vector search for knowledge base
    - Conversation memory
    - Sentiment analysis
    - Multi-channel support
    """
    
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Define tools/functions
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search the knowledge base for relevant information about products, features, or troubleshooting",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["faq", "troubleshooting", "guide", "pricing", "all"],
                                "description": "Category to search in"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_ticket",
                    "description": "Create a new support ticket",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer": {"type": "string", "description": "Customer email or phone"},
                            "channel": {"type": "string", "enum": ["email", "whatsapp", "web"], "description": "Communication channel"},
                            "subject": {"type": "string", "description": "Ticket subject"},
                            "message": {"type": "string", "description": "Customer message"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Ticket priority"}
                        },
                        "required": ["customer", "channel", "subject", "message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_customer_history",
                    "description": "Get customer's past conversations and tickets",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer": {"type": "string", "description": "Customer email or phone"},
                            "limit": {"type": "integer", "description": "Number of records to return", "default": 10}
                        },
                        "required": ["customer"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_to_human",
                    "description": "Escalate the conversation to a human support agent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string", "description": "Ticket ID to escalate"},
                            "reason": {"type": "string", "description": "Reason for escalation"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Escalation priority"}
                        },
                        "required": ["ticket_id", "reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_response",
                    "description": "Send a response to the customer via their channel",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string", "description": "Ticket ID"},
                            "channel": {"type": "string", "enum": ["email", "whatsapp", "web"], "description": "Communication channel"},
                            "customer": {"type": "string", "description": "Customer email or phone"},
                            "message": {"type": "string", "description": "Response message"},
                            "format_type": {"type": "string", "enum": ["formal", "casual", "medium"], "description": "Response format style"}
                        },
                        "required": ["ticket_id", "channel", "customer", "message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_sentiment",
                    "description": "Analyze the sentiment of customer message",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to analyze"}
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
        
        # System prompt
        self.system_prompt = """You are an AI Customer Support Agent for TechCorp Solutions, a leading CRM software company.

YOUR ROLE:
- Provide 24/7 customer support with professionalism and empathy
- Answer questions accurately using the knowledge base
- Resolve issues efficiently or escalate when needed
- Maintain a friendly, helpful tone throughout

BRAND VOICE:
- Professional yet approachable
- Clear and concise (avoid jargon)
- Empathetic to customer frustrations
- Solution-oriented and proactive

RESPONSE GUIDELINES:
1. Acknowledge the customer's issue with empathy
2. Use tools to search knowledge base and get customer history
3. Provide clear, actionable solutions
4. Confirm the issue is resolved before closing
5. Escalate to human support when:
   - Customer is angry, frustrated, or threatening to cancel
   - Billing or refund issues
   - Technical bugs or data loss
   - Complex integration issues
   - Feature requests
   - Multiple failed solutions

CHANNEL FORMATTING:
- Email: Formal, detailed responses with proper greeting and signature
- WhatsApp: Casual, short responses with emojis
- Web: Medium formality, clear and structured

Remember: Your goal is to resolve issues quickly while maintaining customer satisfaction!"""

    def process_message(
        self,
        customer: str,
        channel: str,
        subject: str,
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Process customer message using OpenAI with function calling
        
        Args:
            customer: Customer email/phone
            channel: Communication channel
            subject: Message subject
            message: Customer message
            conversation_history: Optional conversation history
            
        Returns:
            Processing result with response and metadata
        """
        logger.info(f"📨 Processing message from {customer} via {channel}")
        
        # Build messages array
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Channel: {channel}\nSubject: {subject}\nMessage: {message}"}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages[1:1] = conversation_history[-10:]  # Last 10 messages
        
        try:
            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message
            
            # Check if function calls are needed
            if assistant_message.tool_calls:
                return self._handle_tool_calls(
                    assistant_message.tool_calls,
                    messages,
                    customer,
                    channel
                )
            
            # Direct response
            return {
                "response": assistant_message.content,
                "requires_action": False,
                "sentiment": self._analyze_sentiment_local(message),
                "escalation_needed": self._check_escalation(message),
                "ticket_id": None
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": self._get_fallback_response(channel),
                "requires_action": False,
                "error": str(e),
                "escalation_needed": True,
                "escalation_reason": "AI processing error"
            }
    
    def _handle_tool_calls(
        self,
        tool_calls: List,
        messages: List[Dict],
        customer: str,
        channel: str
    ) -> Dict[str, Any]:
        """Handle OpenAI tool calls"""
        results = {}
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"🔧 Calling function: {function_name}")
            
            # Execute the function
            result = self._execute_function(
                function_name,
                function_args,
                customer,
                channel
            )
            
            results[function_name] = result
        
        # Generate final response based on tool results
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": tool_calls
        })
        
        # Add tool results to messages
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(results.get(function_name, {}))
            })
        
        # Get final response from AI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return {
            "response": response.choices[0].message.content,
            "requires_action": True,
            "tool_results": results,
            "sentiment": self._analyze_sentiment_local(messages[1]["content"]),
            "escalation_needed": "escalate_to_human" in results,
            "ticket_id": results.get("create_ticket", {}).get("id")
        }
    
    def _execute_function(
        self,
        function_name: str,
        arguments: Dict,
        customer: str,
        channel: str
    ) -> Any:
        """Execute a tool function"""
        
        if function_name == "search_knowledge_base":
            return self._search_knowledge_base(
                arguments.get("query", ""),
                arguments.get("category", "all")
            )
        
        elif function_name == "create_ticket":
            return self._create_ticket(
                arguments.get("customer", customer),
                arguments.get("channel", channel),
                arguments.get("subject", ""),
                arguments.get("message", ""),
                arguments.get("priority", "medium")
            )
        
        elif function_name == "get_customer_history":
            return self._get_customer_history(
                arguments.get("customer", customer),
                arguments.get("limit", 10)
            )
        
        elif function_name == "escalate_to_human":
            return self._escalate_to_human(
                arguments.get("ticket_id", ""),
                arguments.get("reason", ""),
                arguments.get("priority", "medium")
            )
        
        elif function_name == "send_response":
            return self._send_response(
                arguments.get("ticket_id", ""),
                arguments.get("channel", channel),
                arguments.get("customer", customer),
                arguments.get("message", ""),
                arguments.get("format_type", "medium")
            )
        
        elif function_name == "analyze_sentiment":
            return self._analyze_sentiment(arguments.get("text", ""))
        
        return {"error": f"Unknown function: {function_name}"}
    
    # ========== Tool Implementations ==========
    
    def _search_knowledge_base(self, query: str, category: str) -> Dict:
        """Search knowledge base (placeholder - integrate with vector DB)"""
        # TODO: Integrate with pgvector or similar
        return {
            "results": [
                {"title": "Knowledge Base Search", "content": f"Results for: {query}"}
            ],
            "count": 1
        }
    
    def _create_ticket(self, customer: str, channel: str, subject: str, 
                      message: str, priority: str) -> Dict:
        """Create support ticket (placeholder - integrate with DB)"""
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "id": ticket_id,
            "customer": customer,
            "channel": channel,
            "subject": subject,
            "status": "open",
            "priority": priority,
            "created_at": datetime.now().isoformat()
        }
    
    def _get_customer_history(self, customer: str, limit: int) -> Dict:
        """Get customer history (placeholder - integrate with DB)"""
        return {
            "customer": customer,
            "tickets": [],
            "total": 0
        }
    
    def _escalate_to_human(self, ticket_id: str, reason: str, priority: str) -> Dict:
        """Escalate to human (placeholder - integrate with DB)"""
        return {
            "ticket_id": ticket_id,
            "escalated": True,
            "reason": reason,
            "priority": priority,
            "assigned_to": "human_support"
        }
    
    def _send_response(self, ticket_id: str, channel: str, customer: str, 
                      message: str, format_type: str) -> Dict:
        """Send response (placeholder - integrate with channel APIs)"""
        return {
            "ticket_id": ticket_id,
            "sent": True,
            "channel": channel,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Analyze sentiment. Return JSON: {sentiment: 'positive|neutral|negative|urgent', confidence: 0-1}"},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except:
            return self._analyze_sentiment_local(text)
    
    def _analyze_sentiment_local(self, text: str) -> Dict:
        """Local sentiment analysis (fallback)"""
        text_lower = text.lower()
        
        negative_words = ['angry', 'hate', 'terrible', 'awful', 'worst', 'cancel', 'refund']
        urgent_words = ['urgent', 'emergency', 'asap', 'critical', 'down', 'broken']
        
        negative_score = sum(1 for word in negative_words if word in text_lower)
        urgent_score = sum(1 for word in urgent_words if word in text_lower)
        
        if urgent_score > 0:
            return {"sentiment": "urgent", "confidence": 0.9}
        elif negative_score > 0:
            return {"sentiment": "negative", "confidence": 0.7}
        else:
            return {"sentiment": "neutral", "confidence": 0.7}
    
    def _check_escalation(self, message: str) -> bool:
        """Check if escalation is needed"""
        escalation_keywords = ['cancel', 'refund', 'lawyer', 'lawsuit', 'manager', 
                              'complaint', 'sue', 'legal']
        return any(keyword in message.lower() for keyword in escalation_keywords)
    
    def _get_fallback_response(self, channel: str) -> str:
        """Fallback response when AI fails"""
        if channel == "whatsapp":
            return "Hi! 👋 I'm having trouble processing your message. Let me connect you with a human agent who can help!"
        elif channel == "email":
            return """Dear Valued Customer,

I apologize, but I'm experiencing technical difficulties processing your request. 

A human support agent has been notified and will respond to your inquiry shortly.

Thank you for your patience.

Best regards,
TechCorp Support Team"""
        else:
            return """Hello,

I'm having trouble processing your message. Let me connect you with a human agent who can better assist you.

Thank you for your patience.

Regards,
TechCorp Team"""


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Production AI Agent - CRM Digital FTE")
    print("=" * 60)
    
    agent = ProductionAIAgent()
    
    # Test message
    result = agent.process_message(
        customer="test@example.com",
        channel="email",
        subject="Cannot login to my account",
        message="I've been trying to login for the past hour but keep getting 'Invalid credentials' error. This is very frustrating!"
    )
    
    print(f"\n📤 Response: {result['response'][:200]}...")
    print(f"📊 Sentiment: {result.get('sentiment', {})}")
    print(f"⚠️  Escalation needed: {result.get('escalation_needed', False)}")
