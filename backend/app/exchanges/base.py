from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ExchangeType(Enum):
    BINANCE = "binance"
    BYBIT = "bybit"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"

@dataclass
class Order:
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    status: OrderStatus
    filled_quantity: float
    remaining_quantity: float
    created_at: datetime
    updated_at: datetime
    exchange_order_id: Optional[str] = None

@dataclass
class Trade:
    id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    fee: float
    fee_currency: str
    timestamp: datetime
    exchange_trade_id: Optional[str] = None

@dataclass
class PriceData:
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    exchange: ExchangeType

@dataclass
class Balance:
    asset: str
    free: float
    locked: float
    total: float

class BaseExchange(ABC):
    """Base class for exchange integrations"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.is_connected = False
        self.ws_connections = {}
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to exchange"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from exchange"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        pass
    
    @abstractmethod
    async def get_balances(self) -> List[Balance]:
        """Get account balances"""
        pass
    
    @abstractmethod
    async def get_symbols(self) -> List[str]:
        """Get available trading symbols"""
        pass
    
    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for symbol"""
        pass
    
    @abstractmethod
    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get order book for symbol"""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: OrderSide, order_type: OrderType, 
                         quantity: float, price: Optional[float] = None) -> Optional[Order]:
        """Place a new order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order"""
        pass
    
    @abstractmethod
    async def get_order(self, symbol: str, order_id: str) -> Optional[Order]:
        """Get order details"""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get open orders"""
        pass
    
    @abstractmethod
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Trade]:
        """Get recent trades"""
        pass
    
    @abstractmethod
    async def subscribe_price_feed(self, symbol: str, callback) -> bool:
        """Subscribe to real-time price feed"""
        pass
    
    @abstractmethod
    async def unsubscribe_price_feed(self, symbol: str) -> bool:
        """Unsubscribe from price feed"""
        pass
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate trading symbol format"""
        # Basic validation - can be overridden by specific exchanges
        if not symbol or len(symbol) < 3:
            return False
        return True
    
    def validate_quantity(self, quantity: float) -> bool:
        """Validate order quantity"""
        if quantity <= 0:
            return False
        return True
    
    def validate_price(self, price: float) -> bool:
        """Validate order price"""
        if price <= 0:
            return False
        return True
    
    async def health_check(self) -> bool:
        """Check exchange connection health"""
        try:
            await self.get_account_info()
            return True
        except Exception as e:
            logger.error(f"Exchange health check failed: {e}")
            return False
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information"""
        return {
            "exchange_type": self.__class__.__name__,
            "testnet": self.testnet,
            "is_connected": self.is_connected,
            "api_key": self.api_key[:8] + "..." if self.api_key else None
        }