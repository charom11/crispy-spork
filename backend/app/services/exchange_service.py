from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.exchange import ExchangeConfig
from app.schemas.exchange import (
    ExchangeConfigCreate, ExchangeConfigUpdate, ExchangeConfigResponse,
    OrderCreate, OrderResponse, TradeResponse, BalanceResponse,
    PriceData, OrderBook, ExchangeStatus
)
from app.exchanges.factory import exchange_factory
from app.exchanges.base import OrderSide, OrderType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExchangeService:
    """Service class for exchange operations"""
    
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
    
    async def get_user_exchanges(self) -> List[ExchangeConfigResponse]:
        """Get all exchange configurations for a user"""
        try:
            exchanges = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.user_id == self.user_id
            ).all()
            
            return [exchange.to_dict() for exchange in exchanges]
            
        except Exception as e:
            logger.error(f"Error getting user exchanges: {e}")
            raise
    
    async def get_exchange(self, exchange_id: str) -> Optional[ExchangeConfigResponse]:
        """Get a specific exchange configuration"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if exchange:
                return exchange.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting exchange {exchange_id}: {e}")
            raise
    
    async def create_exchange(self, exchange_create: ExchangeConfigCreate) -> Optional[ExchangeConfigResponse]:
        """Create a new exchange configuration"""
        try:
            # Create database record
            db_exchange = ExchangeConfig(
                user_id=self.user_id,
                exchange_type=exchange_create.exchange_type,
                name=exchange_create.name,
                api_key=exchange_create.api_key,
                api_secret=exchange_create.api_secret,
                testnet=exchange_create.testnet,
                config=exchange_create.config
            )
            
            self.db.add(db_exchange)
            self.db.commit()
            self.db.refresh(db_exchange)
            
            # Create exchange instance
            exchange = await exchange_factory.create_exchange(
                exchange_create.exchange_type,
                exchange_create.api_key,
                exchange_create.api_secret,
                exchange_create.testnet
            )
            
            if exchange:
                logger.info(f"Exchange {exchange_create.name} created successfully")
                return db_exchange.to_dict()
            else:
                # Rollback if exchange creation failed
                self.db.rollback()
                logger.error(f"Failed to create exchange instance for {exchange_create.name}")
                return None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating exchange: {e}")
            raise
    
    async def update_exchange(self, exchange_id: str, 
                            exchange_update: ExchangeConfigUpdate) -> Optional[ExchangeConfigResponse]:
        """Update an exchange configuration"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Update fields
            update_data = exchange_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                setattr(exchange, field, value)
            
            exchange.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(exchange)
            
            # Update exchange instance if API keys changed
            if 'api_key' in update_data or 'api_secret' in update_data:
                # Remove old instance
                old_exchange_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
                await exchange_factory.remove_exchange(old_exchange_id)
                
                # Create new instance
                new_exchange = await exchange_factory.create_exchange(
                    exchange.exchange_type,
                    exchange.api_key,
                    exchange.api_secret,
                    exchange.testnet
                )
                
                if not new_exchange:
                    logger.warning(f"Failed to recreate exchange instance for {exchange.name}")
            
            logger.info(f"Exchange {exchange.name} updated successfully")
            return exchange.to_dict()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating exchange {exchange_id}: {e}")
            raise
    
    async def delete_exchange(self, exchange_id: str) -> bool:
        """Delete an exchange configuration"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return False
            
            # Remove exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            await exchange_factory.remove_exchange(exchange_instance_id)
            
            # Delete database record
            self.db.delete(exchange)
            self.db.commit()
            
            logger.info(f"Exchange {exchange.name} deleted successfully")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting exchange {exchange_id}: {e}")
            raise
    
    async def get_exchange_status(self, exchange_id: str) -> Optional[ExchangeStatus]:
        """Get exchange connection status"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return ExchangeStatus(
                    exchange_id=exchange_id,
                    exchange_type=exchange.exchange_type,
                    is_connected=False,
                    health_status=False,
                    last_health_check=datetime.utcnow(),
                    connection_info={}
                )
            
            # Check health
            health_status = await exchange_instance.health_check()
            
            return ExchangeStatus(
                exchange_id=exchange_id,
                exchange_type=exchange.exchange_type,
                is_connected=exchange_instance.is_connected,
                health_status=health_status,
                last_health_check=datetime.utcnow(),
                connection_info=exchange_instance.get_exchange_info()
            )
            
        except Exception as e:
            logger.error(f"Error getting exchange status {exchange_id}: {e}")
            raise
    
    async def get_balances(self, exchange_id: str) -> Optional[List[BalanceResponse]]:
        """Get account balances for an exchange"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return None
            
            balances = await exchange_instance.get_balances()
            
            return [
                BalanceResponse(
                    asset=balance.asset,
                    free=balance.free,
                    locked=balance.locked,
                    total=balance.total
                )
                for balance in balances
            ]
            
        except Exception as e:
            logger.error(f"Error getting balances for {exchange_id}: {e}")
            raise
    
    async def get_symbols(self, exchange_id: str) -> Optional[List[str]]:
        """Get available trading symbols for an exchange"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return None
            
            return await exchange_instance.get_symbols()
            
        except Exception as e:
            logger.error(f"Error getting symbols for {exchange_id}: {e}")
            raise
    
    async def get_price(self, exchange_id: str, symbol: str) -> Optional[PriceData]:
        """Get current price for a symbol"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return None
            
            price_data = await exchange_instance.get_price(symbol)
            
            if price_data:
                return PriceData(
                    symbol=price_data.symbol,
                    price=price_data.price,
                    volume=price_data.volume,
                    timestamp=price_data.timestamp,
                    exchange=price_data.exchange.value
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol} on {exchange_id}: {e}")
            raise
    
    async def get_order_book(self, exchange_id: str, symbol: str, limit: int = 20) -> Optional[OrderBook]:
        """Get order book for a symbol"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return None
            
            order_book_data = await exchange_instance.get_order_book(symbol, limit)
            
            if order_book_data:
                return OrderBook(
                    symbol=order_book_data['symbol'],
                    bids=order_book_data['bids'],
                    asks=order_book_data['asks'],
                    last_update_id=order_book_data.get('lastUpdateId')
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting order book for {symbol} on {exchange_id}: {e}")
            raise
    
    async def place_order(self, exchange_id: str, order_create: OrderCreate) -> Optional[OrderResponse]:
        """Place a new order"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return None
            
            # Convert to exchange types
            side = OrderSide(order_create.side)
            order_type = OrderType(order_create.order_type)
            
            # Place order
            order = await exchange_instance.place_order(
                order_create.symbol,
                side,
                order_type,
                order_create.quantity,
                order_create.price
            )
            
            if order:
                return OrderResponse(
                    id=order.id,
                    symbol=order.symbol,
                    side=order.side.value,
                    order_type=order.order_type.value,
                    quantity=order.quantity,
                    price=order.price,
                    status=order.status.value,
                    filled_quantity=order.filled_quantity,
                    remaining_quantity=order.remaining_quantity,
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                    exchange_order_id=order.exchange_order_id
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error placing order on {exchange_id}: {e}")
            raise
    
    async def get_open_orders(self, exchange_id: str, symbol: Optional[str] = None) -> Optional[List[OrderResponse]]:
        """Get open orders for an exchange"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return None
            
            orders = await exchange_instance.get_open_orders(symbol)
            
            return [
                OrderResponse(
                    id=order.id,
                    symbol=order.symbol,
                    side=order.side.value,
                    order_type=order.order_type.value,
                    quantity=order.quantity,
                    price=order.price,
                    status=order.status.value,
                    filled_quantity=order.filled_quantity,
                    remaining_quantity=order.remaining_quantity,
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                    exchange_order_id=order.exchange_order_id
                )
                for order in orders
            ]
            
        except Exception as e:
            logger.error(f"Error getting orders for {exchange_id}: {e}")
            raise
    
    async def cancel_order(self, exchange_id: str, symbol: str, order_id: str) -> bool:
        """Cancel an order"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return False
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return False
            
            return await exchange_instance.cancel_order(symbol, order_id)
            
        except Exception as e:
            logger.error(f"Error cancelling order {order_id} on {exchange_id}: {e}")
            raise
    
    async def get_trades(self, exchange_id: str, symbol: str, limit: int = 100) -> Optional[List[TradeResponse]]:
        """Get recent trades for an exchange"""
        try:
            exchange = self.db.query(ExchangeConfig).filter(
                ExchangeConfig.id == exchange_id,
                ExchangeConfig.user_id == self.user_id
            ).first()
            
            if not exchange:
                return None
            
            # Get exchange instance
            exchange_instance_id = f"{exchange.exchange_type}_{exchange.api_key[:8]}"
            exchange_instance = await exchange_factory.get_exchange(exchange_instance_id)
            
            if not exchange_instance:
                return None
            
            trades = await exchange_instance.get_trades(symbol, limit)
            
            return [
                TradeResponse(
                    id=trade.id,
                    order_id=trade.order_id,
                    symbol=trade.symbol,
                    side=trade.side.value,
                    quantity=trade.quantity,
                    price=trade.price,
                    fee=trade.fee,
                    fee_currency=trade.fee_currency,
                    timestamp=trade.timestamp,
                    exchange_trade_id=trade.exchange_trade_id
                )
                for trade in trades
            ]
            
        except Exception as e:
            logger.error(f"Error getting trades for {exchange_id}: {e}")
            raise
