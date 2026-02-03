"""
Notification Service
Consumes messages from RabbitMQ and sends notifications
"""

import logging
from consumer import start_consuming

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("🚀 Starting Notification Service")
    start_consuming()