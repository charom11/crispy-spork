from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class ExchangeConfigBase(BaseModel):
    exchange_type: str = Field(..., regex="^(binance|bybit)$")
    name: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=1, max_length=255)
    api_secret: str = Field(..., min_length=1, max_length=255)
    testnet: bool = Field(default=True)
    config: Dict[str, Any] = Field(default_factory=dict)

class ExchangeConfigCreate(ExchangeConfigBase):
    pass

class ExchangeConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, min_length=1, max_length=255)
    api_secret: Optional[str] = Field(None, min_length=1, max_length=255)
    testnet: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ExchangeConfigInDB(ExchangeConfigBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ExchangeConfig(ExchangeConfigInDB):
    pass

class ExchangeConfigResponse(BaseModel):
    id: str
    user_id: str
    exchange_type: str
    name: str
    api_key: str  # Masked
    api_secret: str  # Masked
    testnet: bool
    is_active: bool
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ExchangeConnection(BaseModel):
    exchange_id: str
    exchange_type: str
    name: str
    is_connected: bool
    testnet: bool
    health_status: bool

class PriceData(BaseModel):
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    exchange: str

class OrderBook(BaseModel):
    symbol: str
    bids: List[List[float]]
    asks: List[List[float]]
    last_update_id: Optional[str] = None

class OrderCreate(BaseModel):
    symbol: str = Field(..., min_length=1)
    side: str = Field(..., regex="^(buy|sell)$")
    order_type: str = Field(..., regex="^(market|limit|stop_loss|take_profit)$")
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)

class OrderResponse(BaseModel):
    id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float]
    status: str
    filled_quantity: float
    remaining_quantity: float
    created_at: datetime
    updated_at: datetime
    exchange_order_id: Optional[str] = None

class TradeResponse(BaseModel):
    id: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float
    fee_currency: str
    timestamp: datetime
    exchange_trade_id: Optional[str] = None

class BalanceResponse(BaseModel):
    asset: str
    free: float
    locked: float
    total: float

class ExchangeStatus(BaseModel):
    exchange_id: str
    exchange_type: str
    is_connected: bool
    health_status: bool
    last_health_check: Optional[datetime] = None
    connection_info: Dict[str, Any]

class ExchangeList(BaseModel):
    exchanges: List[ExchangeConfigResponse]
    total: int
