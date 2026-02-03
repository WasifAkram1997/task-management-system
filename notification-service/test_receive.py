"""
Simple script to RECEIVE messages from RabbitMQ
This is the CONSUMER
"""

import pika

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=pika.PlainCredentials('admin', 'rabbitmq_secure_pass_2024_ghi')
    )
)

channel = connection.channel()

# Make sure queue exists
channel.queue_declare(queue='test_queue')

# This function runs when we receive a message
def callback(ch, method, properties, body):
    message = body.decode()
    print(f"✓ Received: {message}")

# Tell RabbitMQ to call our callback function when message arrives
channel.basic_consume(
    queue='test_queue',
    on_message_callback=callback,
    auto_ack=True  # Automatically acknowledge receipt
)

print("Waiting for messages... Press CTRL+C to exit")
channel.start_consuming()