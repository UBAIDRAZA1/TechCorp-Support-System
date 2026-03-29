"""
Kafka Producer for CRM Digital FTE
Sends messages to Kafka topics
"""

import json
import logging
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaProducerService:
    """Kafka Producer Service for sending messages"""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Connect to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                retry_backoff_ms=100
            )
            logger.info(f"✅ Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kafka: {e}")
            raise
    
    def send_message(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """
        Send a message to Kafka topic
        
        Args:
            topic: Kafka topic name
            message: Message dictionary
            key: Optional message key
            
        Returns:
            True if sent successfully
        """
        if not self.producer:
            logger.error("Kafka producer not connected")
            return False
        
        try:
            # Add metadata
            message['timestamp'] = datetime.now().isoformat()
            message['message_id'] = str(uuid.uuid4())
            
            # Send to Kafka
            future = self.producer.send(
                topic,
                value=message,
                key=key
            )
            
            # Wait for confirmation
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"📤 Message sent to {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def send_incoming_message(self, message: Dict[str, Any]) -> bool:
        """Send incoming message to incoming_messages topic"""
        return self.send_message("incoming_messages", message)
    
    def send_outgoing_message(self, message: Dict[str, Any]) -> bool:
        """Send outgoing message to outgoing_messages topic"""
        return self.send_message("outgoing_messages", message)
    
    def send_escalation(self, message: Dict[str, Any]) -> bool:
        """Send escalation to escalations topic"""
        return self.send_message("escalations", message)
    
    def send_analytics(self, message: Dict[str, Any]) -> bool:
        """Send analytics event to analytics topic"""
        return self.send_message("analytics", message)
    
    def flush(self):
        """Flush all pending messages"""
        if self.producer:
            self.producer.flush()
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("🔌 Kafka producer closed")


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Create producer
    producer = KafkaProducerService()
    
    # Send test message
    test_message = {
        "type": "test",
        "channel": "web",
        "customer": "test@example.com",
        "subject": "Test Message",
        "content": "This is a test message",
        "priority": "low"
    }
    
    # Send to incoming messages topic
    producer.send_incoming_message(test_message)
    
    # Flush and close
    producer.flush()
    producer.close()
    
    print("✅ Test message sent!")
