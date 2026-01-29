"""
Pydantic schemas for request/response validation
Defines the API contract
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

# User Schemas

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for user profile update"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Authentication Schemas

class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Schema for access token response"""
    access_token: str
    token_type: str = "bearer"

# Standard Response Schemas

class MessageResponse(BaseModel):
    """Standard message response"""
    message: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None