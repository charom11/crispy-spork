from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid

class RiskProfile(Base):
    __tablename__ = "risk_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Position Limits
    max_position_size = Column(Float, default=10000.0)  # Maximum position size in USD
    max_positions = Column(Integer, default=10)  # Maximum number of open positions
    max_leverage = Column(Float, default=1.0)  # Maximum leverage allowed
    
    # Loss Limits
    daily_loss_limit = Column(Float, default=1000.0)  # Daily loss limit in USD
    weekly_loss_limit = Column(Float, default=5000.0)  # Weekly loss limit in USD
    monthly_loss_limit = Column(Float, default=20000.0)  # Monthly loss limit in USD
    total_loss_limit = Column(Float, default=50000.0)  # Total loss limit in USD
    
    # Stop Loss & Take Profit
    default_stop_loss_percent = Column(Float, default=5.0)  # Default stop loss percentage
    default_take_profit_percent = Column(Float, default=10.0)  # Default take profit percentage
    trailing_stop_enabled = Column(Boolean, default=False)  # Enable trailing stop loss
    trailing_stop_percent = Column(Float, default=2.0)  # Trailing stop percentage
    
    # Risk Per Trade
    max_risk_per_trade = Column(Float, default=2.0)  # Maximum risk per trade as % of portfolio
    max_portfolio_risk = Column(Float, default=10.0)  # Maximum portfolio risk percentage
    
    # Volatility Controls
    max_volatility_threshold = Column(Float, default=50.0)  # Maximum allowed volatility
    correlation_limit = Column(Float, default=0.7)  # Maximum correlation between positions
    
    # Time-based Controls
    trading_hours_start = Column(String(5), default="09:00")  # Trading start time
    trading_hours_end = Column(String(5), default="17:00")  # Trading end time
    weekend_trading = Column(Boolean, default=False)  # Allow weekend trading
    
    # Additional Configuration
    config = Column(JSONB, default={})  # Additional risk parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="risk_profiles")
    risk_alerts = relationship("RiskAlert", back_populates="risk_profile")
    
    def __repr__(self):
        return f"<RiskProfile(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert risk profile to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'is_active': self.is_active,
            'max_position_size': self.max_position_size,
            'max_positions': self.max_positions,
            'max_leverage': self.max_leverage,
            'daily_loss_limit': self.daily_loss_limit,
            'weekly_loss_limit': self.weekly_loss_limit,
            'monthly_loss_limit': self.monthly_loss_limit,
            'total_loss_limit': self.total_loss_limit,
            'default_stop_loss_percent': self.default_stop_loss_percent,
            'default_take_profit_percent': self.default_take_profit_percent,
            'trailing_stop_enabled': self.trailing_stop_enabled,
            'trailing_stop_percent': self.trailing_stop_percent,
            'max_risk_per_trade': self.max_risk_per_trade,
            'max_portfolio_risk': self.max_portfolio_risk,
            'max_volatility_threshold': self.max_volatility_threshold,
            'correlation_limit': self.correlation_limit,
            'trading_hours_start': self.trading_hours_start,
            'trading_hours_end': self.trading_hours_end,
            'weekend_trading': self.weekend_trading,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RiskAlert(Base):
    __tablename__ = "risk_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_profile_id = Column(UUID(as_uuid=True), ForeignKey('risk_profiles.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Alert Details
    alert_type = Column(String(50), nullable=False)  # loss_limit, position_limit, volatility, etc.
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    message = Column(Text, nullable=False)
    details = Column(JSONB, default={})  # Additional alert details
    
    # Status
    is_active = Column(Boolean, default=True)  # Whether alert is still active
    is_acknowledged = Column(Boolean, default=False)  # Whether user acknowledged
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    risk_profile = relationship("RiskProfile", back_populates="risk_alerts")
    user = relationship("User", foreign_keys=[user_id])
    acknowledged_user = relationship("User", foreign_keys=[acknowledged_by])
    
    def __repr__(self):
        return f"<RiskAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
    
    def to_dict(self):
        """Convert risk alert to dictionary"""
        return {
            'id': str(self.id),
            'risk_profile_id': str(self.risk_profile_id),
            'user_id': str(self.user_id),
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'details': self.details,
            'is_active': self.is_active,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': str(self.acknowledged_by) if self.acknowledged_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }