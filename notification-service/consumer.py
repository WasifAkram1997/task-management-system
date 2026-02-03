"""
RabbitMQ consumer for notification service.
Listens to messages and processes them.
"""

import logging
from rabbitmq import rabbitmq_service
from handlers import handle_notification
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body):
    """
    Called every time a message is received
    
    :param ch: Channel
    :param method: Delivery method
    :param properties: Message properties
    :param body: Message body
    """
    try:
        message = body.decode("utf-8")
        logger.info("Received message")
        success = handle_notification(message)
        if success:
            logger.info("Message processed")
        else:
            logger.info("Message had errors. Acknowledged and discarded")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error in consumer callback: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    """
    Start listening for messages. This runs infinitely until interrupted
    """
    try:
        rabbitmq_service.connect()

        #Give me one message at a time for processing. Controlled by prefetch count
        rabbitmq_service.channel.basic_qos(prefetch_count=1)

        #Start consuming messages. Auto ack is set to false since we acknowledge manually
        rabbitmq_service.channel.basic_consume(
            queue=settings.QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False
        )

        logger.info(f"Listening to messages from queue: {settings.QUEUE_NAME}")

        rabbitmq_service.channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
        rabbitmq_service.disconnect()
    
    except Exception as e:
        logger.error(f"Error in consumer: {e}")
        rabbitmq_service.disconnect()
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    start_consuming()