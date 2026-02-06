import pytest

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# def test_rate_limiting(client):
#     for i in range(102):
#         response = client.get("/health")
#         if i <= 100:
#             assert response.status_code == 200
#         else:
#             assert response.status_code == 429