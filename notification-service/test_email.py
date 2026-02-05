"""
Test email sending
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your Gmail credentials
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "wasifakram@iut-dhaka.edu"           # ← Change this
SMTP_PASSWORD = "bfmp bfgj ddes wtqk"  # ← Change this
FROM_EMAIL = "wasifakram@iut-dhaka.edu"          # ← Change this
TO_EMAIL = "apexkheliami@gmail.com"            # ← Can send to yourself for testing

try:
    print("Connecting to Gmail...")
    
    # Create message
    message = MIMEMultipart()
    message['From'] = FROM_EMAIL
    message['To'] = TO_EMAIL
    message['Subject'] = "Test Email from Task Management System"
    
    body = "Hello! This is a test email from your notification service. It works! 🎉"
    message.attach(MIMEText(body, 'plain'))
    
    # Connect and send
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    print("Logging in...")
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("Sending email...")
    server.send_message(message)
    server.quit()
    
    print("✓ Email sent successfully!")
    print(f"Check your inbox: {TO_EMAIL}")
    
except Exception as e:
    print(f"✗ Error: {e}")