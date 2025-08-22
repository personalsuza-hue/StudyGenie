"""
Authentication module for Google OAuth integration
"""
import os
import jwt
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

# Models
class User(BaseModel):
    id: str
    email: str
    name: str
    picture: str
    created_at: datetime
    last_login: datetime

class TokenData(BaseModel):
    user_id: str
    email: str
    exp: datetime

# Configuration
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

security = HTTPBearer(auto_error=False)

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
    async def verify_google_token(self, token: str) -> Dict[str, Any]:
        """Verify Google ID token and return user info"""
        try:
            # For development, we'll use Google's tokeninfo endpoint
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=401, detail="Invalid Google token")
                
                token_data = response.json()
                
                # Verify the token is for our client
                if token_data.get('aud') != self.google_client_id:
                    raise HTTPException(status_code=401, detail="Token not for this application")
                
                return {
                    'id': token_data.get('sub'),
                    'email': token_data.get('email'),
                    'name': token_data.get('name'),
                    'picture': token_data.get('picture'),
                    'email_verified': token_data.get('email_verified', False)
                }
                
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    
    async def get_or_create_user(self, google_user_data: Dict[str, Any]) -> User:
        """Get existing user or create new user from Google data"""
        email = google_user_data['email']
        
        # Check if user already exists
        existing_user = await self.db.users.find_one({"email": email})
        
        current_time = datetime.now(timezone.utc)
        
        if existing_user:
            # Update last login
            await self.db.users.update_one(
                {"email": email},
                {"$set": {"last_login": current_time}}
            )
            return User(**existing_user)
        else:
            # Create new user
            new_user_data = {
                "id": google_user_data['id'],
                "email": email,
                "name": google_user_data['name'],
                "picture": google_user_data['picture'],
                "created_at": current_time,
                "last_login": current_time
            }
            
            await self.db.users.insert_one(new_user_data)
            return User(**new_user_data)
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expires_at = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "exp": expires_at
        }
        
        return jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> TokenData:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            user_id = payload.get("user_id")
            email = payload.get("email")
            
            if not user_id or not email:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            
            return TokenData(
                user_id=user_id,
                email=email,
                exp=datetime.fromtimestamp(payload.get("exp"))
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def get_current_user(self, token_data: TokenData) -> Optional[User]:
        """Get current user from token data"""
        user = await self.db.users.find_one({"id": token_data.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return User(**user)

# Dependency to get current user
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current authenticated user"""
    
    # Get database from request app state
    db = request.app.state.db
    auth_service = AuthService(db)
    
    token = None
    
    # Try to get token from Authorization header
    if credentials:
        token = credentials.credentials
    
    # Try to get token from cookie as fallback
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Verify token and get user
    token_data = auth_service.verify_token(token)
    user = await auth_service.get_current_user(token_data)
    
    return user

# Optional authentication (returns None if not authenticated)
async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None