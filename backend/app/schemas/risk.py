from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    LOSS_LIMIT = "loss_limit"
    POSITION_LIMIT = "position_limit"
    VOLATILITY = "volatility"
    CORRELATION = "correlation"
    LEVERAGE = "leverage"
    TRADING_HOURS = "trading_hours"
    PORTFOLIO_RISK = "portfolio_risk"
    SYSTEM = "system"

class RiskProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True
    
    # Position Limits
    max_position_size: float = Field(10000.0, gt=0, description="Maximum position size in USD")
    max_positions: int = Field(10, gt=0, le=100, description="Maximum number of open positions")
    max_leverage: float = Field(1.0, gt=0, le=100, description="Maximum leverage allowed")
    
    # Loss Limits
    daily_loss_limit: float = Field(1000.0, gt=0, description="Daily loss limit in USD")
    weekly_loss_limit: float = Field(5000.0, gt=0, description="Weekly loss limit in USD")
    monthly_loss_limit: float = Field(20000.0, gt=0, description="Monthly loss limit in USD")
    total_loss_limit: float = Field(50000.0, gt=0, description="Total loss limit in USD")
    
    # Stop Loss & Take Profit
    default_stop_loss_percent: float = Field(5.0, gt=0, le=50, description="Default stop loss percentage")
    default_take_profit_percent: float = Field(10.0, gt=0, le=100, description="Default take profit percentage")
    trailing_stop_enabled: bool = False
    trailing_stop_percent: float = Field(2.0, gt=0, le=20, description="Trailing stop percentage")
    
    # Risk Per Trade
    max_risk_per_trade: float = Field(2.0, gt=0, le=10, description="Maximum risk per trade as % of portfolio")
    max_portfolio_risk: float = Field(10.0, gt=0, le=50, description="Maximum portfolio risk percentage")
    
    # Volatility Controls
    max_volatility_threshold: float = Field(50.0, gt=0, le=200, description="Maximum allowed volatility")
    correlation_limit: float = Field(0.7, gt=0, le=1, description="Maximum correlation between positions")
    
    # Time-based Controls
    trading_hours_start: str = Field("09:00", regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    trading_hours_end: str = Field("17:00", regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    weekend_trading: bool = False
    
    # Additional Configuration
    config: Dict[str, Any] = {}

    @validator('weekly_loss_limit')
    def validate_weekly_loss_limit(cls, v, values):
        if 'daily_loss_limit' in values and v < values['daily_loss_limit'] * 5:
            raise ValueError('Weekly loss limit should be at least 5x daily loss limit')
        return v

    @validator('monthly_loss_limit')
    def validate_monthly_loss_limit(cls, v, values):
        if 'weekly_loss_limit' in values and v < values['weekly_loss_limit'] * 3:
            raise ValueError('Monthly loss limit should be at least 3x weekly loss limit')
        return v

    @validator('total_loss_limit')
    def validate_total_loss_limit(cls, v, values):
        if 'monthly_loss_limit' in values and v < values['monthly_loss_limit'] * 2:
            raise ValueError('Total loss limit should be at least 2x monthly loss limit')
        return v

    @validator('trading_hours_end')
    def validate_trading_hours(cls, v, values):
        if 'trading_hours_start' in values:
            start = values['trading_hours_start']
            if v <= start:
                raise ValueError('Trading end time must be after start time')
        return v

class RiskProfileCreate(RiskProfileBase):
    pass

class RiskProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    
    # Position Limits
    max_position_size: Optional[float] = Field(None, gt=0)
    max_positions: Optional[int] = Field(None, gt=0, le=100)
    max_leverage: Optional[float] = Field(None, gt=0, le=100)
    
    # Loss Limits
    daily_loss_limit: Optional[float] = Field(None, gt=0)
    weekly_loss_limit: Optional[float] = Field(None, gt=0)
    monthly_loss_limit: Optional[float] = Field(None, gt=0)
    total_loss_limit: Optional[float] = Field(None, gt=0)
    
    # Stop Loss & Take Profit
    default_stop_loss_percent: Optional[float] = Field(None, gt=0, le=50)
    default_take_profit_percent: Optional[float] = Field(None, gt=0, le=100)
    trailing_stop_enabled: Optional[bool] = None
    trailing_stop_percent: Optional[float] = Field(None, gt=0, le=20)
    
    # Risk Per Trade
    max_risk_per_trade: Optional[float] = Field(None, gt=0, le=10)
    max_portfolio_risk: Optional[float] = Field(None, gt=0, le=50)
    
    # Volatility Controls
    max_volatility_threshold: Optional[float] = Field(None, gt=0, le=200)
    correlation_limit: Optional[float] = Field(None, gt=0, le=1)
    
    # Time-based Controls
    trading_hours_start: Optional[str] = Field(None, regex=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    trading_hours_end: Optional[str] = Field(None, regex=r"^([0-1]?[0-3]):[0-5][0-9]$")
    weekend_trading: Optional[bool] = None
    
    # Additional Configuration
    config: Optional[Dict[str, Any]] = None

class RiskProfile(RiskProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RiskAlertBase(BaseModel):
    alert_type: AlertType
    severity: RiskSeverity = RiskSeverity.MEDIUM
    message: str = Field(..., min_length=1, max_length=500)
    details: Dict[str, Any] = {}

class RiskAlertCreate(RiskAlertBase):
    risk_profile_id: str
    user_id: str

class RiskAlertUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_acknowledged: Optional[bool] = None
    message: Optional[str] = Field(None, min_length=1, max_length=500)
    details: Optional[Dict[str, Any]] = None

class RiskAlert(RiskAlertBase):
    id: str
    risk_profile_id: str
    user_id: str
    is_active: bool
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RiskMetrics(BaseModel):
    """Real-time risk metrics for monitoring"""
    current_portfolio_value: float
    daily_pnl: float
    daily_pnl_percent: float
    weekly_pnl: float
    weekly_pnl_percent: float
    monthly_pnl: float
    monthly_pnl_percent: float
    total_pnl: float
    total_pnl_percent: float
    
    # Risk Indicators
    current_risk_level: str  # low, medium, high, critical
    portfolio_risk_percent: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    volatility: float
    
    # Position Information
    open_positions: int
    total_position_value: float
    largest_position: float
    position_concentration: float  # % in largest position
    
    # Limits Status
    daily_loss_limit_remaining: float
    weekly_loss_limit_remaining: float
    monthly_loss_limit_remaining: float
    total_loss_limit_remaining: float
    
    # Alerts
    active_alerts_count: int
    critical_alerts_count: int

class RiskCheckRequest(BaseModel):
    """Request for risk check before trade execution"""
    symbol: str
    side: str  # buy, sell
    quantity: float
    price: Optional[float] = None
    order_type: str  # market, limit, stop_loss, take_profit
    strategy_id: Optional[str] = None

class RiskCheckResponse(BaseModel):
    """Response from risk check"""
    is_allowed: bool
    risk_score: float  # 0-100, lower is better
    warnings: List[str] = []
    errors: List[str] = []
    suggested_quantity: Optional[float] = None
    suggested_price: Optional[float] = None
    risk_factors: Dict[str, Any] = {}

class RiskProfileSummary(BaseModel):
    """Summary of risk profile for dashboard"""
    id: str
    name: str
    is_active: bool
    risk_level: str
    daily_loss_limit: float
    daily_loss_limit_remaining: float
    weekly_loss_limit: float
    weekly_loss_limit_remaining: float
    monthly_loss_limit: float
    monthly_loss_limit_remaining: float
    active_alerts_count: int
    last_updated: datetime