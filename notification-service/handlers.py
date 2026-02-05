"""
Message handlers
Processes different types of notifications
"""

import logging
import json
from email_sender import send_email

logger = logging.getLogger(__name__)


def handle_notification(message_body: str) -> bool:
    """
    Process a notification message
    
    Args:
        message_body: JSON string from RabbitMQ
    
    Returns:
        True if processed successfully
        False if error (message should still be ACKed to avoid infinite retry)
    """
    try:
        # Parse the message
        data = json.loads(message_body)
        
        notification_type = data.get("type")
        
        if notification_type == "task_created":
            handle_task_created(data)
        elif notification_type == "task_updated":
            handle_task_updated(data)
        else:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False  # Unknown type, discard
        
        return True  # Successfully processed
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON message: {e}")
        logger.error(f"Message body: {message_body}")
        return False  # Bad JSON, discard (don't retry)
    
    except Exception as e:
        logger.error(f"Error handling notification: {e}")
        return False  # Unexpected error, discard


def handle_task_created(data: dict):
    """Handle task creation notification"""
    task_id = data.get("task_id")
    user_email = data.get("user_email")
    task_title = data.get("task_title")
    
    logger.info(f"📧 Task created notification for: {user_email}")

    subject = "New Task Created"
    body = f"""Hello!
    Your new task has been created sucessfully:
    Task ID: {task_id}
    Title: {task_title}

    Thank you for using our Task management system."""

    success = send_email(user_email, subject, body)

    if not success:
        logger.error(f"Failed to send email to {user_email}")



def handle_task_updated(data: dict):
    """Handle task update notification"""
    task_id = data.get("task_id")
    user_email = data.get("user_email")
    task_title = data.get("task_title")
    
    logger.info(f"📧 Task updated notification for: {user_email}")
    
    print("\n" + "="*50)
    print("📧 EMAIL NOTIFICATION")
    print("="*50)
    print(f"TO: {user_email}")
    print(f"SUBJECT: Task Updated")
    print(f"BODY:")
    print(f"  Task ID: {task_id}")
    print(f"  Title: {task_title}")
    print(f"  Your task has been updated!")
    print("="*50 + "\n")