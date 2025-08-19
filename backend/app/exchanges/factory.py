from typing import Dict, Any, Optional
from .base import BaseExchange, ExchangeType
from .binance_exchange import BinanceExchange
from .bybit_exchange import BybitExchange
import logging

logger = logging.getLogger(__name__)

class ExchangeFactory:
    """Factory class for creating and managing exchange connections"""
    
    def __init__(self):
        self.exchanges: Dict[str, BaseExchange] = {}
        self.connections = {}
        
    async def create_exchange(self, exchange_type: str, api_key: str, api_secret: str, 
                             testnet: bool = True) -> Optional[BaseExchange]:
        """Create a new exchange instance"""
        try:
            exchange_type_enum = ExchangeType(exchange_type.lower())
            
            if exchange_type_enum == ExchangeType.BINANCE:
                exchange = BinanceExchange(api_key, api_secret, testnet)
            elif exchange_type_enum == ExchangeType.BYBIT:
                exchange = BybitExchange(api_key, api_secret, testnet)
            else:
                logger.error(f"Unsupported exchange type: {exchange_type}")
                return None
            
            # Connect to exchange
            if await exchange.connect():
                exchange_id = f"{exchange_type}_{api_key[:8]}"
                self.exchanges[exchange_id] = exchange
                self.connections[exchange_id] = {
                    'type': exchange_type,
                    'testnet': testnet,
                    'connected_at': exchange.last_execution if hasattr(exchange, 'last_execution') else None
                }
                
                logger.info(f"Exchange {exchange_type} created and connected successfully")
                return exchange
            else:
                logger.error(f"Failed to connect to {exchange_type}")
                return None
                
        except ValueError as e:
            logger.error(f"Invalid exchange type: {exchange_type}")
            return None
        except Exception as e:
            logger.error(f"Error creating exchange {exchange_type}: {e}")
            return None
    
    async def get_exchange(self, exchange_id: str) -> Optional[BaseExchange]:
        """Get an existing exchange instance"""
        return self.exchanges.get(exchange_id)
    
    async def remove_exchange(self, exchange_id: str) -> bool:
        """Remove and disconnect an exchange instance"""
        try:
            if exchange_id in self.exchanges:
                exchange = self.exchanges[exchange_id]
                await exchange.disconnect()
                
                del self.exchanges[exchange_id]
                del self.connections[exchange_id]
                
                logger.info(f"Exchange {exchange_id} removed successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing exchange {exchange_id}: {e}")
            return False
    
    async def get_all_exchanges(self) -> Dict[str, BaseExchange]:
        """Get all exchange instances"""
        return self.exchanges.copy()
    
    async def get_exchange_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all exchanges"""
        info = {}
        
        for exchange_id, exchange in self.exchanges.items():
            info[exchange_id] = {
                'exchange_info': exchange.get_exchange_info(),
                'connection_info': self.connections.get(exchange_id, {}),
                'is_healthy': await exchange.health_check()
            }
        
        return info
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all exchanges"""
        health_status = {}
        
        for exchange_id, exchange in self.exchanges.items():
            try:
                health_status[exchange_id] = await exchange.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {exchange_id}: {e}")
                health_status[exchange_id] = False
        
        return health_status
    
    async def subscribe_to_symbol(self, exchange_id: str, symbol: str, callback) -> bool:
        """Subscribe to price feed for a symbol on a specific exchange"""
        try:
            exchange = self.exchanges.get(exchange_id)
            if not exchange:
                logger.error(f"Exchange {exchange_id} not found")
                return False
            
            return await exchange.subscribe_price_feed(symbol, callback)
            
        except Exception as e:
            logger.error(f"Error subscribing to symbol {symbol} on {exchange_id}: {e}")
            return False
    
    async def unsubscribe_from_symbol(self, exchange_id: str, symbol: str) -> bool:
        """Unsubscribe from price feed for a symbol"""
        try:
            exchange = self.exchanges.get(exchange_id)
            if not exchange:
                logger.error(f"Exchange {exchange_id} not found")
                return False
            
            return await exchange.unsubscribe_price_feed(symbol)
            
        except Exception as e:
            logger.error(f"Error unsubscribing from symbol {symbol} on {exchange_id}: {e}")
            return False
    
    async def get_price_from_all_exchanges(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol from all connected exchanges"""
        prices = {}
        
        for exchange_id, exchange in self.exchanges.items():
            try:
                price_data = await exchange.get_price(symbol)
                if price_data:
                    prices[exchange_id] = {
                        'price': price_data.price,
                        'volume': price_data.volume,
                        'timestamp': price_data.timestamp.isoformat(),
                        'exchange': price_data.exchange.value
                    }
            except Exception as e:
                logger.error(f"Error getting price from {exchange_id}: {e}")
        
        return prices
    
    async def shutdown(self):
        """Shutdown all exchange connections"""
        try:
            for exchange_id in list(self.exchanges.keys()):
                await self.remove_exchange(exchange_id)
            
            logger.info("All exchange connections shutdown successfully")
            
        except Exception as e:
            logger.error(f"Error during exchange factory shutdown: {e}")

# Global exchange factory instance
exchange_factory = ExchangeFactory()