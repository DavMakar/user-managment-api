import pika
import json
import os
import logging
from pika.exceptions import AMQPConnectionError

logger = logging.getLogger(__name__)

class RabbitMQService:
    """RabbitMQ service for publishing and consuming messages"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connected = False
        self.exchange_name = 'user_events'
        self.queue_name = 'user_notifications'
        
        # RabbitMQ Configuration
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.user = os.getenv('RABBITMQ_USER', 'guest')
        self.password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.vhost = os.getenv('RABBITMQ_VHOST', '/')
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=credentials,
                connection_attempts=5,
                retry_delay=2,
                heartbeat=600
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            # Declare queue
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key='user.*'
            )
            
            self.connected = True
            logger.info(f"✓ RabbitMQ connected: {self.host}:{self.port}")
            return True
            
        except AMQPConnectionError as e:
            logger.error(f"✗ Failed to connect to RabbitMQ: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"✗ Unexpected error connecting to RabbitMQ: {e}")
            self.connected = False
            return False
    
    def publish_event(self, event_type, user_data):
        """Publish event to RabbitMQ"""
        if not self.connected or not self.channel:
            logger.warning("RabbitMQ not connected. Event not published.")
            return False
        
        try:
            message = {
                'event_type': event_type,
                'user_id': user_data.get('id'),
                'user_data': user_data,
                'timestamp': str(__import__('datetime').datetime.utcnow())
            }
            
            routing_key = f'user.{event_type}'
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=json.dumps(message, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published {event_type} event for user {user_data.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def consume_events(self, callback):
        """Consume events from RabbitMQ"""
        if not self.connected or not self.channel:
            logger.error("RabbitMQ not connected. Cannot consume events.")
            return False
        
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info(f"✓ Started consuming from queue: {self.queue_name}")
            self.channel.start_consuming()
            return True
            
        except Exception as e:
            logger.error(f"Failed to consume events: {e}")
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
        self.connected = False

# Global RabbitMQ service instance
rabbitmq_service = None

def get_rabbitmq_service():
    """Get or create RabbitMQ service instance"""
    global rabbitmq_service
    if rabbitmq_service is None:
        rabbitmq_service = RabbitMQService()
    return rabbitmq_service

def init_rabbitmq(max_retries=10, retry_delay=5):
    """Initialize RabbitMQ connection with retries"""
    service = get_rabbitmq_service()
    for i in range(max_retries):
        logger.info(f"Attempting to connect to RabbitMQ (attempt {i+1}/{max_retries})...")
        if service.connect():
            return True
        import time
        time.sleep(retry_delay)
    logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts.")
    return False