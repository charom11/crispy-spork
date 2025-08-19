from typing import Dict, Any, Optional, List
from .base import BaseStrategy, TradeSignal, StrategyStatus
import logging
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)

class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion Strategy - Trades based on price deviations from moving averages"""
    
    def __init__(self, config: Dict[str, Any], user_id: str):
        super().__init__(config, user_id)
        self.price_history = deque(maxlen=200)  # Store last 200 prices
        self.sma_short = deque(maxlen=50)      # Short-term SMA
        self.sma_long = deque(maxlen=200)      # Long-term SMA
        self.current_position = 0.0
        self.last_signal = None
        
    def initialize(self) -> bool:
        """Initialize strategy parameters"""
        try:
            # Clear any existing data
            self.price_history.clear()
            self.sma_short.clear()
            self.sma_long.clear()
            
            logger.info("Mean reversion strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing mean reversion strategy: {e}")
            return False
    
    def execute(self, market_data: Dict[str, Any]) -> Optional[TradeSignal]:
        """Execute mean reversion strategy logic"""
        try:
            if not self.is_running:
                return None
            
            current_price = market_data.get('price', 0.0)
            if current_price <= 0:
                return None
            
            # Add current price to history
            self.price_history.append(current_price)
            
            # Calculate moving averages
            short_period = self.config.get('short_period', 20)
            long_period = self.config.get('long_period', 50)
            
            if len(self.price_history) < long_period:
                return None  # Not enough data yet
            
            # Calculate short-term SMA
            if len(self.price_history) >= short_period:
                short_sma = np.mean(list(self.price_history)[-short_period:])
                self.sma_short.append(short_sma)
            
            # Calculate long-term SMA
            long_sma = np.mean(list(self.price_history)[-long_period:])
            self.sma_long.append(long_sma)
            
            # Get deviation thresholds
            buy_threshold = self.config.get('buy_threshold', -0.02)  # -2%
            sell_threshold = self.config.get('sell_threshold', 0.02)  # +2%
            
            # Calculate price deviation from long-term SMA
            deviation = (current_price - long_sma) / long_sma
            
            # Determine trade signal
            signal = None
            
            if deviation <= buy_threshold and self.current_position < self.config.get('max_position', 1000.0):
                # Price is significantly below SMA, potential buy signal
                if self.last_signal != TradeSignal.BUY:
                    signal = TradeSignal.BUY
                    self.last_signal = TradeSignal.BUY
                    
            elif deviation >= sell_threshold and self.current_position > -self.config.get('max_position', 1000.0):
                # Price is significantly above SMA, potential sell signal
                if self.last_signal != TradeSignal.SELL:
                    signal = TradeSignal.SELL
                    self.last_signal = TradeSignal.SELL
                    
            else:
                # Price is within normal range, hold
                signal = TradeSignal.HOLD
                self.last_signal = None
            
            # Log trade if signal is generated
            if signal in [TradeSignal.BUY, TradeSignal.SELL]:
                quantity = self.calculate_position_size(signal, market_data)
                self.log_trade(signal, quantity, current_price)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error executing mean reversion strategy: {e}")
            return None
    
    def calculate_position_size(self, signal: TradeSignal, market_data: Dict[str, Any]) -> float:
        """Calculate position size for mean reversion trades"""
        try:
            current_price = market_data.get('price', 1.0)
            base_amount = self.config.get('base_amount', 100.0)
            
            # Calculate base quantity
            quantity = base_amount / current_price
            
            # Apply position sizing based on deviation
            deviation = self.config.get('buy_threshold', -0.02)
            if abs(deviation) > 0.05:  # Large deviation
                quantity *= 1.5  # Increase position size
            elif abs(deviation) < 0.01:  # Small deviation
                quantity *= 0.5  # Decrease position size
            
            # Apply risk management
            max_position = self.config.get('max_position', 1000.0)
            if signal == TradeSignal.BUY:
                if self.current_position + quantity > max_position:
                    quantity = max_position - self.current_position
            else:  # SELL
                if self.current_position - quantity < -max_position:
                    quantity = self.current_position + max_position
            
            # Ensure positive quantity
            quantity = max(0, quantity)
            
            # Update current position
            if signal == TradeSignal.BUY:
                self.current_position += quantity
            elif signal == TradeSignal.SELL:
                self.current_position -= quantity
            
            return quantity
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def validate_config(self) -> bool:
        """Validate mean reversion strategy configuration"""
        try:
            required_fields = ['short_period', 'long_period', 'buy_threshold', 'sell_threshold', 'base_amount']
            
            for field in required_fields:
                if field not in self.config:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            short_period = self.config['short_period']
            long_period = self.config['long_period']
            buy_threshold = self.config['buy_threshold']
            sell_threshold = self.config['sell_threshold']
            base_amount = self.config['base_amount']
            
            if short_period <= 0 or long_period <= 0:
                logger.error("Periods must be positive")
                return False
            
            if short_period >= long_period:
                logger.error("Short period must be less than long period")
                return False
            
            if buy_threshold >= 0 or sell_threshold <= 0:
                logger.error("Buy threshold must be negative, sell threshold must be positive")
                return False
            
            if abs(buy_threshold) > 0.5 or abs(sell_threshold) > 0.5:
                logger.error("Thresholds must be between -50% and +50%")
                return False
            
            if base_amount <= 0:
                logger.error("Base amount must be positive")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating mean reversion strategy config: {e}")
            return False
    
    def get_strategy_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics"""
        try:
            if len(self.price_history) < 2:
                return {}
            
            prices = list(self.price_history)
            returns = []
            
            for i in range(1, len(prices)):
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
            
            if returns:
                volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
                sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            else:
                volatility = 0
                sharpe_ratio = 0
            
            return {
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'price_history_length': len(self.price_history),
                'current_deviation': self._calculate_current_deviation() if self.price_history else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating strategy metrics: {e}")
            return {}
    
    def _calculate_current_deviation(self) -> float:
        """Calculate current price deviation from long-term SMA"""
        try:
            if not self.price_history or not self.sma_long:
                return 0.0
            
            current_price = self.price_history[-1]
            long_sma = self.sma_long[-1]
            
            return (current_price - long_sma) / long_sma
            
        except Exception as e:
            logger.error(f"Error calculating current deviation: {e}")
            return 0.0
