from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid

class ExchangeConfig(Base):
    __tablename__ = "exchange_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    exchange_type = Column(String(50), nullable=False)  # binance, bybit
    name = Column(String(100), nullable=False)
    api_key = Column(String(255), nullable=False)
    api_secret = Column(String(255), nullable=False)
    testnet = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    config = Column(JSONB, default={})  # Additional configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="exchange_configs")
    
    def __repr__(self):
        return f"<ExchangeConfig(id={self.id}, exchange_type='{self.exchange_type}', name='{self.name}', user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert exchange config to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'exchange_type': self.exchange_type,
            'name': self.name,
            'api_key': self.api_key[:8] + "..." if self.api_key else None,  # Mask API key
            'api_secret': "***" if self.api_secret else None,  # Mask API secret
            'testnet': self.testnet,
            'is_active': self.is_active,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_full_config(self):
        """Get full configuration including API keys (for internal use)"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'exchange_type': self.exchange_type,
            'name': self.name,
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'testnet': self.testnet,
            'is_active': self.is_active,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
