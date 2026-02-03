"""
Test script to send a message to the notifications queue
"""

import pika
import json

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=pika.PlainCredentials('admin', 'rabbitmq_secure_pass_2024_ghi')
    )
)

channel = connection.channel()

# Create test message
message = {
    "type": "task_created",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_email": "test@example.com",
    "task_title": "My Test Task"
}

# Send message
channel.basic_publish(
    exchange='',
    routing_key='notifications',
    body=json.dumps(message)
)

print(f"✓ Sent test message")
connection.close()