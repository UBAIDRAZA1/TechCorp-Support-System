"""
Kafka Consumer for CRM Digital FTE
Consumes messages from Kafka topics and processes them
"""

import json
import logging
from typing import Dict, Any, Callable, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """Kafka Consumer Service for processing messages"""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "crm-digital-fte-group",
        auto_offset_reset: str = "latest"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.consumer = None
        self.running = False
        self._connect()
    
    def _connect(self):
        """Connect to Kafka"""
        try:
            self.consumer = KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info(f"✅ Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kafka: {e}")
            raise
    
    def subscribe(self, topics: list):
        """Subscribe to Kafka topics"""
        if self.consumer:
            self.consumer.subscribe(topics)
            logger.info(f"📬 Subscribed to topics: {topics}")
    
    def start_consuming(
        self,
        message_handler: Callable[[str, Dict[str, Any]], None],
        error_handler: Optional[Callable[[Exception], None]] = None
    ):
        """
        Start consuming messages
        
        Args:
            message_handler: Function to handle messages (topic, message)
            error_handler: Optional function to handle errors
        """
        if not self.consumer:
            logger.error("Kafka consumer not connected")
            return
        
        self.running = True
        logger.info("🚀 Starting to consume messages...")
        
        try:
            while self.running:
                try:
                    # Poll for messages
                    messages = self.consumer.poll(timeout_ms=1000)
                    
                    for topic_partition, records in messages.items():
                        for record in records:
                            try:
                                message_handler(record.topic, record.value)
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")
                                if error_handler:
                                    error_handler(e)
                    
                except Exception as e:
                    logger.error(f"Error polling messages: {e}")
                    if error_handler:
                        error_handler(e)
                    time.sleep(1)  # Wait before retrying
                    
        except KeyboardInterrupt:
            logger.info("⏹️  Consumer interrupted by user")
        finally:
            self.stop_consuming()
    
    def start_consuming_async(
        self,
        message_handler: Callable[[str, Dict[str, Any]], None],
        error_handler: Optional[Callable[[Exception], None]] = None
    ) -> threading.Thread:
        """Start consuming in a separate thread"""
        thread = threading.Thread(
            target=self.start_consuming,
            args=(message_handler, error_handler),
            daemon=True
        )
        thread.start()
        return thread
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.running = False
        logger.info("⏹️  Stopping consumer...")
    
    def close(self):
        """Close the consumer"""
        self.stop_consuming()
        if self.consumer:
            self.consumer.close()
            logger.info("🔌 Kafka consumer closed")


# ==================== USAGE EXAMPLE ====================

def handle_message(topic: str, message: Dict[str, Any]):
    """Example message handler"""
    logger.info(f"📨 Received message from {topic}:")
    logger.info(f"   Customer: {message.get('customer', 'N/A')}")
    logger.info(f"   Channel: {message.get('channel', 'N/A')}")
    logger.info(f"   Subject: {message.get('subject', 'N/A')}")
    logger.info(f"   Content: {message.get('content', 'N/A')[:50]}...")
    
    # Process the message here
    # For example, call AI agent to generate response


def handle_error(error: Exception):
    """Example error handler"""
    logger.error(f"❌ Error: {error}")


if __name__ == "__main__":
    # Create consumer
    consumer = KafkaConsumerService()
    
    # Subscribe to topics
    consumer.subscribe(["incoming_messages"])
    
    # Start consuming
    print("🚀 Starting Kafka consumer... Press Ctrl+C to stop")
    
    try:
        consumer.start_consuming(
            message_handler=handle_message,
            error_handler=handle_error
        )
    except KeyboardInterrupt:
        print("\n⏹️  Stopping...")
    finally:
        consumer.close()
