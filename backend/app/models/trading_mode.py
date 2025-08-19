from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid

class TradingMode(Base):
    __tablename__ = "trading_modes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)
    
    # Trading mode settings
    is_paper_trading = Column(Boolean, default=True, nullable=False)
    paper_trading_balance = Column(String(20), default="100000")  # Default $100k paper balance
    
    # Live trading settings
    live_trading_enabled = Column(Boolean, default=False, nullable=False)
    live_trading_balance = Column(String(20), nullable=True)
    max_live_position_size = Column(String(20), default="10000")  # Max $10k per position in live mode
    
    # Safety controls
    require_confirmation = Column(Boolean, default=True, nullable=False)  # Require confirmation for live trades
    max_daily_trades = Column(Integer, default=50, nullable=False)  # Maximum trades per day
    max_daily_volume = Column(String(20), default="100000", nullable=False)  # Maximum daily volume
    
    # Risk controls for live trading
    live_stop_loss_percent = Column(String(10), default="3.0", nullable=False)  # Tighter stop loss for live
    live_take_profit_percent = Column(String(10), default="6.0", nullable=False)  # Conservative take profit
    
    # Configuration
    config = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trading_mode")
    
    def __repr__(self):
        return f"<TradingMode(user_id={self.user_id}, paper_trading={self.is_paper_trading})>"
    
    def to_dict(self):
        """Convert trading mode to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'is_paper_trading': self.is_paper_trading,
            'paper_trading_balance': self.paper_trading_balance,
            'live_trading_enabled': self.live_trading_enabled,
            'live_trading_balance': self.live_trading_balance,
            'max_live_position_size': self.max_live_position_size,
            'require_confirmation': self.require_confirmation,
            'max_daily_trades': self.max_daily_trades,
            'max_daily_volume': self.max_daily_volume,
            'live_stop_loss_percent': self.live_stop_loss_percent,
            'live_take_profit_percent': self.live_take_profit_percent,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_effective_balance(self) -> str:
        """Get the effective balance based on trading mode"""
        if self.is_paper_trading:
            return self.paper_trading_balance
        else:
            return self.live_trading_balance or "0"
    
    def get_effective_stop_loss(self) -> str:
        """Get the effective stop loss percentage"""
        if self.is_paper_trading:
            return "5.0"  # Default paper trading stop loss
        else:
            return self.live_stop_loss_percent
    
    def get_effective_take_profit(self) -> str:
        """Get the effective take profit percentage"""
        if self.is_paper_trading:
            return "10.0"  # Default paper trading take profit
        else:
            return self.live_take_profit_percent
    
    def can_switch_to_live(self) -> bool:
        """Check if user can switch to live trading"""
        # Add additional checks here (e.g., KYC verification, risk assessment)
        return self.live_trading_enabled
    
    def get_trading_mode_description(self) -> str:
        """Get human-readable trading mode description"""
        if self.is_paper_trading:
            return f"Paper Trading (${self.paper_trading_balance} balance)"
        else:
            return f"Live Trading (${self.live_trading_balance or '0'} balance)"
    
    def validate_trade(self, trade_value: float, daily_trades: int, daily_volume: float) -> tuple[bool, str]:
        """Validate if a trade is allowed"""
        if self.is_paper_trading:
            # Paper trading has fewer restrictions
            paper_balance = float(self.paper_trading_balance.replace(',', ''))
            if trade_value > paper_balance * 0.1:  # Max 10% of paper balance per trade
                return False, "Trade value exceeds 10% of paper trading balance"
            return True, "Trade allowed in paper mode"
        
        else:
            # Live trading has stricter controls
            if not self.live_trading_enabled:
                return False, "Live trading is not enabled"
            
            if daily_trades >= self.max_daily_trades:
                return False, f"Daily trade limit reached ({self.max_daily_trades})"
            
            max_volume = float(self.max_daily_volume.replace(',', ''))
            if daily_volume + trade_value > max_volume:
                return False, f"Daily volume limit would be exceeded"
            
            max_position = float(self.max_live_position_size.replace(',', ''))
            if trade_value > max_position:
                return False, f"Trade value exceeds maximum position size (${max_position})"
            
            return True, "Trade allowed in live mode"
    
    @classmethod
    def get_default_paper_mode(cls, user_id: str):
        """Get default paper trading mode for a user"""
        return cls(
            user_id=user_id,
            is_paper_trading=True,
            paper_trading_balance="100000",
            live_trading_enabled=False,
            require_confirmation=True,
            max_daily_trades=50,
            max_daily_volume="100000",
            live_stop_loss_percent="3.0",
            live_take_profit_percent="6.0"
        )
    
    @classmethod
    def get_default_live_mode(cls, user_id: str):
        """Get default live trading mode for a user"""
        return cls(
            user_id=user_id,
            is_paper_trading=False,
            paper_trading_balance="100000",
            live_trading_enabled=True,
            live_trading_balance="0",
            max_live_position_size="10000",
            require_confirmation=True,
            max_daily_trades=20,  # Fewer trades in live mode
            max_daily_volume="50000",  # Lower volume in live mode
            live_stop_loss_percent="2.0",  # Tighter stop loss
            live_take_profit_percent="4.0"  # Conservative take profit
        )