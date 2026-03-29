"""
WhatsApp Integration for CRM Digital FTE
Receives and sends messages via Twilio WhatsApp API
"""

import os
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
from flask import Flask, request, jsonify

from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

from kafka.producer import KafkaProducerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppIntegration:
    """WhatsApp Integration via Twilio"""
    
    def __init__(
        self,
        account_sid: str = None,
        auth_token: str = None,
        whatsapp_number: str = None,
        webhook_port: int = 5000
    ):
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = whatsapp_number or os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.webhook_port = webhook_port
        self.client = None
        self.producer = KafkaProducerService()
        self.app = Flask(__name__)
        self._setup_routes()
        self._connect()
    
    def _connect(self):
        """Connect to Twilio"""
        try:
            if self.account_sid and self.auth_token:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info(f"✅ Connected to Twilio WhatsApp: {self.whatsapp_number}")
            else:
                logger.warning("⚠️  Twilio credentials not configured. Running in demo mode.")
        except Exception as e:
            logger.error(f"❌ Twilio connection failed: {e}")
            raise
    
    def send_message(
        self,
        to: str,
        body: str,
        media_urls: Optional[List[str]] = None
    ) -> bool:
        """
        Send WhatsApp message
        
        Args:
            to: Recipient WhatsApp number (with country code)
            body: Message body
            media_urls: Optional list of media URLs
            
        Returns:
            True if sent successfully
        """
        try:
            # Format numbers
            to_number = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
            from_number = self.whatsapp_number
            
            if self.client:
                # Send via Twilio
                message = self.client.messages.create(
                    from_=from_number,
                    body=body,
                    to=to_number
                )
                
                logger.info(f"📤 WhatsApp sent to {to_number}: {message.sid}")
            else:
                # Demo mode - just log
                logger.info(f"📤 [DEMO] WhatsApp to {to_number}: {body[:50]}...")
                message = type('obj', (object,), {'sid': 'demo_' + datetime.now().strftime('%Y%m%d%H%M%S')})
            
            # Send to Kafka for tracking
            self.producer.send_outgoing_message({
                'type': 'whatsapp',
                'channel': 'whatsapp',
                'customer': to_number,
                'content': body,
                'message_id': message.sid,
                'timestamp': datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {e}")
            return False
    
    def _setup_routes(self):
        """Setup Flask webhook routes"""
        
        @self.app.route('/webhook/whatsapp', methods=['POST'])
        def receive_webhook():
            """Receive WhatsApp webhook from Twilio"""
            try:
                # Get message data
                from_number = request.form.get('From', '')
                to_number = request.form.get('To', '')
                body = request.form.get('Body', '')
                message_sid = request.form.get('MessageSid', '')
                
                logger.info(f"📬 WhatsApp received from {from_number}: {body[:50]}...")
                
                # Send to Kafka for processing
                self.producer.send_incoming_message({
                    'type': 'whatsapp',
                    'channel': 'whatsapp',
                    'customer': from_number,
                    'content': body,
                    'priority': 'medium',
                    'message_id': message_sid,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Respond to Twilio
                return jsonify({'status': 'received'}), 200
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/webhook/whatsapp', methods=['GET'])
        def verify_webhook():
            """Verify webhook for Twilio"""
            return request.args.get('hub.challenge', ''), 200
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check"""
            return jsonify({'status': 'healthy', 'service': 'whatsapp'}), 200
    
    def start_webhook(self, host: str = '0.0.0.0', port: int = None):
        """
        Start webhook server
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        port = port or self.webhook_port
        logger.info(f"🚀 Starting WhatsApp webhook server on port {port}")
        
        # Disable Flask development server warning in production
        self.app.run(host=host, port=port, debug=False, threaded=True)
    
    def send_template(
        self,
        to: str,
        template_name: str,
        language: str = "en_US",
        components: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send WhatsApp template message
        
        Args:
            to: Recipient number
            template_name: Template name from Twilio
            language: Template language
            components: Template components/variables
            
        Returns:
            True if sent successfully
        """
        try:
            to_number = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
            
            if self.client:
                message = self.client.messages.create(
                    from_=self.whatsapp_number,
                    content_sid=template_name,
                    content_variables=str(components or {}),
                    to=to_number
                )
                
                logger.info(f"📤 WhatsApp template sent: {message.sid}")
            else:
                logger.info(f"📤 [DEMO] WhatsApp template: {template_name}")
                message = type('obj', (object,), {'sid': 'demo_template_' + datetime.now().strftime('%Y%m%d%H%M%S')})
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send template: {e}")
            return False
    
    def send_quick_reply(
        self,
        to: str,
        body: str,
        options: List[str]
    ) -> bool:
        """
        Send message with quick reply options
        
        Args:
            to: Recipient number
            body: Message body
            options: List of quick reply options
            
        Returns:
            True if sent successfully
        """
        # Format with options
        formatted_body = f"{body}\n\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        return self.send_message(to, formatted_body)


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("=" * 60)
    print("📱 WhatsApp Integration - CRM Digital FTE")
    print("=" * 60)
    
    # Initialize WhatsApp integration
    whatsapp = WhatsAppIntegration()
    
    # Send test message
    # whatsapp.send_message(
    #     to="+1234567890",
    #     body="Hello! This is a test message from TechCorp Support. 🤖"
    # )
    
    # Start webhook server
    print("🚀 Starting WhatsApp webhook server...")
    whatsapp.start_webhook(port=5000)
