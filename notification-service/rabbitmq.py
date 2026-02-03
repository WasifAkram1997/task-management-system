"""
Rabbitmq connection handler
"""

import pika
import logging
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class RabbitMQService:
    """Manage rabbitmq connection and channel"""

    def __init__(self):
        """Initialization with attributes connection and channel"""
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to rabbitmq and create channel"""
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )

            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials
            )

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            self.channel.queue_declare(queue=settings.QUEUE_NAME, durable=True)

            logger.info(f"✓ Connected to RabbitMQ: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
            logger.info(f"✓ Queue declared: {settings.QUEUE_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to rabbitmq: {e}")
            raise
    
    def disconnect(self):
        """Close connection gracefully"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Rabbitmq connection closed")


rabbitmq_service = RabbitMQService()