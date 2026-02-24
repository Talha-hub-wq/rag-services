from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from supabase import create_client, Client
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    # Password Hashing
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    # JWT Token Creation
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access"):
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            print(payload)
            
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if email is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            
            return {"email": email, "user_id": user_id}
        
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    # User Operations
    def create_user(self, email: str, password: str, full_name: Optional[str] = None):
        """Create a new user"""
        # Check if user already exists
        existing_user = self.supabase.table("users").select("*").eq("email", email).execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = self.hash_password(password)
        
        # Insert user
        user_data = {
            "email": email,
            "password_hash": hashed_password,
            "full_name": full_name
        }
        
        result = self.supabase.table("users").insert(user_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        return result.data[0]
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user with email and password"""
        # Get user from database
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user = result.data[0]
        
        # Verify password
        if not self.verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        return user
    
    def get_user_by_id(self, user_id: str):
        """Get user by ID"""
        result = self.supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return result.data[0]
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        result = self.supabase.table("users").select("*").eq("email", email).execute()
        
        if not result.data:
            return None
        
        return result.data[0]
    
    # Password Reset Operations
    def create_password_reset_token(self, email: str) -> str:
        """Create a password reset token"""
        user = self.get_user_by_email(email)
        
        if not user:
            # Don't reveal if email exists or not for security
            return None
        
        # Generate random token
        token = secrets.token_urlsafe(32)
        
        # Set expiration (1 hour from now)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Insert token into database
        token_data = {
            "user_id": user["id"],
            "token": token,
            "expires_at": expires_at.isoformat()
        }
        
        self.supabase.table("password_reset_tokens").insert(token_data).execute()
        
        return token
    
    def verify_reset_token(self, token: str):
        """Verify password reset token"""
        result = self.supabase.table("password_reset_tokens")\
            .select("*")\
            .eq("token", token)\
            .eq("used", False)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        token_data = result.data[0]
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_data["expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow() > expires_at.replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        return token_data
    
    def reset_password(self, token: str, new_password: str):
        """Reset user password with token"""
        # Verify token
        token_data = self.verify_reset_token(token)
        
        # Hash new password
        hashed_password = self.hash_password(new_password)
        
        # Update user password
        self.supabase.table("users")\
            .update({"password_hash": hashed_password})\
            .eq("id", token_data["user_id"])\
            .execute()
        
        # Mark token as used
        self.supabase.table("password_reset_tokens")\
            .update({"used": True})\
            .eq("id", token_data["id"])\
            .execute()
        
        return True
    
    def change_password(self, user_id: str, old_password: str, new_password: str):
        """Change user password"""
        user = self.get_user_by_id(user_id)
        
        # Verify old password
        if not self.verify_password(old_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        # Hash new password
        hashed_password = self.hash_password(new_password)
        
        # Update password
        self.supabase.table("users")\
            .update({"password_hash": hashed_password})\
            .eq("id", user_id)\
            .execute()
        
        return True
    
    # Email Service
    @staticmethod
    def send_reset_email(email: str, token: str):
        """Send password reset email"""
        try:
            # Create reset link
            reset_link = f"http://localhost:8080/index.html?reset={token}"
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Password Reset Request"
            message["From"] = settings.email_from
            message["To"] = email
            
            # HTML content
            html = f"""
            <html>
                <body>
                    <h2>Password Reset Request</h2>
                    <p>You have requested to reset your password.</p>
                    <p>Click the link below to reset your password:</p>
                    <a href="{reset_link}">Reset Password</a>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </body>
            </html>
            """
            
            html_part = MIMEText(html, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)
            
            return True
        
        except Exception as e:
            print(f"Error sending email: {e}")
            return False