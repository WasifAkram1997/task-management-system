"""
On Task creation/update publish notification messages
"""

import pika
import json
import logging
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

def publish_notification(notification_type: str, data: dict):
    """
    Publishes message to rabbitmq
    
    :param notification_type: Type of notification(task_created, task_updated)
    :type notification_type: str
    :param data: Notification data
    :type data: dict
    """

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

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        message = {
            "type": notification_type,
            **data
        }
        
        channel.basic_publish(
            exchange='',
            routing_key=settings.RABBITMQ_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        
        logger.info(f"Published notification: {notification_type}")

        connection.close()
    except Exception as e:
        logger.error(f"Failed to publish notification: {e}")
        