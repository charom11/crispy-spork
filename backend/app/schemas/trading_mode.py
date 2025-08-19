from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class TradingModeBase(BaseModel):
    """Base trading mode configuration"""
    is_paper_trading: bool = True
    paper_trading_balance: str = Field("100000", description="Paper trading balance in USD")
    
    # Live trading settings
    live_trading_enabled: bool = False
    live_trading_balance: Optional[str] = Field(None, description="Live trading balance in USD")
    max_live_position_size: str = Field("10000", description="Maximum position size in live mode")
    
    # Safety controls
    require_confirmation: bool = True
    max_daily_trades: int = Field(50, ge=1, le=1000, description="Maximum trades per day")
    max_daily_volume: str = Field("100000", description="Maximum daily volume in USD")
    
    # Risk controls for live trading
    live_stop_loss_percent: str = Field("3.0", description="Stop loss percentage for live trading")
    live_take_profit_percent: str = Field("6.0", description="Take profit percentage for live trading")
    
    # Additional configuration
    config: Dict[str, Any] = {}

    @validator('paper_trading_balance', 'live_trading_balance', 'max_live_position_size', 'max_daily_volume')
    def validate_currency_amount(cls, v):
        if v is None:
            return v
        
        try:
            # Remove commas and convert to float
            amount = float(v.replace(',', ''))
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            return v
        except ValueError:
            raise ValueError("Invalid currency amount format")
    
    @validator('live_stop_loss_percent', 'live_take_profit_percent')
    def validate_percentage(cls, v):
        try:
            percent = float(v)
            if percent <= 0 or percent > 100:
                raise ValueError("Percentage must be between 0 and 100")
            return v
        except ValueError:
            raise ValueError("Invalid percentage format")

class TradingModeCreate(TradingModeBase):
    """Schema for creating trading mode"""
    pass

class TradingModeUpdate(BaseModel):
    """Schema for updating trading mode"""
    is_paper_trading: Optional[bool] = None
    paper_trading_balance: Optional[str] = None
    live_trading_enabled: Optional[bool] = None
    live_trading_balance: Optional[str] = None
    max_live_position_size: Optional[str] = None
    require_confirmation: Optional[bool] = None
    max_daily_trades: Optional[int] = Field(None, ge=1, le=1000)
    max_daily_volume: Optional[str] = None
    live_stop_loss_percent: Optional[str] = None
    live_take_profit_percent: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class TradingMode(TradingModeBase):
    """Schema for trading mode response"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TradingModeSummary(BaseModel):
    """Schema for trading mode summary"""
    mode: str  # 'paper', 'live', 'not_configured', 'error'
    description: str
    balance: str
    can_switch: bool
    daily_trades: int
    daily_volume: float
    max_daily_trades: int
    max_daily_volume: str
    require_confirmation: bool
    stop_loss_percent: str
    take_profit_percent: str

class TradingModeSwitch(BaseModel):
    """Schema for switching trading mode"""
    target_mode: str = Field(..., description="Target mode: 'paper' or 'live'")
    confirm_live_trading: bool = Field(False, description="Confirmation for live trading")

class TradingModeSwitchResponse(BaseModel):
    """Schema for trading mode switch response"""
    success: bool
    message: str
    new_mode: str
    previous_mode: str
    timestamp: datetime

class TradingStatistics(BaseModel):
    """Schema for trading statistics"""
    daily_trades: int
    weekly_trades: int
    monthly_trades: int
    daily_volume: float
    current_period: Dict[str, str]

class TradingModeValidation(BaseModel):
    """Schema for trade validation"""
    is_allowed: bool
    message: str
    trading_mode: str
    daily_trades_remaining: int
    daily_volume_remaining: float
    max_position_size: str