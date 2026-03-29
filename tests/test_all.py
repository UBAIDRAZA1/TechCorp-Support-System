# CRM Digital FTE - Test Suite

"""
Test structure:

tests/
├── unit/                    # Unit tests
│   ├── test_mcp_tools.py
│   ├── test_ai_agent.py
│   ├── test_sentiment.py
│   └── test_channel_formatting.py
│
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_kafka.py
│   ├── test_database.py
│   └── test_webhooks.py
│
├── e2e/                     # End-to-end tests
│   ├── test_message_flow.py
│   ├── test_escalation_flow.py
│   └── test_multi_channel.py
│
└── conftest.py              # Pytest configuration

"""

import pytest
import json
from datetime import datetime


# ==================== UNIT TESTS ====================

class TestMCPTools:
    """Test MCP Tools"""
    
    def test_search_knowledge_base(self):
        """Test knowledge base search"""
        from prototype.mcp_tools import MCPTools
        
        tools = MCPTools()
        results = tools.search_knowledge_base("login issue")
        
        assert isinstance(results, list)
        assert len(results) > 0
    
    def test_create_ticket(self):
        """Test ticket creation"""
        from prototype.mcp_tools import MCPTools
        
        tools = MCPTools()
        ticket = tools.create_ticket(
            customer="test@example.com",
            channel="email",
            subject="Test",
            message="Test message"
        )
        
        assert ticket['id'].startswith('TKT-')
        assert ticket['status'] == 'open'
    
    def test_analyze_sentiment_positive(self):
        """Test positive sentiment analysis"""
        from prototype.mcp_tools import MCPTools
        
        tools = MCPTools()
        result = tools.analyze_sentiment("I love your product!")
        
        assert result['sentiment'] == 'positive'
    
    def test_analyze_sentiment_negative(self):
        """Test negative sentiment analysis"""
        from prototype.mcp_tools import MCPTools
        
        tools = MCPTools()
        result = tools.analyze_sentiment("This is terrible!")
        
        assert result['sentiment'] == 'negative'
    
    def test_decide_escalation(self):
        """Test escalation decision"""
        from prototype.mcp_tools import MCPTools
        
        tools = MCPTools()
        ticket = {'message': 'I want to cancel'}
        sentiment = {'sentiment': 'negative', 'confidence': 0.8}
        
        result = tools.decide_escalation(ticket, sentiment)
        
        assert result['should_escalate'] == True


class TestAIAgent:
    """Test AI Agent"""
    
    def test_process_message(self):
        """Test message processing"""
        from prototype.ai_agent import AIAgent
        
        agent = AIAgent()
        result = agent.process_message(
            customer="test@example.com",
            channel="email",
            subject="Login issue",
            message="Cannot login"
        )
        
        assert 'ticket' in result
        assert 'response' in result
    
    def test_channel_formatting_email(self):
        """Test email formatting"""
        from prototype.ai_agent import AIAgent
        
        agent = AIAgent()
        response = agent._generate_email_response(
            ticket={'subject': 'Test', 'message': 'Help'},
            kb_results=[],
            context=""
        )
        
        assert 'Dear' in response or 'Hello' in response
    
    def test_channel_formatting_whatsapp(self):
        """Test WhatsApp formatting"""
        from prototype.ai_agent import AIAgent
        
        agent = AIAgent()
        response = agent._generate_whatsapp_response(
            ticket={'subject': 'Test'},
            kb_results=[],
            context=""
        )
        
        assert len(response) < 200  # WhatsApp messages should be short


# ==================== INTEGRATION TESTS ====================

class TestAPIEndpoints:
    """Test API Endpoints"""
    
    def test_health_check(self):
        """Test health endpoint"""
        import requests
        
        response = requests.get("http://localhost:8000/health")
        
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    
    def test_post_message(self):
        """Test message endpoint"""
        import requests
        
        payload = {
            "customer": "test@example.com",
            "channel": "email",
            "subject": "Test",
            "message": "Test message"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/message",
            json=payload
        )
        
        assert response.status_code == 200
        assert 'ticket_id' in response.json()
    
    def test_get_stats(self):
        """Test stats endpoint"""
        import requests
        
        response = requests.get("http://localhost:8000/api/v1/stats")
        
        assert response.status_code == 200
        assert 'total_tickets' in response.json()


class TestKafka:
    """Test Kafka Integration"""
    
    def test_producer_send_message(self):
        """Test Kafka producer"""
        from kafka.producer import KafkaProducerService
        
        producer = KafkaProducerService()
        result = producer.send_incoming_message({
            "type": "test",
            "customer": "test@example.com"
        })
        
        assert result == True


class TestDatabase:
    """Test Database Operations"""
    
    def test_create_customer(self):
        """Test customer creation"""
        from sqlalchemy import create_engine
        from database.models import Customer, Base
        
        engine = create_engine("postgresql://postgres:postgres@localhost/crm_digital_fte")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1


# ==================== E2E TESTS ====================

class TestMessageFlow:
    """End-to-end message flow tests"""
    
    def test_complete_message_flow(self):
        """Test complete message processing flow"""
        import requests
        
        # 1. Send message
        payload = {
            "customer": "e2e@test.com",
            "channel": "web",
            "subject": "E2E Test",
            "message": "Testing complete flow"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/message",
            json=payload
        )
        
        ticket_id = response.json()['ticket_id']
        
        # 2. Check ticket status
        status_response = requests.get(
            f"http://localhost:8000/api/v1/message/{ticket_id}"
        )
        
        assert status_response.status_code == 200
        
        # 3. Check customer history
        history_response = requests.get(
            f"http://localhost:8000/api/v1/customer/e2e@test.com/history"
        )
        
        assert history_response.status_code == 200


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
