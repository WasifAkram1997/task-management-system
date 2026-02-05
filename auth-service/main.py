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
    description="Authentication service for task management system",
    lifespan=lifespan
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
        hashed_password = hashed_pwd
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
    access_token = auth.create_access_token(user.id, user.email)
    refresh_token, refresh_expires = auth.create_refresh_token(user.id, user.email)

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
    user_id = auth.verify_token(token=refresh_token.refresh_token, expected_type="refresh")

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
    access_token = auth.create_access_token(db_user.id, db_user.email)

    return{
        "access_token": access_token
    }

#User logout
@app.post("/auth/logout", response_model=schemas.MessageResponse)
def logout(request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    """Logout and revoke refresh token"""

    db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == request.refresh_token).first()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found."
        )
    
    db_token.revoked = True
    db.commit()

    return {"message": "Logged out successfully"}

#Get current user
@app.get("/auth/me", response_model=schemas.UserResponse)
def get_current_user_profile(current_user: models.User = Depends(auth.get_current_user)):
    """Get current authenticated user profile"""
    return current_user

@app.put("/auth/me", response_model=schemas.UserResponse)
def update_profile(
    update_data: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    
    # Update email if provided
    if update_data.email is not None:
        # Check if new email already exists
        existing_user = db.query(models.User).filter(
            models.User.email == update_data.email,
            models.User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        
        current_user.email = update_data.email
    
    # Update name if provided
    if update_data.name is not None:
        current_user.name = update_data.name
    
    # Save changes
    db.commit()
    db.refresh(current_user)
    
    return current_user
    



    






