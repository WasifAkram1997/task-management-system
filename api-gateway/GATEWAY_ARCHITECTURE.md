# API Gateway Architecture: Two-Layer Design

## Overview

```
Client --> Nginx (Layer 1) --> FastAPI Gateway (Layer 2) --> Backend Services
```

The API gateway uses two complementary layers. Each layer does what it's best at.

## Layer 1: Nginx (Reverse Proxy)

Nginx sits in front of the application and handles concerns that are
cheap at the connection level but expensive in Python.

| Responsibility | How |
|---|---|
| **IP-based rate limiting** | `limit_req_zone` — drops abusive IPs before they hit Python |
| **Connection limiting** | `limit_conn_zone` — caps concurrent connections per IP |
| **Access logging** | Built-in `access_log` — method, path, status, latency |
| **TLS termination** | `ssl_certificate` / `ssl_certificate_key` (uncomment in nginx.conf) |
| **Security headers** | `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection` |
| **Client IP forwarding** | Sets `X-Real-IP` and `X-Forwarded-For` for the app layer |

**Config:** `nginx/nginx.conf`

## Layer 2: FastAPI Gateway (Application)

The Python gateway handles concerns that require business logic —
things Nginx fundamentally cannot do.

| Responsibility | How |
|---|---|
| **JWT validation** | Decodes Bearer tokens, extracts `user_id` and `email` |
| **User-aware rate limiting** | Redis-backed per-user limits (not per-IP, which Nginx handles) |
| **Auth header transformation** | Strips `Authorization`, injects `X-User-ID` / `X-User-Email` |
| **Structured logging** | JSON logs with authenticated user identity for audit trails |
| **Service routing** | Routes `auth/*` and `tasks/*` to the correct backend |

**Config:** `api-gateway/middleware.py`, `api-gateway/routes.py`

## Why not just one layer?

| "Just Nginx" | "Just Python" |
|---|---|
| Can't decode JWTs without Lua/njs hacks | Wastes Python processes on connection-level abuse |
| Can't do per-user rate limiting | Can't handle TLS termination efficiently |
| Can't inject custom headers based on token claims | Slow-client attacks tie up async workers |
| Path-based routing gets complex in Nginx for business rules | Basic access logging is redundant work |

## Configuration

### Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `BEHIND_PROXY` | Trust `X-Forwarded-For` headers from Nginx | `false` |
| `RATE_LIMIT_REQUESTS` | Max requests per user per window | `100` |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | `60` |

### Running with Nginx (production)

```bash
docker compose up
# Client -> :80 (Nginx) -> :8001 (Gateway) -> :8000/:8002 (Services)
```

### Running without Nginx (development)

```bash
# Just run the gateway directly
cd api-gateway && uvicorn main:app --reload --port 8001
# Client -> :8001 (Gateway) -> :8000/:8002 (Services)
# BEHIND_PROXY defaults to false, so X-Forwarded-For spoofing is ignored
```

## Rate Limiting Summary

| Layer | What it limits | Storage | Cost |
|---|---|---|---|
| Nginx | 30 req/s per IP, burst of 20 | In-memory (shared zone) | Nearly free |
| FastAPI | 100 req/60s per authenticated user | Redis | One INCR per request |

Anonymous abusers get blocked by Nginx. Authenticated abusers get blocked by the app.
