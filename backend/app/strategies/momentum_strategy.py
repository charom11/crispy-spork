from typing import Dict, Any, Optional, List
from .base import BaseStrategy, TradeSignal, StrategyStatus
import logging
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)

class MomentumStrategy(BaseStrategy):
    """Momentum Strategy - Follows trending price movements using technical indicators"""
    
    def __init__(self, config: Dict[str, Any], user_id: str):
        super().__init__(config, user_id)
        self.price_history = deque(maxlen=100)
        self.volume_history = deque(maxlen=100)
        self.rsi_values = deque(maxlen=50)
        self.macd_values = deque(maxlen=50)
        self.current_position = 0.0
        self.trend_direction = None  # 'up', 'down', or None
        
    def initialize(self) -> bool:
        """Initialize strategy parameters"""
        try:
            # Clear any existing data
            self.price_history.clear()
            self.volume_history.clear()
            self.rsi_values.clear()
            self.macd_values.clear()
            self.trend_direction = None
            
            logger.info("Momentum strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing momentum strategy: {e}")
            return False
    
    def execute(self, market_data: Dict[str, Any]) -> Optional[TradeSignal]:
        """Execute momentum strategy logic"""
        try:
            if not self.is_running:
                return None
            
            current_price = market_data.get('price', 0.0)
            current_volume = market_data.get('volume', 0.0)
            
            if current_price <= 0:
                return None
            
            # Add current data to history
            self.price_history.append(current_price)
            self.volume_history.append(current_volume)
            
            # Need minimum data for calculations
            min_periods = max(
                self.config.get('rsi_period', 14),
                self.config.get('macd_fast', 12),
                self.config.get('macd_slow', 26)
            )
            
            if len(self.price_history) < min_periods:
                return None
            
            # Calculate technical indicators
            rsi = self._calculate_rsi()
            macd, macd_signal = self._calculate_macd()
            
            if rsi is not None:
                self.rsi_values.append(rsi)
            if macd is not None:
                self.macd_values.append(macd)
            
            # Determine trend direction
            self._update_trend_direction()
            
            # Generate trade signals
            signal = self._generate_signal(rsi, macd, macd_signal)
            
            # Log trade if signal is generated
            if signal in [TradeSignal.BUY, TradeSignal.SELL]:
                quantity = self.calculate_position_size(signal, market_data)
                self.log_trade(signal, quantity, current_price)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error executing momentum strategy: {e}")
            return None
    
    def _calculate_rsi(self) -> Optional[float]:
        """Calculate Relative Strength Index"""
        try:
            period = self.config.get('rsi_period', 14)
            if len(self.price_history) < period + 1:
                return None
            
            prices = list(self.price_history)
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if len(gains) < period:
                return None
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    def _calculate_macd(self) -> tuple[Optional[float], Optional[float]]:
        """Calculate MACD and signal line"""
        try:
            fast_period = self.config.get('macd_fast', 12)
            slow_period = self.config.get('macd_slow', 26)
            signal_period = self.config.get('macd_signal', 9)
            
            if len(self.price_history) < slow_period:
                return None, None
            
            prices = list(self.price_history)
            
            # Calculate EMAs
            fast_ema = self._calculate_ema(prices, fast_period)
            slow_ema = self._calculate_ema(prices, slow_period)
            
            if fast_ema is None or slow_ema is None:
                return None, None
            
            # Calculate MACD line
            macd_line = fast_ema - slow_ema
            
            # Calculate signal line (EMA of MACD)
            if len(self.macd_values) >= signal_period:
                macd_values = list(self.macd_values) + [macd_line]
                signal_line = self._calculate_ema(macd_values, signal_period)
            else:
                signal_line = None
            
            return macd_line, signal_line
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None, None
    
    def _calculate_ema(self, values: List[float], period: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        try:
            if len(values) < period:
                return None
            
            alpha = 2 / (period + 1)
            ema = values[0]
            
            for value in values[1:]:
                ema = alpha * value + (1 - alpha) * ema
            
            return ema
            
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return None
    
    def _update_trend_direction(self):
        """Update trend direction based on price movement"""
        try:
            if len(self.price_history) < 20:
                return
            
            recent_prices = list(self.price_history)[-20:]
            slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
            
            if slope > 0.001:  # Positive slope threshold
                self.trend_direction = 'up'
            elif slope < -0.001:  # Negative slope threshold
                self.trend_direction = 'down'
            else:
                self.trend_direction = None
                
        except Exception as e:
            logger.error(f"Error updating trend direction: {e}")
    
    def _generate_signal(self, rsi: Optional[float], macd: Optional[float], macd_signal: Optional[float]) -> TradeSignal:
        """Generate trade signal based on technical indicators"""
        try:
            if rsi is None or macd is None:
                return TradeSignal.HOLD
            
            # RSI thresholds
            rsi_oversold = self.config.get('rsi_oversold', 30)
            rsi_overbought = self.config.get('rsi_overbought', 70)
            
            # MACD signal
            macd_bullish = macd > macd_signal if macd_signal is not None else False
            macd_bearish = macd < macd_signal if macd_signal is not None else False
            
            # Generate signals based on momentum and trend
            if (rsi < rsi_oversold and macd_bullish and 
                self.trend_direction == 'up' and 
                self.current_position < self.config.get('max_position', 1000.0)):
                return TradeSignal.BUY
                
            elif (rsi > rsi_overbought and macd_bearish and 
                  self.trend_direction == 'down' and 
                  self.current_position > -self.config.get('max_position', 1000.0)):
                return TradeSignal.SELL
            
            return TradeSignal.HOLD
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return TradeSignal.HOLD
    
    def calculate_position_size(self, signal: TradeSignal, market_data: Dict[str, Any]) -> float:
        """Calculate position size for momentum trades"""
        try:
            current_price = market_data.get('price', 1.0)
            base_amount = self.config.get('base_amount', 100.0)
            
            # Calculate base quantity
            quantity = base_amount / current_price
            
            # Adjust position size based on momentum strength
            if len(self.rsi_values) > 0:
                rsi = self.rsi_values[-1]
                if rsi < 20 or rsi > 80:  # Extreme RSI values
                    quantity *= 1.5  # Increase position size
                elif 40 < rsi < 60:  # Neutral RSI
                    quantity *= 0.7  # Decrease position size
            
            # Apply trend-based adjustments
            if self.trend_direction == 'up' and signal == TradeSignal.BUY:
                quantity *= 1.2  # Increase size for trend-following
            elif self.trend_direction == 'down' and signal == TradeSignal.SELL:
                quantity *= 1.2
            
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
        """Validate momentum strategy configuration"""
        try:
            required_fields = ['rsi_period', 'macd_fast', 'macd_slow', 'macd_signal', 
                             'rsi_oversold', 'rsi_overbought', 'base_amount']
            
            for field in required_fields:
                if field not in self.config:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            rsi_period = self.config['rsi_period']
            macd_fast = self.config['macd_fast']
            macd_slow = self.config['macd_slow']
            macd_signal = self.config['macd_signal']
            rsi_oversold = self.config['rsi_oversold']
            rsi_overbought = self.config['rsi_overbought']
            base_amount = self.config['base_amount']
            
            if rsi_period <= 0 or macd_fast <= 0 or macd_slow <= 0 or macd_signal <= 0:
                logger.error("All periods must be positive")
                return False
            
            if macd_fast >= macd_slow:
                logger.error("MACD fast period must be less than slow period")
                return False
            
            if rsi_oversold >= rsi_overbought:
                logger.error("RSI oversold must be less than overbought")
                return False
            
            if rsi_oversold < 0 or rsi_overbought > 100:
                logger.error("RSI values must be between 0 and 100")
                return False
            
            if base_amount <= 0:
                logger.error("Base amount must be positive")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating momentum strategy config: {e}")
            return False
    
    def get_strategy_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics"""
        try:
            metrics = {}
            
            if self.rsi_values:
                metrics['current_rsi'] = self.rsi_values[-1]
                metrics['rsi_trend'] = 'bullish' if self.rsi_values[-1] > 50 else 'bearish'
            
            if self.macd_values:
                metrics['current_macd'] = self.macd_values[-1]
            
            metrics['trend_direction'] = self.trend_direction
            metrics['price_history_length'] = len(self.price_history)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating strategy metrics: {e}")
            return {}
