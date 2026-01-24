from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, init_db
from contextlib import asynccontextmanager
from config import get_settings
import models
import schemas
import auth

settings = get_settings()

@asynccontextmanager
async def lifespan(app:FastAPI):
    """Lifecycle events"""
    #code before yield is for startup and code after yield is for cleanup or shutdown
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Authentication service for task management system"
)

#Health check endpoint
@app.get("/health")
def health_check():
    return{
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION
    }


#Authentication endpoints

#User registration
@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db : Session = Depends(get_db)):
    """Register a new user"""

    #check if user already  exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists."
        )
    
    #create new user
    hashed_pwd = auth.hash_pwd(user_data.password)
    new_user = models.User(
        email=user_data.email,
        name= user_data.name,
        hashed_pwd = hashed_pwd
    )

    #Save to db
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


#User login
@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.LoginRequest, db: Session= Depends(get_db)):
    """Login and get access + refresh tokens"""

    #Try to get the user from db
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    #If user does not exist or password is wrong raise exception
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    #If user is not active disallow access
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    #All tests passed. Generate access and refresh tokens
    access_token = auth.create_access_token(user.id)
    refresh_token, refresh_expires = auth.create_refresh_token(user.id)

    db_refresh_token = models.RefreshToken(
        user_id= user.id,
        token = refresh_token,
        expires_at = refresh_expires
    )

    db.add(db_refresh_token)
    db.commit()

    return{
        "access_token": access_token,
        "refresh_token": refresh_token
    }


#Get new access token using refresh token
@app.post("/auth/refresh", response_model=schemas.AccessTokenResponse)
def refresh_access_token(refresh_token: schemas.RefreshTokenRequest, db : Session = Depends(get_db)):
    """Use refresh token to get a new access token"""

    #Decode the refresh token to get user id
    user_id = auth.verify_token(token=refresh_token, expected_type="refresh")

    #If none is returned raise exception
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    #Check database to make sure refresh token is in db and not revoked
    db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == refresh_token.refresh_token, models.RefreshToken.revoked == False ).first()

    #If token is not found in database, it means that it either does not exist or is revoked
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or is revoked"
        )
    
    #Check database to make sure that user exists and is active
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.is_active == True).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    #Create new access token
    access_token = auth.create_access_token(user_id)

    return{
        "access_token": access_token
    }

    



    






