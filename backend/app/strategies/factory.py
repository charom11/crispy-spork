from typing import Dict, Any, Optional, List
from .base import BaseStrategy, StrategyType
from .grid_strategy import GridStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .momentum_strategy import MomentumStrategy
import logging

logger = logging.getLogger(__name__)

class StrategyFactory:
    """Factory class for creating trading strategies"""
    
    @staticmethod
    def create_strategy(strategy_type: str, config: Dict[str, Any], user_id: str) -> Optional[BaseStrategy]:
        """Create a strategy instance based on type"""
        try:
            strategy_type_enum = StrategyType(strategy_type.lower())
            
            if strategy_type_enum == StrategyType.GRID:
                return GridStrategy(config, user_id)
            elif strategy_type_enum == StrategyType.MEAN_REVERSION:
                return MeanReversionStrategy(config, user_id)
            elif strategy_type_enum == StrategyType.MOMENTUM:
                return MomentumStrategy(config, user_id)
            else:
                logger.error(f"Unknown strategy type: {strategy_type}")
                return None
                
        except ValueError as e:
            logger.error(f"Invalid strategy type: {strategy_type}")
            return None
        except Exception as e:
            logger.error(f"Error creating strategy: {e}")
            return None
    
    @staticmethod
    def get_default_config(strategy_type: str) -> Dict[str, Any]:
        """Get default configuration for a strategy type"""
        try:
            strategy_type_enum = StrategyType(strategy_type.lower())
            
            if strategy_type_enum == StrategyType.GRID:
                return {
                    "base_price": 50000.0,
                    "grid_spacing": 1000.0,
                    "num_levels": 10,
                    "base_amount": 100.0,
                    "max_position": 1000.0,
                    "trigger_threshold": 100.0
                }
            elif strategy_type_enum == StrategyType.MEAN_REVERSION:
                return {
                    "short_period": 20,
                    "long_period": 50,
                    "buy_threshold": -0.02,
                    "sell_threshold": 0.02,
                    "base_amount": 100.0,
                    "max_position": 1000.0
                }
            elif strategy_type_enum == StrategyType.MOMENTUM:
                return {
                    "rsi_period": 14,
                    "macd_fast": 12,
                    "macd_slow": 26,
                    "macd_signal": 9,
                    "rsi_oversold": 30,
                    "rsi_overbought": 70,
                    "base_amount": 100.0,
                    "max_position": 1000.0
                }
            else:
                return {}
                
        except ValueError:
            logger.error(f"Invalid strategy type for default config: {strategy_type}")
            return {}
        except Exception as e:
            logger.error(f"Error getting default config: {e}")
            return {}
    
    @staticmethod
    def get_strategy_info(strategy_type: str) -> Dict[str, Any]:
        """Get information about a strategy type"""
        try:
            strategy_type_enum = StrategyType(strategy_type.lower())
            
            if strategy_type_enum == StrategyType.GRID:
                return {
                    "name": "Grid Trading",
                    "description": "Places buy/sell orders at predefined price levels for automated trading",
                    "type": "grid",
                    "parameters": [
                        {"name": "base_price", "type": "float", "description": "Center price for grid levels"},
                        {"name": "grid_spacing", "type": "float", "description": "Price difference between grid levels"},
                        {"name": "num_levels", "type": "int", "description": "Number of levels above and below base price"},
                        {"name": "base_amount", "type": "float", "description": "Base amount per trade"},
                        {"name": "max_position", "type": "float", "description": "Maximum position size"},
                        {"name": "trigger_threshold", "type": "float", "description": "Price threshold to trigger trades"}
                    ]
                }
            elif strategy_type_enum == StrategyType.MEAN_REVERSION:
                return {
                    "name": "Mean Reversion",
                    "description": "Trades based on price deviations from moving averages",
                    "type": "mean_reversion",
                    "parameters": [
                        {"name": "short_period", "type": "int", "description": "Short-term moving average period"},
                        {"name": "long_period", "type": "int", "description": "Long-term moving average period"},
                        {"name": "buy_threshold", "type": "float", "description": "Buy signal threshold (negative)"},
                        {"name": "sell_threshold", "type": "float", "description": "Sell signal threshold (positive)"},
                        {"name": "base_amount", "type": "float", "description": "Base amount per trade"},
                        {"name": "max_position", "type": "float", "description": "Maximum position size"}
                    ]
                }
            elif strategy_type_enum == StrategyType.MOMENTUM:
                return {
                    "name": "Momentum",
                    "description": "Follows trending price movements using RSI and MACD indicators",
                    "type": "momentum",
                    "parameters": [
                        {"name": "rsi_period", "type": "int", "description": "RSI calculation period"},
                        {"name": "macd_fast", "type": "int", "description": "MACD fast EMA period"},
                        {"name": "macd_slow", "type": "int", "description": "MACD slow EMA period"},
                        {"name": "macd_signal", "type": "int", "description": "MACD signal line period"},
                        {"name": "rsi_oversold", "type": "int", "description": "RSI oversold threshold"},
                        {"name": "rsi_overbought", "type": "int", "description": "RSI overbought threshold"},
                        {"name": "base_amount", "type": "float", "description": "Base amount per trade"},
                        {"name": "max_position", "type": "float", "description": "Maximum position size"}
                    ]
                }
            else:
                return {}
                
        except ValueError:
            logger.error(f"Invalid strategy type for info: {strategy_type}")
            return {}
        except Exception as e:
            logger.error(f"Error getting strategy info: {e}")
            return {}
    
    @staticmethod
    def get_available_strategies() -> List[Dict[str, Any]]:
        """Get list of all available strategies"""
        strategies = []
        
        for strategy_type in StrategyType:
            info = StrategyFactory.get_strategy_info(strategy_type.value)
            if info:
                strategies.append(info)
        
        return strategies
