import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=pika.PlainCredentials('admin','rabbitmq_secure_pass_2024_ghi')))
channel = connection.channel()
channel.queue_declare(queue='test_queue')
message = 'Hello, RabbitMQ!'
channel.basic_publish(exchange='', routing_key='test_queue', body=message)
print(f" [x] Sent '{message}'")
connection.close()