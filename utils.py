import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import session
import database_models
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# This tells FastAPI exactly where users go to get their token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):

    # --- THE NEW BLOCKLIST CHECK ---
    db = session() # Open a quick database connection
    try:
        is_blocked = db.query(database_models.Blocklist).filter(
            database_models.Blocklist.token == token
        ).first()
    finally:
        db.close() # Always close it so we don't leak memory

    # If the token is in the database, kick them out immediately
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This token has been logged out. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- THE REGULAR CHECK ---
    # 1. Setup the generic error if the token is fake or expired
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 2. Try to unlock the token using your SECRET_KEY
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 3. Extract the user_id we packed inside it earlier
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise credentials_exception
            
        return user_id
        
    except JWTError:
        # If the token is expired or tampered with, it throws an error
        raise credentials_exception

    ##refresh token