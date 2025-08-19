from typing import Dict, Any, Optional, List
from .base import BaseStrategy, TradeSignal, StrategyStatus
import logging
import math

logger = logging.getLogger(__name__)

class GridStrategy(BaseStrategy):
    """Grid Trading Strategy - Places buy/sell orders at predefined price levels"""
    
    def __init__(self, config: Dict[str, Any], user_id: str):
        super().__init__(config, user_id)
        self.grid_levels = []
        self.current_position = 0.0
        self.base_price = 0.0
        self.grid_spacing = 0.0
        
    def initialize(self) -> bool:
        """Initialize grid levels and parameters"""
        try:
            self.base_price = self.config.get('base_price', 0.0)
            self.grid_spacing = self.config.get('grid_spacing', 0.0)
            num_levels = self.config.get('num_levels', 10)
            
            if self.base_price <= 0 or self.grid_spacing <= 0 or num_levels <= 0:
                logger.error("Invalid grid configuration parameters")
                return False
            
            # Create grid levels above and below base price
            self.grid_levels = []
            for i in range(-num_levels, num_levels + 1):
                level_price = self.base_price + (i * self.grid_spacing)
                if level_price > 0:
                    self.grid_levels.append({
                        'price': level_price,
                        'type': 'buy' if i < 0 else 'sell',
                        'filled': False,
                        'order_id': None
                    })
            
            # Sort grid levels by price
            self.grid_levels.sort(key=lambda x: x['price'])
            
            logger.info(f"Grid strategy initialized with {len(self.grid_levels)} levels")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing grid strategy: {e}")
            return False
    
    def execute(self, market_data: Dict[str, Any]) -> Optional[TradeSignal]:
        """Execute grid strategy logic"""
        try:
            if not self.is_running:
                return None
            
            current_price = market_data.get('price', 0.0)
            if current_price <= 0:
                return None
            
            # Find the closest grid level
            closest_level = None
            min_distance = float('inf')
            
            for level in self.grid_levels:
                if not level['filled']:
                    distance = abs(current_price - level['price'])
                    if distance < min_distance:
                        min_distance = distance
                        closest_level = level
            
            if closest_level and min_distance <= self.config.get('trigger_threshold', self.grid_spacing * 0.1):
                # Determine trade signal based on grid level type
                if closest_level['type'] == 'buy' and current_price <= closest_level['price']:
                    signal = TradeSignal.BUY
                elif closest_level['type'] == 'sell' and current_price >= closest_level['price']:
                    signal = TradeSignal.SELL
                else:
                    return None
                
                # Mark level as filled
                closest_level['filled'] = True
                
                # Log the trade
                quantity = self.calculate_position_size(signal, market_data)
                self.log_trade(signal, quantity, current_price)
                
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error executing grid strategy: {e}")
            return None
    
    def calculate_position_size(self, signal: TradeSignal, market_data: Dict[str, Any]) -> float:
        """Calculate position size for grid trades"""
        try:
            base_amount = self.config.get('base_amount', 100.0)  # Base amount per trade
            current_price = market_data.get('price', 1.0)
            
            # Calculate quantity based on base amount
            quantity = base_amount / current_price
            
            # Apply position sizing rules
            max_position = self.config.get('max_position', 1000.0)
            if self.current_position + quantity > max_position:
                quantity = max_position - self.current_position
            
            # Update current position
            if signal == TradeSignal.BUY:
                self.current_position += quantity
            else:
                self.current_position -= quantity
            
            return quantity
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def validate_config(self) -> bool:
        """Validate grid strategy configuration"""
        try:
            required_fields = ['base_price', 'grid_spacing', 'num_levels', 'base_amount']
            
            for field in required_fields:
                if field not in self.config:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            base_price = self.config['base_price']
            grid_spacing = self.config['grid_spacing']
            num_levels = self.config['num_levels']
            base_amount = self.config['base_amount']
            
            if base_price <= 0:
                logger.error("Base price must be positive")
                return False
            
            if grid_spacing <= 0:
                logger.error("Grid spacing must be positive")
                return False
            
            if num_levels <= 0 or num_levels > 100:
                logger.error("Number of levels must be between 1 and 100")
                return False
            
            if base_amount <= 0:
                logger.error("Base amount must be positive")
                return False
            
            # Check if grid levels would be reasonable
            min_price = base_price - (num_levels * grid_spacing)
            if min_price <= 0:
                logger.error("Grid levels would include negative prices")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating grid strategy config: {e}")
            return False
    
    def get_grid_status(self) -> Dict[str, Any]:
        """Get detailed grid status"""
        status = self.get_status()
        status.update({
            'grid_levels': self.grid_levels,
            'current_position': self.current_position,
            'base_price': self.base_price,
            'grid_spacing': self.grid_spacing,
            'filled_levels': len([level for level in self.grid_levels if level['filled']]),
            'total_levels': len(self.grid_levels)
        })
        return status
    
    def reset_grid(self) -> bool:
        """Reset all grid levels to unfilled state"""
        try:
            for level in self.grid_levels:
                level['filled'] = False
                level['order_id'] = None
            
            self.current_position = 0.0
            logger.info("Grid levels reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting grid: {e}")
            return False
