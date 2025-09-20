from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import execute_query

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simple single-user credentials (set via environment variables)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password123")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user = execute_query("SELECT id, username, email FROM users WHERE id = %s", (user_id,), fetch_one=True)
    
    if user is None:
        raise credentials_exception
    
    return {
        "id": user['id'],
        "username": user['username'],
        "email": user['email']
    }

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user with username and password"""
    # First try to get user from database
    user = execute_query("SELECT id, username, email, hashed_password FROM users WHERE username = %s", (username,), fetch_one=True)
    
    if user and verify_password(password, user['hashed_password']):
        return {
            "id": user['id'],
            "username": user['username'],
            "email": user['email']
        }
    
    # Fallback to environment variables for backward compatibility
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create user in database if it doesn't exist
        create_admin_user_if_not_exists()
        return {
            "id": 1,
            "username": ADMIN_USERNAME,
            "email": "admin@studybuddy.local"
        }
    
    return None

def create_admin_user_if_not_exists():
    """Create admin user in database if it doesn't exist"""
    existing_user = execute_query("SELECT id FROM users WHERE username = %s", (ADMIN_USERNAME,), fetch_one=True)
    
    if not existing_user:
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        
        conn = None
        cur = None
        try:
            from database import get_db_connection
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("INSERT INTO users (id, username, email, hashed_password) VALUES (%s, %s, %s, %s)", 
                       (1, ADMIN_USERNAME, "admin@studybuddy.local", hashed_password))
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Failed to create admin user: {e}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

def create_user(username: str, email: str, password: str) -> dict:
    """Create a new user"""
    # Check if user already exists
    existing_user = execute_query("SELECT id FROM users WHERE username = %s OR email = %s", (username, email), fetch_one=True)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(password)
    
    # Insert user into database
    conn = None
    cur = None
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s) RETURNING id", 
                   (username, email, hashed_password))
        user_id = cur.fetchone()[0]
        conn.commit()
        
        return {
            "id": user_id,
            "username": username,
            "email": email
        }
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
