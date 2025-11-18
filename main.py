from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, field_validator
from typing import Optional
import json
import os
import hashlib
import jwt
import re
from datetime import datetime, timedelta

app = FastAPI()

# Configuration
USERS_FILE = "users.json"
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

# Pydantic Models
class SignUpRequest(BaseModel):
    username: str
    password: str
    fname: str
    lname: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v:
            raise ValueError('username is required')
        if len(v) < 4:
            raise ValueError('username must be at least 4 characters')
        if not re.match(r'^[a-z]+$', v):
            raise ValueError('username can only contain lowercase English alphabets')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v:
            raise ValueError('password is required')
        if len(v) < 5:
            raise ValueError('password must be at least 5 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('password must contain at least 1 uppercase character')
        if not re.search(r'[a-z]', v):
            raise ValueError('password must contain at least 1 lowercase character')
        if not re.search(r'\d', v):
            raise ValueError('password must contain at least 1 number')
        if re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('password cannot contain special characters')
        return v
    
    @field_validator('fname', 'lname')
    @classmethod
    def validate_name(cls, v):
        if not v:
            raise ValueError('name is required')
        if not re.match(r'^[A-Za-z]+$', v):
            raise ValueError('name should only contain English alphabets')
        return v

class SignInRequest(BaseModel):
    username: str
    password: str

# Helper Functions
def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt_token(username: str, fname: str) -> str:
    """Create JWT token with username and firstname"""
    payload = {
        'username': username,
        'fname': fname,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail={
            "result": False,
            "error": "JWT Verification Failed"
        })

# API Endpoints
@app.post("/signup", status_code=201)
async def signup(request: SignUpRequest):
    """User signup endpoint"""
    try:
        users = load_users()
        
        # Check if username already exists
        if request.username in users:
            raise HTTPException(status_code=400, detail={
                "result": False,
                "error": "Username already exists"
            })
        
        # Hash password and store user
        hashed_password = hash_password(request.password)
        users[request.username] = {
            "username": request.username,
            "password": hashed_password,
            "fname": request.fname,
            "lname": request.lname
        }
        
        save_users(users)
        
        return {
            "result": True,
            "message": "SignUp success. Please proceed to Signin"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail={
            "result": False,
            "error": str(e)
        })

@app.post("/signin", status_code=200)
async def signin(request: SignInRequest):
    """User signin endpoint"""
    try:
        users = load_users()
        
        # Check if user exists
        if request.username not in users:
            raise HTTPException(status_code=400, detail={
                "result": False,
                "error": "Invalid credentials"
            })
        
        user = users[request.username]
        hashed_password = hash_password(request.password)
        
        # Verify password
        if user['password'] != hashed_password:
            raise HTTPException(status_code=400, detail={
                "result": False,
                "error": "Invalid credentials"
            })
        
        # Create JWT token
        token = create_jwt_token(request.username, user['fname'])
        
        return {
            "result": True,
            "jwt": token,
            "message": "Signin success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            "result": False,
            "error": "Invalid request"
        })

@app.get("/user/me", status_code=200)
async def get_user_info(authorization: Optional[str] = Header(None)):
    """Get user information endpoint"""
    if not authorization:
        raise HTTPException(status_code=400, detail={
            "result": False,
            "error": "Please provide a JWT token"
        })
    
    # Extract token (handle "Bearer <token>" format)
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    
    # Verify token
    payload = verify_jwt_token(token)
    username = payload.get('username')
    
    # Load user data
    users = load_users()
    if username not in users:
        raise HTTPException(status_code=400, detail={
            "result": False,
            "error": "User not found"
        })
    
    user = users[username]
    
    return {
        "result": True,
        "data": {
            "fname": user['fname'],
            "lname": user['lname'],
            "password": user['password']
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Auth Server API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)