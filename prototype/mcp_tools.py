"""
MCP Tools for CRM Digital FTE
These tools provide the core functionality for the AI Agent
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class MCPTools:
    """Model Context Protocol Tools for CRM Agent"""
    
    def __init__(self, context_dir: str = None):
        self.context_dir = context_dir or os.path.join(os.path.dirname(__file__), '..', 'context')
        self.knowledge_base = self._load_knowledge_base()
        self.tickets = self._load_tickets()
        
    def _load_knowledge_base(self) -> Dict:
        """Load all knowledge base documents"""
        kb = {}
        try:
            # Load company profile
            with open(os.path.join(self.context_dir, 'company-profile.md'), 'r', encoding='utf-8') as f:
                kb['company_profile'] = f.read()
            
            # Load product docs
            with open(os.path.join(self.context_dir, 'product-docs.md'), 'r', encoding='utf-8') as f:
                kb['product_docs'] = f.read()
            
            # Load escalation rules
            with open(os.path.join(self.context_dir, 'escalation-rules.md'), 'r', encoding='utf-8') as f:
                kb['escalation_rules'] = f.read()
            
            # Load brand voice
            with open(os.path.join(self.context_dir, 'brand-voice.md'), 'r', encoding='utf-8') as f:
                kb['brand_voice'] = f.read()
                
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            kb = {}
            
        return kb
    
    def _load_tickets(self) -> List[Dict]:
        """Load sample tickets"""
        try:
            with open(os.path.join(self.context_dir, 'sample-tickets.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sample_tickets', [])
        except Exception as e:
            print(f"Error loading tickets: {e}")
            return []
    
    # ========== TOOL 1: search_knowledge_base ==========
    def search_knowledge_base(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search the knowledge base for relevant information
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with scores
        """
        results = []
        query_lower = query.lower()
        
        # Simple keyword search (can be enhanced with embeddings)
        for doc_name, doc_content in self.knowledge_base.items():
            # Calculate relevance score
            score = 0
            query_words = query_lower.split()
            
            for word in query_words:
                if word in doc_content.lower():
                    score += doc_content.lower().count(word)
            
            if score > 0:
                # Extract relevant snippet
                snippet = self._extract_snippet(doc_content, query_words)
                results.append({
                    'document': doc_name,
                    'score': score,
                    'snippet': snippet,
                    'content': doc_content
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def _extract_snippet(self, content: str, keywords: List[str], window: int = 100) -> str:
        """Extract a snippet containing keywords"""
        content_lower = content.lower()
        
        for keyword in keywords:
            idx = content_lower.find(keyword)
            if idx != -1:
                start = max(0, idx - window)
                end = min(len(content), idx + window)
                return "..." + content[start:end] + "..."
        
        return content[:200] + "..."
    
    # ========== TOOL 2: create_ticket ==========
    def create_ticket(self, customer: str, channel: str, subject: str, 
                     message: str, priority: str = "medium") -> Dict:
        """
        Create a new support ticket
        
        Args:
            customer: Customer email/phone
            channel: email, whatsapp, or web
            subject: Ticket subject
            message: Customer message
            priority: low, medium, high
            
        Returns:
            Created ticket object
        """
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ticket = {
            'id': ticket_id,
            'customer': customer,
            'channel': channel,
            'subject': subject,
            'message': message,
            'priority': priority,
            'status': 'open',
            'escalation_level': 'L1',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Save to tickets list (in production, save to database)
        self.tickets.append(ticket)
        
        return ticket
    
    # ========== TOOL 3: get_customer_history ==========
    def get_customer_history(self, customer: str, limit: int = 10) -> List[Dict]:
        """
        Get customer's conversation history
        
        Args:
            customer: Customer email/phone
            limit: Number of records to return
            
        Returns:
            List of past tickets/conversations
        """
        history = []
        
        for ticket in self.tickets:
            if ticket['customer'] == customer:
                history.append(ticket)
        
        # Sort by created_at descending
        history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return history[:limit]
    
    # ========== TOOL 4: send_response ==========
    def send_response(self, ticket_id: str, channel: str, customer: str, 
                     message: str, format_type: str = "auto") -> Dict:
        """
        Send response to customer via appropriate channel
        
        Args:
            ticket_id: Ticket reference ID
            channel: email, whatsapp, or web
            customer: Customer email/phone
            message: Response message
            format_type: auto, formal, casual, medium
            
        Returns:
            Response status
        """
        # Format message based on channel
        if format_type == "auto":
            if channel == "email":
                formatted = self._format_email(message)
            elif channel == "whatsapp":
                formatted = self._format_whatsapp(message)
            else:  # web
                formatted = self._format_web(message)
        else:
            formatted = message
        
        # In production, this would send via actual channel APIs
        response = {
            'ticket_id': ticket_id,
            'channel': channel,
            'customer': customer,
            'message': formatted,
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        print(f"\n📤 RESPONSE SENT via {channel}:")
        print(f"   To: {customer}")
        print(f"   Message: {formatted[:100]}...")
        
        return response
    
    def _format_email(self, message: str) -> str:
        """Format for email (formal)"""
        return f"""Dear Valued Customer,

Thank you for contacting TechCorp Support.

{message}

Please let me know if you need any further assistance.

Best regards,
TechCorp Support Team
"""
    
    def _format_whatsapp(self, message: str) -> str:
        """Format for WhatsApp (casual & short)"""
        return f"Hi! 👋 {message}\n\nNeed more help? Just reply! 😊"
    
    def _format_web(self, message: str) -> str:
        """Format for web (medium formality)"""
        return f"""Hello,

Thanks for reaching out!

{message}

Feel free to contact us if you have questions.

Regards,
TechCorp Team
"""
    
    # ========== TOOL 5: escalate_to_human ==========
    def escalate_to_human(self, ticket_id: str, reason: str, 
                         priority: str = "medium") -> Dict:
        """
        Escalate ticket to human support
        
        Args:
            ticket_id: Ticket reference ID
            reason: Reason for escalation
            priority: low, medium, high, urgent
            
        Returns:
            Escalation status
        """
        escalation = {
            'ticket_id': ticket_id,
            'escalated_at': datetime.now().isoformat(),
            'reason': reason,
            'priority': priority,
            'assigned_to': 'human_support',
            'status': 'escalated'
        }
        
        # Update ticket
        for ticket in self.tickets:
            if ticket['id'] == ticket_id:
                ticket['status'] = 'escalated'
                ticket['escalation_level'] = 'L2'
                ticket['escalation_reason'] = reason
                break
        
        print(f"\n⚠️  ESCALATED: Ticket {ticket_id} to human support")
        print(f"   Reason: {reason}")
        print(f"   Priority: {priority}")
        
        return escalation
    
    # ========== TOOL 6: analyze_sentiment ==========
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of customer message
        
        Args:
            text: Customer message
            
        Returns:
            Sentiment analysis result
        """
        text_lower = text.lower()
        
        # Simple keyword-based sentiment analysis
        positive_words = ['happy', 'great', 'good', 'thanks', 'love', 'excellent', 
                         'awesome', 'wonderful', 'pleased', 'satisfied']
        negative_words = ['angry', 'frustrated', 'hate', 'terrible', 'awful', 
                         'worst', 'disappointed', 'upset', 'furious', 'cancel']
        urgent_words = ['urgent', 'emergency', 'asap', 'immediately', 'critical', 
                       'down', 'broken', 'not working']
        
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        urgent_score = sum(1 for word in urgent_words if word in text_lower)
        
        # Determine sentiment
        if urgent_score > 0 or 'cancel' in text_lower or 'refund' in text_lower:
            sentiment = 'urgent'
            confidence = 0.9
        elif negative_score > positive_score:
            sentiment = 'negative'
            confidence = min(0.5 + (negative_score * 0.1), 0.95)
        elif positive_score > negative_score:
            sentiment = 'positive'
            confidence = min(0.5 + (positive_score * 0.1), 0.95)
        else:
            sentiment = 'neutral'
            confidence = 0.7
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'urgent_score': urgent_score
        }
    
    # ========== TOOL 7: decide_escalation ==========
    def decide_escalation(self, ticket: Dict, sentiment: Dict) -> Dict:
        """
        Decide if ticket should be escalated
        
        Args:
            ticket: Ticket object
            sentiment: Sentiment analysis result
            
        Returns:
            Escalation decision
        """
        should_escalate = False
        reason = []
        level = 'L1'
        
        # Check sentiment
        if sentiment['sentiment'] in ['negative', 'urgent']:
            should_escalate = True
            reason.append(f"Customer sentiment: {sentiment['sentiment']}")
            level = 'L2'
        
        # Check priority
        if ticket.get('priority') == 'high':
            should_escalate = True
            reason.append("High priority ticket")
            level = 'L2'
        
        # Check for escalation keywords
        escalation_keywords = ['cancel', 'refund', 'lawyer', 'lawsuit', 'manager', 
                              'supervisor', 'complaint']
        message_lower = ticket.get('message', '').lower()
        
        for keyword in escalation_keywords:
            if keyword in message_lower:
                should_escalate = True
                reason.append(f"Escalation keyword detected: {keyword}")
                level = 'L2'
                break
        
        # Check for technical issues
        technical_keywords = ['bug', 'error', 'not working', 'broken', 'data loss']
        for keyword in technical_keywords:
            if keyword in message_lower:
                reason.append(f"Technical issue detected: {keyword}")
                if level == 'L1':
                    level = 'L2'
                break
        
        return {
            'should_escalate': should_escalate,
            'reason': '; '.join(reason) if reason else 'No escalation needed',
            'level': level,
            'confidence': sentiment['confidence']
        }
    
    # Get all available tools info
    def get_tools_info(self) -> List[Dict]:
        """Return information about all available tools"""
        return [
            {
                'name': 'search_knowledge_base',
                'description': 'Search knowledge base for relevant information',
                'parameters': ['query', 'top_k']
            },
            {
                'name': 'create_ticket',
                'description': 'Create a new support ticket',
                'parameters': ['customer', 'channel', 'subject', 'message', 'priority']
            },
            {
                'name': 'get_customer_history',
                'description': 'Get customer conversation history',
                'parameters': ['customer', 'limit']
            },
            {
                'name': 'send_response',
                'description': 'Send response to customer',
                'parameters': ['ticket_id', 'channel', 'customer', 'message', 'format_type']
            },
            {
                'name': 'escalate_to_human',
                'description': 'Escalate ticket to human support',
                'parameters': ['ticket_id', 'reason', 'priority']
            },
            {
                'name': 'analyze_sentiment',
                'description': 'Analyze sentiment of customer message',
                'parameters': ['text']
            },
            {
                'name': 'decide_escalation',
                'description': 'Decide if ticket should be escalated',
                'parameters': ['ticket', 'sentiment']
            }
        ]
