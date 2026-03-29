"""
Kafka Worker - Processes messages from Kafka and uses AI Agent
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka.consumer import KafkaConsumerService
from kafka.producer import KafkaProducerService
from prototype.ai_agent import AIAgent

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaWorker:
    """Worker that processes Kafka messages using AI Agent"""
    
    def __init__(self):
        self.consumer = KafkaConsumerService(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            group_id="crm-worker-group"
        )
        self.producer = KafkaProducerService(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        )
        self.agent = AIAgent()
        
    def process_message(self, topic: str, message: dict):
        """Process incoming message from Kafka"""
        logger.info(f"🔄 Processing message from {topic}")
        
        try:
            # Extract message data
            customer = message.get('customer', '')
            channel = message.get('channel', 'web')
            subject = message.get('subject', 'No Subject')
            content = message.get('content', '')
            priority = message.get('priority', 'medium')
            
            if not customer or not content:
                logger.warning("Invalid message: missing customer or content")
                return
            
            # Process with AI agent
            result = self.agent.process_message(
                customer=customer,
                channel=channel,
                subject=subject,
                message=content
            )
            
            # Send response via Kafka
            response_message = {
                'type': 'response',
                'ticket_id': result['ticket']['id'],
                'customer': customer,
                'channel': channel,
                'response': result['response'],
                'sentiment': result['sentiment'],
                'escalated': result['escalation_decision']['should_escalate'],
                'timestamp': datetime.now().isoformat()
            }
            
            self.producer.send_outgoing_message(response_message)
            
            # Send analytics event
            analytics_event = {
                'event_type': 'message_processed',
                'ticket_id': result['ticket']['id'],
                'channel': channel,
                'sentiment': result['sentiment']['sentiment'],
                'escalated': result['escalation_decision']['should_escalate'],
                'processing_time_ms': 0  # Add actual processing time
            }
            
            self.producer.send_analytics(analytics_event)
            
            logger.info(f"✅ Message processed successfully: {result['ticket']['id']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            
            # Send error to analytics
            error_event = {
                'event_type': 'processing_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.producer.send_analytics(error_event)
    
    def handle_error(self, error: Exception):
        """Handle consumer errors"""
        logger.error(f"❌ Consumer error: {error}")
    
    def start(self):
        """Start the worker"""
        logger.info("🚀 Starting Kafka Worker...")
        
        # Subscribe to incoming messages topic
        self.consumer.subscribe(["incoming_messages"])
        
        # Start consuming
        self.consumer.start_consuming(
            message_handler=self.process_message,
            error_handler=self.handle_error
        )
    
    def stop(self):
        """Stop the worker"""
        logger.info("⏹️  Stopping Kafka Worker...")
        self.consumer.close()
        self.producer.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 CRM Digital FTE - Kafka Worker")
    print("=" * 60)
    
    worker = KafkaWorker()
    
    try:
        worker.start()
    except KeyboardInterrupt:
        print("\n⏹️  Worker interrupted by user")
    finally:
        worker.stop()
