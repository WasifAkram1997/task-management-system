def test_health_check(client):
    """Test if service is running"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user(client):
    """Test creation of a new user"""
    user_data = {
        "email": "apexkheliami@gmail.com",
        "password": "password123",
        "name": "Test User"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "apexkheliami@gmail.com"
    assert data["name"] == "Test User"
    assert "id" in data

def test_register_duplicate_email(client):
    """Test registering same email twice fails"""
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
    
    # Register first time
    client.post("/auth/register", json=user_data)
    
    # Try to register again with same email
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == 400

def test_login_success(client):
    """Test user can login"""
    # First register a user
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
    client.post("/auth/register", json=user_data)
    
    # Now login
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_wrong_password(client):
    """Test login fails with wrong password"""
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "correctpassword",
        "name": "Test User"
    }
    client.post("/auth/register", json=user_data)
    
    # Try to login with wrong password
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)
    
    assert response.status_code == 401

def test_get_current_user(client):
    """Test getting user profile with valid token"""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
    client.post("/auth/register", json=user_data)
    
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Get profile
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


def test_get_current_user_no_token(client):
    """Test getting profile without token fails"""
    response = client.get("/auth/me")
    
    assert response.status_code == 403


def test_refresh_token(client):
    """Test refreshing access token"""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
    client.post("/auth/register", json=user_data)
    
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token to get new access token
    response = client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_logout(client):
    """Test logout revokes refresh token"""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
    client.post("/auth/register", json=user_data)
    
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]
    
    # Logout
    response = client.post("/auth/logout", json={
        "refresh_token": refresh_token
    })
    
    assert response.status_code == 200
    
    # Try to use revoked token
    response = client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    
    assert response.status_code == 401