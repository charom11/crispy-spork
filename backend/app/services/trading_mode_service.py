from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import logging

from app.models.trading_mode import TradingMode
from app.models.trade import Trade
from app.schemas.trading_mode import TradingModeCreate, TradingModeUpdate
from app.core.logging import logger

class TradingModeService:
    """Service for managing trading modes (paper vs live)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_trading_mode(self, user_id: str) -> Optional[TradingMode]:
        """Get trading mode for a user"""
        return self.db.query(TradingMode).filter(
            TradingMode.user_id == user_id
        ).first()
    
    def create_trading_mode(self, user_id: str, mode_data: TradingModeCreate) -> TradingMode:
        """Create trading mode for a user"""
        try:
            # Check if user already has a trading mode
            existing_mode = self.get_trading_mode(user_id)
            if existing_mode:
                raise ValueError("User already has a trading mode configured")
            
            # Create new trading mode
            trading_mode = TradingMode(
                user_id=user_id,
                **mode_data.dict()
            )
            
            self.db.add(trading_mode)
            self.db.commit()
            self.db.refresh(trading_mode)
            
            logger.info(f"Created trading mode for user {user_id}", 
                       user_id=user_id, trading_mode=trading_mode.is_paper_trading)
            
            return trading_mode
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating trading mode: {e}", user_id=user_id)
            raise
    
    def update_trading_mode(self, user_id: str, mode_data: TradingModeUpdate) -> Optional[TradingMode]:
        """Update trading mode for a user"""
        try:
            trading_mode = self.get_trading_mode(user_id)
            if not trading_mode:
                return None
            
            # Update fields
            update_data = mode_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(trading_mode, field, value)
            
            trading_mode.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(trading_mode)
            
            logger.info(f"Updated trading mode for user {user_id}", 
                       user_id=user_id, trading_mode=trading_mode.is_paper_trading)
            
            return trading_mode
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating trading mode: {e}", user_id=user_id)
            raise
    
    def switch_to_paper_trading(self, user_id: str) -> bool:
        """Switch user to paper trading mode"""
        try:
            trading_mode = self.get_trading_mode(user_id)
            if not trading_mode:
                # Create default paper trading mode
                trading_mode = TradingMode.get_default_paper_mode(user_id)
                self.db.add(trading_mode)
            else:
                trading_mode.is_paper_trading = True
                trading_mode.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"User {user_id} switched to paper trading", user_id=user_id)
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error switching to paper trading: {e}", user_id=user_id)
            raise
    
    def switch_to_live_trading(self, user_id: str) -> Tuple[bool, str]:
        """Switch user to live trading mode with validation"""
        try:
            trading_mode = self.get_trading_mode(user_id)
            if not trading_mode:
                return False, "No trading mode configured"
            
            # Check if live trading is enabled
            if not trading_mode.live_trading_enabled:
                return False, "Live trading is not enabled for this account"
            
            # Additional safety checks
            if not self._can_switch_to_live(user_id):
                return False, "Account does not meet requirements for live trading"
            
            # Switch to live trading
            trading_mode.is_paper_trading = False
            trading_mode.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.warning(f"User {user_id} switched to live trading", 
                          user_id=user_id, severity="high")
            
            return True, "Successfully switched to live trading"
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error switching to live trading: {e}", user_id=user_id)
            raise
    
    def _can_switch_to_live(self, user_id: str) -> bool:
        """Check if user can switch to live trading"""
        # Add additional checks here:
        # - KYC verification
        # - Risk assessment
        # - Account age
        # - Trading history
        # - Compliance checks
        
        # For now, return True if live trading is enabled
        trading_mode = self.get_trading_mode(user_id)
        return trading_mode and trading_mode.live_trading_enabled
    
    def get_trading_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get trading statistics for the current period"""
        try:
            # Get current date range
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_week = start_of_day - timedelta(days=now.weekday())
            start_of_month = start_of_day.replace(day=1)
            
            # Get trades for different periods
            daily_trades = self.db.query(Trade).filter(
                and_(
                    Trade.user_id == user_id,
                    Trade.created_at >= start_of_day
                )
            ).count()
            
            weekly_trades = self.db.query(Trade).filter(
                and_(
                    Trade.user_id == user_id,
                    Trade.created_at >= start_of_week
                )
            ).count()
            
            monthly_trades = self.db.query(Trade).filter(
                and_(
                    Trade.user_id == user_id,
                    Trade.created_at >= start_of_month
                )
            ).count()
            
            # Calculate daily volume
            daily_volume = self.db.query(Trade).filter(
                and_(
                    Trade.user_id == user_id,
                    Trade.created_at >= start_of_day
                )
            ).with_entities(
                Trade.quantity * Trade.price
            ).all()
            
            daily_volume_sum = sum([float(vol[0]) for vol in daily_volume if vol[0]])
            
            return {
                'daily_trades': daily_trades,
                'weekly_trades': weekly_trades,
                'monthly_trades': monthly_trades,
                'daily_volume': daily_volume_sum,
                'current_period': {
                    'day_start': start_of_day.isoformat(),
                    'week_start': start_of_week.isoformat(),
                    'month_start': start_of_month.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting trading statistics: {e}", user_id=user_id)
            return {}
    
    def validate_trade_request(self, user_id: str, trade_value: float) -> Tuple[bool, str]:
        """Validate if a trade request is allowed"""
        try:
            trading_mode = self.get_trading_mode(user_id)
            if not trading_mode:
                return False, "No trading mode configured"
            
            # Get current trading statistics
            stats = self.get_trading_statistics(user_id)
            
            # Validate trade
            is_allowed, message = trading_mode.validate_trade(
                trade_value=trade_value,
                daily_trades=stats.get('daily_trades', 0),
                daily_volume=stats.get('daily_volume', 0)
            )
            
            if is_allowed:
                logger.info(f"Trade validation passed for user {user_id}", 
                           user_id=user_id, trade_value=trade_value, 
                           trading_mode=trading_mode.is_paper_trading)
            else:
                logger.warning(f"Trade validation failed for user {user_id}: {message}", 
                              user_id=user_id, trade_value=trade_value, 
                              trading_mode=trading_mode.is_paper_trading)
            
            return is_allowed, message
            
        except Exception as e:
            logger.error(f"Error validating trade request: {e}", user_id=user_id)
            return False, f"Validation error: {str(e)}"
    
    def get_trading_mode_summary(self, user_id: str) -> Dict[str, Any]:
        """Get trading mode summary for dashboard"""
        try:
            trading_mode = self.get_trading_mode(user_id)
            if not trading_mode:
                return {
                    'mode': 'not_configured',
                    'description': 'Trading mode not configured',
                    'balance': '0',
                    'can_switch': False
                }
            
            stats = self.get_trading_statistics(user_id)
            
            return {
                'mode': 'paper' if trading_mode.is_paper_trading else 'live',
                'description': trading_mode.get_trading_mode_description(),
                'balance': trading_mode.get_effective_balance(),
                'can_switch': trading_mode.can_switch_to_live(),
                'daily_trades': stats.get('daily_trades', 0),
                'daily_volume': stats.get('daily_volume', 0),
                'max_daily_trades': trading_mode.max_daily_trades,
                'max_daily_volume': trading_mode.max_daily_volume,
                'require_confirmation': trading_mode.require_confirmation,
                'stop_loss_percent': trading_mode.get_effective_stop_loss(),
                'take_profit_percent': trading_mode.get_effective_take_profit()
            }
            
        except Exception as e:
            logger.error(f"Error getting trading mode summary: {e}", user_id=user_id)
            return {
                'mode': 'error',
                'description': 'Error loading trading mode',
                'balance': '0',
                'can_switch': False
            }
    
    def reset_paper_trading_balance(self, user_id: str, new_balance: str = "100000") -> bool:
        """Reset paper trading balance (for testing)"""
        try:
            trading_mode = self.get_trading_mode(user_id)
            if not trading_mode:
                return False
            
            if not trading_mode.is_paper_trading:
                return False
            
            trading_mode.paper_trading_balance = new_balance
            trading_mode.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Reset paper trading balance for user {user_id} to ${new_balance}", 
                       user_id=user_id, new_balance=new_balance)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting paper trading balance: {e}", user_id=user_id)
            raise