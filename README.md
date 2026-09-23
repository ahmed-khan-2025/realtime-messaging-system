<<<<<<< HEAD
# Real-Time Messaging System

A production-style real-time messaging application built with **Python and FastAPI**.

The project demonstrates real-time communication using **WebSockets**, message processing with **Redis Streams and Pub/Sub**, persistent storage with **PostgreSQL**, and secure authentication using **JWT**.

---

## Features

* User registration and login
* JWT authentication
* Chat rooms
* Room membership
* Real-time WebSocket messaging
* Redis Streams for message processing
* Redis Pub/Sub for typing events
* PostgreSQL message persistence
* Message history
* Typing indicators
* Asynchronous SQLAlchemy
* Background Redis worker
* Docker support
* Pytest
* Swagger/OpenAPI documentation
* Simple web-based frontend

---

## Architecture

```text
                    Browser Clients
                    User 1 / User 2
                           |
                           | WebSocket
                           v
                    +-------------+
                    |   FastAPI   |
                    |   WebSocket |
                    +------+------+
                           |
              +------------+------------+
              |                         |
              v                         v
        +-----------+             +-----------+
        | PostgreSQL|             |   Redis   |
        |-----------|             |-----------|
        | Users     |             | Streams   |
        | Rooms     |             | Pub/Sub   |
        | Members   |             |           |
        | Messages  |             +-----+-----+
        +-----------+                   |
                                        v
                              +------------------+
                              | Background Worker|
                              +--------+---------+
                                       |
                                       v
                              WebSocket Manager
                                       |
                                       v
                              Connected Clients
```

### Message Flow

1. User connects to a chat room using WebSocket.
2. FastAPI authenticates the user using JWT.
3. The message is stored in PostgreSQL.
4. The message is published to a Redis Stream.
5. The background worker reads the Redis Stream.
6. The worker broadcasts the message to connected WebSocket clients.
7. Typing events are handled through Redis Pub/Sub.

---

## Technology Stack

| Technology          | Purpose                 |
| ------------------- | ----------------------- |
| Python              | Backend development     |
| FastAPI             | REST API and WebSockets |
| SQLAlchemy          | Database ORM            |
| AsyncPG             | Async PostgreSQL driver |
| PostgreSQL          | Persistent data storage |
| Redis               | Streams and Pub/Sub     |
| JWT                 | Authentication          |
| Docker              | PostgreSQL and Redis    |
| Pytest              | Testing                 |
| HTML/CSS/JavaScript | Frontend                |
| Swagger/OpenAPI     | API documentation       |

---

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd realtime-messaging-system
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start PostgreSQL and Redis

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

You should have PostgreSQL and Redis running.

### 6. Start the application

```bash
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

Main API endpoints include:

```text
POST /auth/register
POST /auth/login

GET  /users/me

POST /rooms
GET  /rooms
POST /rooms/{room_id}/join

GET  /rooms/{room_id}/messages
```

WebSocket endpoint:

```text
/ws/rooms/{room_id}?token=<JWT>
```

---

## Running Tests

Run the test suite with:

```bash
python -m pytest -v
```

---

## Docker Services

The application uses Docker for infrastructure services:

```text
PostgreSQL
    Port: 5432

Redis
    Port: 6379
```

Start services:

```bash
docker compose up -d
```

Stop services:

```bash
docker compose down
```

---

## Security

* Passwords are securely hashed using bcrypt.
* JWT tokens are used for authentication.
* WebSocket connections require a valid JWT.
* Users must be members of a room before accessing its messages.
* Message length is validated before persistence.

---
## License

This project is intended for learning, portfolio development, and demonstration of backend engineering concepts.
=======
# realtime-messaging-system
>>>>>>> 3471a1c3a475ad54c3ec3b5d5c8840b8f194849b
