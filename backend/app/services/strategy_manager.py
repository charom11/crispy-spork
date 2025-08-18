from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.strategy import Strategy
from app.strategies.factory import StrategyFactory
from app.strategies.base import BaseStrategy, TradeSignal
import logging
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class StrategyManager:
    """Manages trading strategies lifecycle and execution"""
    
    def __init__(self):
        self.active_strategies: Dict[str, BaseStrategy] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.is_running = False
        
    async def start_strategy(self, db: Session, strategy_id: str, user_id: str) -> bool:
        """Start a trading strategy"""
        try:
            # Get strategy from database
            db_strategy = db.query(Strategy).filter(
                Strategy.id == strategy_id,
                Strategy.user_id == user_id
            ).first()
            
            if not db_strategy:
                logger.error(f"Strategy {strategy_id} not found for user {user_id}")
                return False
            
            if not db_strategy.is_active:
                logger.error(f"Strategy {strategy_id} is not active")
                return False
            
            # Create strategy instance
            strategy = StrategyFactory.create_strategy(
                db_strategy.type,
                db_strategy.config,
                user_id
            )
            
            if not strategy:
                logger.error(f"Failed to create strategy instance for {strategy_id}")
                return False
            
            # Start the strategy
            if strategy.start():
                self.active_strategies[strategy_id] = strategy
                logger.info(f"Strategy {strategy_id} started successfully")
                
                # Start background execution
                asyncio.create_task(self._execute_strategy(strategy_id))
                
                return True
            else:
                logger.error(f"Failed to start strategy {strategy_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting strategy {strategy_id}: {e}")
            return False
    
    async def stop_strategy(self, strategy_id: str, user_id: str) -> bool:
        """Stop a trading strategy"""
        try:
            if strategy_id not in self.active_strategies:
                logger.warning(f"Strategy {strategy_id} is not running")
                return True
            
            strategy = self.active_strategies[strategy_id]
            
            # Verify user ownership
            if strategy.user_id != user_id:
                logger.error(f"User {user_id} cannot stop strategy {strategy_id}")
                return False
            
            # Stop the strategy
            if strategy.stop():
                del self.active_strategies[strategy_id]
                logger.info(f"Strategy {strategy_id} stopped successfully")
                return True
            else:
                logger.error(f"Failed to stop strategy {strategy_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping strategy {strategy_id}: {e}")
            return False
    
    async def pause_strategy(self, strategy_id: str, user_id: str) -> bool:
        """Pause a trading strategy"""
        try:
            if strategy_id not in self.active_strategies:
                logger.warning(f"Strategy {strategy_id} is not running")
                return False
            
            strategy = self.active_strategies[strategy_id]
            
            # Verify user ownership
            if strategy.user_id != user_id:
                logger.error(f"User {user_id} cannot pause strategy {strategy_id}")
                return False
            
            # Pause the strategy
            if strategy.pause():
                logger.info(f"Strategy {strategy_id} paused successfully")
                return True
            else:
                logger.error(f"Failed to pause strategy {strategy_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error pausing strategy {strategy_id}: {e}")
            return False
    
    async def resume_strategy(self, strategy_id: str, user_id: str) -> bool:
        """Resume a paused trading strategy"""
        try:
            if strategy_id not in self.active_strategies:
                logger.warning(f"Strategy {strategy_id} is not running")
                return False
            
            strategy = self.active_strategies[strategy_id]
            
            # Verify user ownership
            if strategy.user_id != user_id:
                logger.error(f"User {user_id} cannot resume strategy {strategy_id}")
                return False
            
            # Resume the strategy
            if strategy.resume():
                logger.info(f"Strategy {strategy_id} resumed successfully")
                return True
            else:
                logger.error(f"Failed to resume strategy {strategy_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error resuming strategy {strategy_id}: {e}")
            return False
    
    async def update_strategy_config(self, db: Session, strategy_id: str, user_id: str, new_config: Dict[str, Any]) -> bool:
        """Update strategy configuration"""
        try:
            if strategy_id not in self.active_strategies:
                logger.warning(f"Strategy {strategy_id} is not running")
                return False
            
            strategy = self.active_strategies[strategy_id]
            
            # Verify user ownership
            if strategy.user_id != user_id:
                logger.error(f"User {user_id} cannot update strategy {strategy_id}")
                return False
            
            # Update configuration
            if strategy.update_config(new_config):
                # Update database
                db_strategy = db.query(Strategy).filter(
                    Strategy.id == strategy_id,
                    Strategy.user_id == user_id
                ).first()
                
                if db_strategy:
                    db_strategy.config = new_config
                    db_strategy.updated_at = datetime.utcnow()
                    db.commit()
                
                logger.info(f"Strategy {strategy_id} configuration updated successfully")
                return True
            else:
                logger.error(f"Failed to update strategy {strategy_id} configuration")
                return False
                
        except Exception as e:
            logger.error(f"Error updating strategy {strategy_id} configuration: {e}")
            return False
    
    async def get_strategy_status(self, strategy_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get strategy status"""
        try:
            if strategy_id not in self.active_strategies:
                return None
            
            strategy = self.active_strategies[strategy_id]
            
            # Verify user ownership
            if strategy.user_id != user_id:
                logger.error(f"User {user_id} cannot access strategy {strategy_id}")
                return None
            
            return strategy.get_status()
            
        except Exception as e:
            logger.error(f"Error getting strategy {strategy_id} status: {e}")
            return None
    
    async def get_all_strategies_status(self, user_id: str) -> List[Dict[str, Any]]:
        """Get status of all user's strategies"""
        try:
            statuses = []
            
            for strategy_id, strategy in self.active_strategies.items():
                if strategy.user_id == user_id:
                    status = strategy.get_status()
                    status['id'] = strategy_id
                    statuses.append(status)
            
            return statuses
            
        except Exception as e:
            logger.error(f"Error getting strategies status for user {user_id}: {e}")
            return []
    
    async def _execute_strategy(self, strategy_id: str):
        """Background execution loop for a strategy"""
        try:
            while strategy_id in self.active_strategies:
                strategy = self.active_strategies[strategy_id]
                
                if not strategy.is_running:
                    await asyncio.sleep(1)
                    continue
                
                # Get market data (mock data for now)
                market_data = self._get_mock_market_data()
                
                # Execute strategy
                signal = strategy.execute(market_data)
                
                if signal in [TradeSignal.BUY, TradeSignal.SELL]:
                    # Process trade signal
                    await self._process_trade_signal(strategy_id, signal, market_data)
                
                # Wait before next execution
                execution_interval = strategy.config.get('execution_interval', 60)  # seconds
                await asyncio.sleep(execution_interval)
                
        except Exception as e:
            logger.error(f"Error in strategy execution loop for {strategy_id}: {e}")
            if strategy_id in self.active_strategies:
                strategy = self.active_strategies[strategy_id]
                strategy.status = 'error'
    
    async def _process_trade_signal(self, strategy_id: str, signal: TradeSignal, market_data: Dict[str, Any]):
        """Process trade signal from strategy"""
        try:
            logger.info(f"Processing {signal.value} signal from strategy {strategy_id}")
            
            # Here you would:
            # 1. Calculate position size
            # 2. Check risk limits
            # 3. Place order with exchange
            # 4. Log trade in database
            # 5. Update strategy state
            
            # For now, just log the signal
            logger.info(f"Trade signal processed: {signal.value} for strategy {strategy_id}")
            
        except Exception as e:
            logger.error(f"Error processing trade signal for strategy {strategy_id}: {e}")
    
    def _get_mock_market_data(self) -> Dict[str, Any]:
        """Get mock market data for testing"""
        # In production, this would fetch real market data
        import random
        
        return {
            'price': 50000 + random.uniform(-1000, 1000),
            'volume': random.uniform(100, 1000),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def shutdown(self):
        """Shutdown strategy manager"""
        try:
            self.is_running = False
            
            # Stop all active strategies
            for strategy_id in list(self.active_strategies.keys()):
                strategy = self.active_strategies[strategy_id]
                strategy.stop()
            
            self.active_strategies.clear()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info("Strategy manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during strategy manager shutdown: {e}")

# Global strategy manager instance
strategy_manager = StrategyManager()