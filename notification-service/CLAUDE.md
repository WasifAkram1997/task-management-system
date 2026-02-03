# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Service Overview

The notification service is part of a microservices-based task management system. It consumes messages from RabbitMQ and sends notifications (currently email) to users when tasks are created or updated.

## Architecture

This is an event-driven consumer service that:
1. Connects to RabbitMQ on startup
2. Listens to the `notifications` queue for messages
3. Processes messages based on notification type (`task_created`, `task_updated`)
4. Sends notifications via configured channels (email via SMTP)

### Key Components

- **config.py**: Loads environment variables using pydantic-settings. Settings are cached with `@lru_cache()`. Reads from `../.env` (parent directory)
- **rabbitmq.py**: Manages RabbitMQ connection lifecycle. Exports singleton `rabbitmq_service` instance. Uses blocking connection for synchronous message consumption
- **handlers.py**: Routes and processes notification messages. Each handler function corresponds to a notification type

### Message Flow

```
Task Service → RabbitMQ → Notification Service → Email/SMS/etc
```

Messages are JSON with the following structure:
```json
{
  "type": "task_created" | "task_updated",
  "task_id": "uuid",
  "user_email": "user@example.com",
  "task_title": "Task title"
}
```

## Environment Setup

This service requires environment variables defined in `../.env` (parent directory):

**Required:**
- `RABBITMQ_USER`: RabbitMQ username
- `RABBITMQ_PASSWORD`: RabbitMQ password

**Optional (for email notifications):**
- `SMTP_HOST`: SMTP server hostname (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USER`: Email sender address
- `SMTP_PASSWORD`: Email sender password

## Development Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Testing RabbitMQ Connection

Send a test message:
```bash
python test_send.py
```

Receive test messages:
```bash
python test_receive.py
```

### Running the Service

Currently, there's no main entry point. To implement the consumer, create a main script that:
1. Calls `rabbitmq_service.connect()`
2. Sets up message consumption with `handlers.handle_notification` as callback
3. Calls `channel.start_consuming()`

## Integration with System

This service integrates with:
- **RabbitMQ**: Shared message broker running in Docker (port 5672, management UI on 15672)
- **Task Service**: Publishes messages when tasks are created/updated
- **Auth Service**: Provides user information (email addresses)

All services communicate via the `task-network` Docker network defined in `../docker-compose.yml`.

## Current State

The service is partially implemented:
- ✅ RabbitMQ connection management
- ✅ Message routing by notification type
- ✅ Basic handlers for task_created and task_updated
- ⚠️ Email sending is stubbed (prints to console instead)
- ⚠️ No main consumer loop implemented
- ⚠️ No error recovery or retry logic

## Important Patterns

### Singleton Pattern
`rabbitmq_service` in rabbitmq.py is a singleton instance. Import and use it directly:
```python
from rabbitmq import rabbitmq_service
rabbitmq_service.connect()
```

### Handler Registration
Add new notification types by:
1. Adding a handler function in handlers.py
2. Adding a case in `handle_notification()` dispatcher

### Configuration Loading
Settings are loaded once and cached. To reload settings, restart the service.
