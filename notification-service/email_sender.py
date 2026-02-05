"""
Email sender using SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send email via SMTP
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body (plain text)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = settings.SMTP_FROM_EMAIL
        message['To'] = to_email
        message['Subject'] = subject
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        
        # Login
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        # Send email
        server.send_message(message)
        server.quit()
        
        logger.info(f"✓ Email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False