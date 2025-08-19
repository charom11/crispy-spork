from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # grid, mean_reversion, momentum
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=False)
    config = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', type='{self.type}', user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert strategy to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'user_id': str(self.user_id),
            'is_active': self.is_active,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
