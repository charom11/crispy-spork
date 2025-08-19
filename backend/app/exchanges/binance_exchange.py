import asyncio
import json
import hmac
import hashlib
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
import aiohttp
import websockets
from datetime import datetime

from .base import (
    BaseExchange, ExchangeType, OrderType, OrderSide, OrderStatus,
    Order, Trade, PriceData, Balance
)
import logging

logger = logging.getLogger(__name__)

class BinanceExchange(BaseExchange):
    """Binance exchange integration"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        
        # API endpoints
        if testnet:
            self.base_url = "https://testnet.binance.vision"
            self.ws_url = "wss://testnet.binance.vision/ws"
        else:
            self.base_url = "https://api.binance.com"
            self.ws_url = "wss://stream.binance.com:9443/ws"
        
        self.session = None
        self.price_callbacks = {}
        
    async def connect(self) -> bool:
        """Connect to Binance exchange"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Test connection
            async with self.session.get(f"{self.base_url}/api/v3/ping") as response:
                if response.status == 200:
                    self.is_connected = True
                    logger.info("Connected to Binance exchange")
                    return True
                else:
                    logger.error(f"Failed to connect to Binance: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error connecting to Binance: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Binance exchange"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            # Close WebSocket connections
            for ws in self.ws_connections.values():
                await ws.close()
            self.ws_connections.clear()
            
            self.is_connected = False
            logger.info("Disconnected from Binance exchange")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Binance: {e}")
            return False
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC signature for authenticated requests"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, 
                           signed: bool = False) -> Dict[str, Any]:
        """Make HTTP request to Binance API"""
        try:
            if params is None:
                params = {}
            
            # Add timestamp for signed requests
            if signed:
                params['timestamp'] = int(time.time() * 1000)
                params['signature'] = self._generate_signature(params)
            
            # Add API key header
            headers = {}
            if self.api_key:
                headers['X-MBX-APIKEY'] = self.api_key
            
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                if params:
                    url += '?' + urlencode(params)
                async with self.session.get(url, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'POST':
                async with self.session.post(url, data=params, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'DELETE':
                if params:
                    url += '?' + urlencode(params)
                async with self.session.delete(url, headers=headers) as response:
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except Exception as e:
            logger.error(f"Error making request to Binance: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            response = await self._make_request('GET', '/api/v3/account', signed=True)
            return response
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    async def get_balances(self) -> List[Balance]:
        """Get account balances"""
        try:
            account_info = await self.get_account_info()
            balances = []
            
            for balance in account_info.get('balances', []):
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    balances.append(Balance(
                        asset=balance['asset'],
                        free=float(balance['free']),
                        locked=float(balance['locked']),
                        total=float(balance['free']) + float(balance['locked'])
                    ))
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            raise
    
    async def get_symbols(self) -> List[str]:
        """Get available trading symbols"""
        try:
            response = await self._make_request('GET', '/api/v3/exchangeInfo')
            symbols = []
            
            for symbol_info in response.get('symbols', []):
                if symbol_info['status'] == 'TRADING':
                    symbols.append(symbol_info['symbol'])
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            raise
    
    async def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for symbol"""
        try:
            if not self.validate_symbol(symbol):
                return None
            
            response = await self._make_request('GET', '/api/v3/ticker/24hr', {'symbol': symbol})
            
            if 'price' in response:
                return PriceData(
                    symbol=symbol,
                    price=float(response['price']),
                    volume=float(response['volume']),
                    timestamp=datetime.utcnow(),
                    exchange=ExchangeType.BINANCE
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get order book for symbol"""
        try:
            if not self.validate_symbol(symbol):
                return {}
            
            params = {'symbol': symbol, 'limit': min(limit, 100)}
            response = await self._make_request('GET', '/api/v3/depth', params)
            
            return {
                'symbol': symbol,
                'bids': [[float(price), float(qty)] for price, qty in response.get('bids', [])],
                'asks': [[float(price), float(qty)] for price, qty in response.get('asks', [])],
                'lastUpdateId': response.get('lastUpdateId')
            }
            
        except Exception as e:
            logger.error(f"Error getting order book for {symbol}: {e}")
            return {}
    
    async def place_order(self, symbol: str, side: OrderSide, order_type: OrderType, 
                         quantity: float, price: Optional[float] = None) -> Optional[Order]:
        """Place a new order"""
        try:
            if not self.validate_symbol(symbol) or not self.validate_quantity(quantity):
                return None
            
            params = {
                'symbol': symbol,
                'side': side.value.upper(),
                'type': order_type.value.upper(),
                'quantity': quantity
            }
            
            if price and order_type != OrderType.MARKET:
                if not self.validate_price(price):
                    return None
                params['price'] = price
            
            response = await self._make_request('POST', '/api/v3/order', params, signed=True)
            
            if 'orderId' in response:
                return Order(
                    id=response['orderId'],
                    symbol=symbol,
                    side=side,
                    order_type=order_type,
                    quantity=quantity,
                    price=price,
                    status=OrderStatus.PENDING,
                    filled_quantity=0.0,
                    remaining_quantity=quantity,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    exchange_order_id=response['orderId']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order"""
        try:
            if not self.validate_symbol(symbol):
                return False
            
            params = {'symbol': symbol, 'orderId': order_id}
            response = await self._make_request('DELETE', '/api/v3/order', params, signed=True)
            
            return 'orderId' in response
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    async def get_order(self, symbol: str, order_id: str) -> Optional[Order]:
        """Get order details"""
        try:
            if not self.validate_symbol(symbol):
                return None
            
            params = {'symbol': symbol, 'orderId': order_id}
            response = await self._make_request('GET', '/api/v3/order', params, signed=True)
            
            if 'orderId' in response:
                return Order(
                    id=response['orderId'],
                    symbol=symbol,
                    side=OrderSide.BUY if response['side'] == 'BUY' else OrderSide.SELL,
                    order_type=OrderType(response['type'].lower()),
                    quantity=float(response['origQty']),
                    price=float(response['price']) if response['price'] != '0' else None,
                    status=OrderStatus(response['status'].lower()),
                    filled_quantity=float(response['executedQty']),
                    remaining_quantity=float(response['origQty']) - float(response['executedQty']),
                    created_at=datetime.fromtimestamp(response['time'] / 1000),
                    updated_at=datetime.fromtimestamp(response['updateTime'] / 1000),
                    exchange_order_id=response['orderId']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting order: {e}")
            return None
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get open orders"""
        try:
            params = {}
            if symbol:
                if not self.validate_symbol(symbol):
                    return []
                params['symbol'] = symbol
            
            response = await self._make_request('GET', '/api/v3/openOrders', params, signed=True)
            orders = []
            
            for order_data in response:
                order = Order(
                    id=order_data['orderId'],
                    symbol=order_data['symbol'],
                    side=OrderSide.BUY if order_data['side'] == 'BUY' else OrderSide.SELL,
                    order_type=OrderType(order_data['type'].lower()),
                    quantity=float(order_data['origQty']),
                    price=float(order_data['price']) if order_data['price'] != '0' else None,
                    status=OrderStatus(order_data['status'].lower()),
                    filled_quantity=float(order_data['executedQty']),
                    remaining_quantity=float(order_data['origQty']) - float(order_data['executedQty']),
                    created_at=datetime.fromtimestamp(order_data['time'] / 1000),
                    updated_at=datetime.fromtimestamp(order_data['updateTime'] / 1000),
                    exchange_order_id=order_data['orderId']
                )
                orders.append(order)
            
            return orders
            
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    async def get_trades(self, symbol: str, limit: int = 100) -> List[Trade]:
        """Get recent trades"""
        try:
            if not self.validate_symbol(symbol):
                return []
            
            params = {'symbol': symbol, 'limit': min(limit, 1000)}
            response = await self._make_request('GET', '/api/v3/myTrades', params, signed=True)
            trades = []
            
            for trade_data in response:
                trade = Trade(
                    id=trade_data['id'],
                    order_id=trade_data['orderId'],
                    symbol=symbol,
                    side=OrderSide.BUY if trade_data['isBuyer'] else OrderSide.SELL,
                    quantity=float(trade_data['qty']),
                    price=float(trade_data['price']),
                    fee=float(trade_data['commission']),
                    fee_currency=trade_data['commissionAsset'],
                    timestamp=datetime.fromtimestamp(trade_data['time'] / 1000),
                    exchange_trade_id=trade_data['id']
                )
                trades.append(trade)
            
            return trades
            
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return []
    
    async def subscribe_price_feed(self, symbol: str, callback) -> bool:
        """Subscribe to real-time price feed"""
        try:
            if not self.validate_symbol(symbol):
                return False
            
            # Convert symbol to lowercase for WebSocket
            ws_symbol = symbol.lower()
            
            if ws_symbol in self.ws_connections:
                logger.warning(f"Already subscribed to {symbol}")
                return True
            
            # Create WebSocket connection
            ws_url = f"{self.ws_url}/{ws_symbol}@ticker"
            
            try:
                websocket = await websockets.connect(ws_url)
                self.ws_connections[ws_symbol] = websocket
                self.price_callbacks[ws_symbol] = callback
                
                # Start listening for messages
                asyncio.create_task(self._handle_price_feed(ws_symbol, websocket, callback))
                
                logger.info(f"Subscribed to price feed for {symbol}")
                return True
                
            except Exception as e:
                logger.error(f"Error creating WebSocket connection for {symbol}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error subscribing to price feed for {symbol}: {e}")
            return False
    
    async def unsubscribe_price_feed(self, symbol: str) -> bool:
        """Unsubscribe from price feed"""
        try:
            ws_symbol = symbol.lower()
            
            if ws_symbol in self.ws_connections:
                websocket = self.ws_connections[ws_symbol]
                await websocket.close()
                
                del self.ws_connections[ws_symbol]
                del self.price_callbacks[ws_symbol]
                
                logger.info(f"Unsubscribed from price feed for {symbol}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error unsubscribing from price feed for {symbol}: {e}")
            return False
    
    async def _handle_price_feed(self, symbol: str, websocket, callback):
        """Handle incoming WebSocket messages"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # Extract price data
                    if 'c' in data:  # Close price
                        price_data = PriceData(
                            symbol=symbol.upper(),
                            price=float(data['c']),
                            volume=float(data['v']),
                            timestamp=datetime.utcnow(),
                            exchange=ExchangeType.BINANCE
                        )
                        
                        # Call callback with price data
                        await callback(price_data)
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON message from {symbol}: {message}")
                except Exception as e:
                    logger.error(f"Error processing message from {symbol}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed for {symbol}")
        except Exception as e:
            logger.error(f"Error in price feed handler for {symbol}: {e}")
        finally:
            # Clean up connection
            if symbol in self.ws_connections:
                del self.ws_connections[symbol]
            if symbol in self.price_callbacks:
                del self.price_callbacks[symbol]
