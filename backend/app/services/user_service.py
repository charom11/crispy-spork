from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.security import create_access_token
from datetime import timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class UserService:
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> Optional[User]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_create.email) | (User.username == user_create.username)
            ).first()
            
            if existing_user:
                if existing_user.email == user_create.email:
                    raise ValueError("Email already registered")
                else:
                    raise ValueError("Username already taken")
            
            # Create new user
            hashed_password = get_password_hash(user_create.password)
            db_user = User(
                email=user_create.email,
                username=user_create.username,
                hashed_password=hashed_password
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User created successfully: {user_create.email}")
            return db_user
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error creating user: {e}")
            raise ValueError("User creation failed - database constraint violation")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return None
            
            if not verify_password(password, user.hashed_password):
                return None
            
            if not user.is_active:
                return None
            
            logger.info(f"User authenticated successfully: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def create_user_token(user: User, expires_delta: Optional[timedelta] = None) -> dict:
        """Create access token for user"""
        try:
            access_token_expires = expires_delta or timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": int(access_token_expires.total_seconds())
            }
            
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def update_user(db: Session, user: User, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            update_data = user_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User updated successfully: {user.email}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {e}")
            raise
    
    @staticmethod
    def deactivate_user(db: Session, user: User) -> bool:
        """Deactivate a user"""
        try:
            user.is_active = False
            db.commit()
            db.refresh(user)
            
            logger.info(f"User deactivated: {user.email}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating user: {e}")
            return False