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

class BybitExchange(BaseExchange):
    """Bybit exchange integration"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        
        # API endpoints
        if testnet:
            self.base_url = "https://api-testnet.bybit.com"
            self.ws_url = "wss://stream-testnet.bybit.com/v5/public/linear"
        else:
            self.base_url = "https://api.bybit.com"
            self.ws_url = "wss://stream.bybit.com/v5/public/linear"
        
        self.session = None
        self.price_callbacks = {}
        
    async def connect(self) -> bool:
        """Connect to Bybit exchange"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Test connection
            async with self.session.get(f"{self.base_url}/v5/market/time") as response:
                if response.status == 200:
                    self.is_connected = True
                    logger.info("Connected to Bybit exchange")
                    return True
                else:
                    logger.error(f"Failed to connect to Bybit: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error connecting to Bybit: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Bybit exchange"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            # Close WebSocket connections
            for ws in self.ws_connections.values():
                await ws.close()
            self.ws_connections.clear()
            
            self.is_connected = False
            logger.info("Disconnected from Bybit exchange")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Bybit: {e}")
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
        """Make HTTP request to Bybit API"""
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
                headers['X-BAPI-API-KEY'] = self.api_key
            
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == 'GET':
                if params:
                    url += '?' + urlencode(params)
                async with self.session.get(url, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'POST':
                async with self.session.post(url, json=params, headers=headers) as response:
                    return await response.json()
            elif method.upper() == 'DELETE':
                if params:
                    url += '?' + urlencode(params)
                async with self.session.delete(url, headers=headers) as response:
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except Exception as e:
            logger.error(f"Error making request to Bybit: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            response = await self._make_request('GET', '/v5/account/wallet-balance', signed=True)
            return response
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    async def get_balances(self) -> List[Balance]:
        """Get account balances"""
        try:
            account_info = await self.get_account_info()
            balances = []
            
            result = account_info.get('result', {})
            list_data = result.get('list', [])
            
            for account in list_data:
                for coin in account.get('coin', []):
                    if float(coin['walletBalance']) > 0:
                        balances.append(Balance(
                            asset=coin['coin'],
                            free=float(coin['availableToWithdraw']),
                            locked=float(coin['walletBalance']) - float(coin['availableToWithdraw']),
                            total=float(coin['walletBalance'])
                        ))
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            raise
    
    async def get_symbols(self) -> List[str]:
        """Get available trading symbols"""
        try:
            response = await self._make_request('GET', '/v5/market/instruments-info', {'category': 'linear'})
            symbols = []
            
            result = response.get('result', {})
            list_data = result.get('list', [])
            
            for instrument in list_data:
                if instrument['status'] == 'Trading':
                    symbols.append(instrument['symbol'])
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            raise
    
    async def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for symbol"""
        try:
            if not self.validate_symbol(symbol):
                return None
            
            params = {'symbol': symbol, 'category': 'linear'}
            response = await self._make_request('GET', '/v5/market/tickers', params)
            
            result = response.get('result', {})
            list_data = result.get('list', [])
            
            if list_data:
                ticker = list_data[0]
                return PriceData(
                    symbol=symbol,
                    price=float(ticker['lastPrice']),
                    volume=float(ticker['volume24h']),
                    timestamp=datetime.utcnow(),
                    exchange=ExchangeType.BYBIT
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
            
            params = {'symbol': symbol, 'category': 'linear', 'limit': min(limit, 200)}
            response = await self._make_request('GET', '/v5/market/orderbook', params)
            
            result = response.get('result', {})
            
            return {
                'symbol': symbol,
                'bids': [[float(price), float(qty)] for price, qty in result.get('b', [])],
                'asks': [[float(price), float(qty)] for price, qty in result.get('a', [])],
                'lastUpdateId': result.get('u')
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
                'category': 'linear',
                'symbol': symbol,
                'side': side.value.capitalize(),
                'orderType': order_type.value.capitalize(),
                'qty': str(quantity)
            }
            
            if price and order_type != OrderType.MARKET:
                if not self.validate_price(price):
                    return None
                params['price'] = str(price)
            
            response = await self._make_request('POST', '/v5/order/create', params, signed=True)
            
            result = response.get('result', {})
            if 'orderId' in result:
                return Order(
                    id=result['orderId'],
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
                    exchange_order_id=result['orderId']
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
            
            params = {
                'category': 'linear',
                'symbol': symbol,
                'orderId': order_id
            }
            response = await self._make_request('POST', '/v5/order/cancel', params, signed=True)
            
            result = response.get('result', {})
            return 'orderId' in result
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    async def get_order(self, symbol: str, order_id: str) -> Optional[Order]:
        """Get order details"""
        try:
            if not self.validate_symbol(symbol):
                return None
            
            params = {
                'category': 'linear',
                'symbol': symbol,
                'orderId': order_id
            }
            response = await self._make_request('GET', '/v5/order/realtime', params, signed=True)
            
            result = response.get('result', {})
            list_data = result.get('list', [])
            
            if list_data:
                order_data = list_data[0]
                return Order(
                    id=order_data['orderId'],
                    symbol=symbol,
                    side=OrderSide.BUY if order_data['side'] == 'Buy' else OrderSide.SELL,
                    order_type=OrderType(order_data['orderType'].lower()),
                    quantity=float(order_data['qty']),
                    price=float(order_data['price']) if order_data['price'] != '0' else None,
                    status=OrderStatus(order_data['orderStatus'].lower()),
                    filled_quantity=float(order_data['cumExecQty']),
                    remaining_quantity=float(order_data['qty']) - float(order_data['cumExecQty']),
                    created_at=datetime.fromtimestamp(int(order_data['createdTime']) / 1000),
                    updated_at=datetime.fromtimestamp(int(order_data['updatedTime']) / 1000),
                    exchange_order_id=order_data['orderId']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting order: {e}")
            return None
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get open orders"""
        try:
            params = {'category': 'linear'}
            if symbol:
                if not self.validate_symbol(symbol):
                    return []
                params['symbol'] = symbol
            
            response = await self._make_request('GET', '/v5/order/realtime', params, signed=True)
            orders = []
            
            result = response.get('result', {})
            list_data = result.get('list', [])
            
            for order_data in list_data:
                if order_data['orderStatus'] in ['New', 'PartiallyFilled']:
                    order = Order(
                        id=order_data['orderId'],
                        symbol=order_data['symbol'],
                        side=OrderSide.BUY if order_data['side'] == 'Buy' else OrderSide.SELL,
                        order_type=OrderType(order_data['orderType'].lower()),
                        quantity=float(order_data['qty']),
                        price=float(order_data['price']) if order_data['price'] != '0' else None,
                        status=OrderStatus(order_data['orderStatus'].lower()),
                        filled_quantity=float(order_data['cumExecQty']),
                        remaining_quantity=float(order_data['qty']) - float(order_data['cumExecQty']),
                        created_at=datetime.fromtimestamp(int(order_data['createdTime']) / 1000),
                        updated_at=datetime.fromtimestamp(int(order_data['updatedTime']) / 1000),
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
            
            params = {
                'category': 'linear',
                'symbol': symbol,
                'limit': min(limit, 1000)
            }
            response = await self._make_request('GET', '/v5/execution/list', params, signed=True)
            trades = []
            
            result = response.get('result', {})
            list_data = result.get('list', [])
            
            for trade_data in list_data:
                trade = Trade(
                    id=trade_data['execId'],
                    order_id=trade_data['orderId'],
                    symbol=symbol,
                    side=OrderSide.BUY if trade_data['side'] == 'Buy' else OrderSide.SELL,
                    quantity=float(trade_data['execQty']),
                    price=float(trade_data['execPrice']),
                    fee=float(trade_data['execFee']),
                    fee_currency=trade_data['feeRate'],
                    timestamp=datetime.fromtimestamp(int(trade_data['execTime']) / 1000),
                    exchange_trade_id=trade_data['execId']
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
            
            if symbol in self.ws_connections:
                logger.warning(f"Already subscribed to {symbol}")
                return True
            
            # Create WebSocket connection
            ws_url = f"{self.ws_url}"
            
            try:
                websocket = await websockets.connect(ws_url)
                self.ws_connections[symbol] = websocket
                self.price_callbacks[symbol] = callback
                
                # Subscribe to ticker stream
                subscribe_msg = {
                    "op": "subscribe",
                    "args": [f"tickers.{symbol}"]
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                # Start listening for messages
                asyncio.create_task(self._handle_price_feed(symbol, websocket, callback))
                
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
            if symbol in self.ws_connections:
                websocket = self.ws_connections[symbol]
                await websocket.close()
                
                del self.ws_connections[symbol]
                del self.price_callbacks[symbol]
                
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
                    
                    # Handle subscription confirmation
                    if data.get('op') == 'subscribe':
                        logger.info(f"Subscription confirmed for {symbol}")
                        continue
                    
                    # Extract price data from ticker
                    if 'data' in data:
                        ticker_data = data['data']
                        if isinstance(ticker_data, list) and len(ticker_data) > 0:
                            ticker = ticker_data[0]
                            
                            price_data = PriceData(
                                symbol=symbol,
                                price=float(ticker['lastPrice']),
                                volume=float(ticker['volume24h']),
                                timestamp=datetime.utcnow(),
                                exchange=ExchangeType.BYBIT
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
