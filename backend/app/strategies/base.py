from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    GRID = "grid"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"

class StrategyStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class TradeSignal(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, config: Dict[str, Any], user_id: str):
        self.config = config
        self.user_id = user_id
        self.status = StrategyStatus.STOPPED
        self.last_execution = None
        self.total_trades = 0
        self.total_pnl = 0.0
        self.is_running = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the strategy with configuration"""
        pass
    
    @abstractmethod
    def execute(self, market_data: Dict[str, Any]) -> Optional[TradeSignal]:
        """Execute strategy logic and return trade signal"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: TradeSignal, market_data: Dict[str, Any]) -> float:
        """Calculate position size for the trade"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate strategy configuration"""
        pass
    
    def start(self) -> bool:
        """Start the strategy"""
        try:
            if self.validate_config() and self.initialize():
                self.status = StrategyStatus.ACTIVE
                self.is_running = True
                logger.info(f"Strategy {self.__class__.__name__} started for user {self.user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error starting strategy: {e}")
            self.status = StrategyStatus.ERROR
            return False
    
    def stop(self) -> bool:
        """Stop the strategy"""
        try:
            self.is_running = False
            self.status = StrategyStatus.STOPPED
            logger.info(f"Strategy {self.__class__.__name__} stopped for user {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error stopping strategy: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause the strategy"""
        try:
            self.is_running = False
            self.status = StrategyStatus.PAUSED
            logger.info(f"Strategy {self.__class__.__name__} paused for user {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error pausing strategy: {e}")
            return False
    
    def resume(self) -> bool:
        """Resume the strategy"""
        try:
            if self.status == StrategyStatus.PAUSED:
                self.is_running = True
                self.status = StrategyStatus.ACTIVE
                logger.info(f"Strategy {self.__class__.__name__} resumed for user {self.user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming strategy: {e}")
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update strategy configuration"""
        try:
            old_config = self.config.copy()
            self.config.update(new_config)
            
            if self.validate_config():
                logger.info(f"Strategy config updated for user {self.user_id}")
                return True
            else:
                # Revert if validation fails
                self.config = old_config
                logger.error(f"Strategy config validation failed for user {self.user_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating strategy config: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current strategy status"""
        return {
            "status": self.status.value,
            "is_running": self.is_running,
            "last_execution": self.last_execution,
            "total_trades": self.total_trades,
            "total_pnl": self.total_pnl,
            "config": self.config
        }
    
    def log_trade(self, signal: TradeSignal, quantity: float, price: float, pnl: float = 0.0):
        """Log a trade execution"""
        self.total_trades += 1
        self.total_pnl += pnl
        self.last_execution = datetime.utcnow()
        logger.info(f"Trade executed: {signal.value} {quantity} @ {price}, PnL: {pnl}")