import pytest

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_rate_limiting(client):
    for i in range(101):
        response = client.get("/health")
        if i <= 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429

# def test_rate_limit_headers(client):
#     """Test rate limit headers are present"""
#     response = client.get("/health")
    
#     assert "X-RateLimit-Limit" in response.headers
#     assert "X-RateLimit-Remaining" in response.headers


# def test_public_auth_endpoints_no_token(client):
#     """Test public auth endpoints work without token"""
#     # Register endpoint (will fail validation but not auth)
#     response = client.post("/auth/register", json={})
#     assert response.status_code != 401
#     assert response.status_code != 403
    
#     # Login endpoint
#     response = client.post("/auth/login", json={})
#     assert response.status_code != 401
#     assert response.status_code != 403


# def test_protected_endpoint_no_token(client):
#     """Test protected endpoints require authentication"""
#     response = client.get("/tasks")
#     assert response.status_code == 401


# def test_protected_endpoint_invalid_token(client):
#     """Test invalid token returns 401"""
#     headers = {"Authorization": "Bearer invalid_token_here"}
#     response = client.get("/tasks", headers=headers)
#     assert response.status_code == 401


# def test_unknown_route(client):
#     """Test unknown routes return 404"""
#     response = client.get("/nonexistent/route")
#     assert response.status_code == 404