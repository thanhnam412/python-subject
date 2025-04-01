import os
import logging
import secrets
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import EmailStr
from database import SessionLocal, get_db
from models import User
from schemas import UserCreate, UserResponse, MessageResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter(tags=["Authentication"], prefix="/auth")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

mail_username = os.getenv("MAIL_USERNAME")
mail_password = os.getenv("MAIL_PASSWORD")
mail_from = os.getenv("MAIL_FROM")

if not mail_username or not mail_password or not mail_from:
    logger.error("Missing required environment variables: MAIL_USERNAME, MAIL_PASSWORD, or MAIL_FROM")
    raise ValueError("Missing required environment variables: MAIL_USERNAME, MAIL_PASSWORD, or MAIL_FROM")

def str_to_bool(value: str) -> bool:
    if value is None:
        return False
    return value.lower() in ("true", "1", "yes", "on")

try:
    mail_conf = ConnectionConfig(
        MAIL_USERNAME=mail_username,
        MAIL_PASSWORD=mail_password,
        MAIL_FROM=mail_from,
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Expense Tracker"),
        MAIL_STARTTLS=str_to_bool(os.getenv("MAIL_STARTTLS", "True")),
        MAIL_SSL_TLS=str_to_bool(os.getenv("MAIL_SSL_TLS", "False"))
    )
    logger.info("ConnectionConfig initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ConnectionConfig: {str(e)}")
    raise

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    return UserResponse.from_orm(user)

@router.post("/register", response_model=UserResponse, description="Register a new user with username, email, and password.")
async def register(user: UserCreate, db: SessionLocal = Depends(get_db)):
    logger.info(f"Register attempt for email: {user.email}")
    if db.query(User).filter(User.email == user.email).first():
        logger.warning(f"Email already registered: {user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        logger.warning(f"Username already taken: {user.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    
    if len(user.password) < 8:
        logger.warning(f"Password too short for email: {user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")

    hashed_password = hash_password(user.password)
    verification_token = secrets.token_urlsafe(32)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_verified=False,
        verification_token=verification_token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    message = MessageSchema(
        subject="Verify Your Email",
        recipients=[user.email],
        body=f"Click this link to verify your email: http://127.0.0.1:5000/auth/verify-email?token={verification_token}",
        subtype="html"
    )
    fm = FastMail(mail_conf)
    await fm.send_message(message)
    logger.info(f"Verification email sent to: {user.email}")

    logger.info(f"User registered successfully: {db_user.user_id}")
    return UserResponse.from_orm(db_user)

@router.get("/verify-email", response_model=MessageResponse, description="Verify the user's email using a verification token.")
async def verify_email(token: str, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        logger.warning("Email verification failed: Invalid token")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    logger.info(f"Email verified for user: {user.user_id}")
    return {"message": "Email verified successfully"}

@router.post("/login", description="Log in with email and password to receive an access token.")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        logger.warning(f"Login failed for email {form_data.username}: Email not verified")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.user_id)}, expires_delta=access_token_expires)
    logger.info(f"User logged in successfully: {user.user_id}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", response_model=MessageResponse, description="Log out the current user (client-side token removal).")
async def logout():
    logger.info("User logged out")
    return {"message": "Logged out successfully"}

@router.get("/profile", response_model=UserResponse, description="Get the profile of the currently authenticated user.")
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    logger.info(f"Profile accessed for user: {current_user.user_id}")
    return current_user

@router.put("/profile", response_model=UserResponse, description="Update the profile of the currently authenticated user (username or email).")
async def update_profile(
    username: Optional[str] = None,
    email: Optional[EmailStr] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    
    if (username == user.username or username is None) and (email == user.email or email is None):
        logger.info(f"No changes made to profile for user: {current_user.user_id}")
        return UserResponse.from_orm(user)

    if username and username != user.username:
        if db.query(User).filter(User.username == username).first():
            logger.warning(f"Username already taken: {username}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        user.username = username

    if email and email != user.email:
        if db.query(User).filter(User.email == email).first():
            logger.warning(f"Email already registered: {email}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user.email = email
        user.is_verified = False
        verification_token = secrets.token_urlsafe(32)
        user.verification_token = verification_token

        message = MessageSchema(
            subject="Verify Your New Email",
            recipients=[email],
            body=f"Click this link to verify your new email: http://127.0.0.1:5000/auth/verify-email?token={verification_token}",
            subtype="html"
        )
        fm = FastMail(mail_conf)
        await fm.send_message(message)
        logger.info(f"Verification email sent to new email: {email}")
    
    db.commit()
    db.refresh(user)
    logger.info(f"Profile updated for user: {current_user.user_id}")
    return UserResponse.from_orm(user)

@router.post("/forgot-password", response_model=MessageResponse, description="Request a password reset link to be sent to the user's email.")
async def forgot_password(email: EmailStr, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click this link to reset your password: http://127.0.0.1:5000/reset-password?token={token}",
        subtype="html"
    )
    fm = FastMail(mail_conf)
    await fm.send_message(message)
    logger.info(f"Password reset email sent to: {email}")
    return {"message": "Password reset email sent"}

@router.post("/reset-password", response_model=MessageResponse, description="Reset the user's password using a valid reset token.")
async def reset_password(token: str, new_password: str, db: SessionLocal = Depends(get_db)):
    if len(new_password) < 8:
        logger.warning("Password reset failed: Password too short")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
    
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or user.reset_token_expiry < datetime.utcnow():
        logger.warning("Password reset failed: Invalid or expired token")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    user.password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    logger.info(f"Password reset successful for user: {user.user_id}")
    return {"message": "Password reset successful"}