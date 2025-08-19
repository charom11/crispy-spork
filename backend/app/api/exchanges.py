from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.database import get_db
from app.schemas.exchange import (
    ExchangeConfigCreate, ExchangeConfigUpdate, ExchangeConfigResponse,
    OrderCreate, OrderResponse, TradeResponse, BalanceResponse,
    PriceData, OrderBook, ExchangeStatus
)
from app.services.exchange_service import ExchangeService
from app.core.deps import get_current_active_user
from app.models.user import User
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exchanges", tags=["exchanges"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

@router.get("/", response_model=List[ExchangeConfigResponse])
async def get_exchanges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all exchange configurations for the current user"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        exchanges = await exchange_service.get_user_exchanges()
        return exchanges
        
    except Exception as e:
        logger.error(f"Error fetching exchanges: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=ExchangeConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_exchange(
    exchange_create: ExchangeConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new exchange configuration"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        exchange = await exchange_service.create_exchange(exchange_create)
        
        if not exchange:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create exchange configuration"
            )
        
        return exchange
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating exchange: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{exchange_id}", response_model=ExchangeConfigResponse)
async def get_exchange(
    exchange_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific exchange configuration"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        exchange = await exchange_service.get_exchange(exchange_id)
        
        if not exchange:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange configuration not found"
            )
        
        return exchange
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching exchange {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{exchange_id}", response_model=ExchangeConfigResponse)
async def update_exchange(
    exchange_id: str,
    exchange_update: ExchangeConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an exchange configuration"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        exchange = await exchange_service.update_exchange(exchange_id, exchange_update)
        
        if not exchange:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange configuration not found"
            )
        
        return exchange
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating exchange {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exchange(
    exchange_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an exchange configuration"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        success = await exchange_service.delete_exchange(exchange_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange configuration not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting exchange {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{exchange_id}/status", response_model=ExchangeStatus)
async def get_exchange_status(
    exchange_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get exchange connection status"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        status_info = await exchange_service.get_exchange_status(exchange_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange not found"
            )
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exchange status {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{exchange_id}/balances", response_model=List[BalanceResponse])
async def get_balances(
    exchange_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get account balances for an exchange"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        balances = await exchange_service.get_balances(exchange_id)
        
        if balances is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange not found"
            )
        
        return balances
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting balances for {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{exchange_id}/symbols", response_model=List[str])
async def get_symbols(
    exchange_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get available trading symbols for an exchange"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        symbols = await exchange_service.get_symbols(exchange_id)
        
        if symbols is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange not found"
            )
        
        return symbols
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting symbols for {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{exchange_id}/price/{symbol}", response_model=PriceData)
async def get_price(
    exchange_id: str,
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current price for a symbol"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        price_data = await exchange_service.get_price(exchange_id, symbol)
        
        if not price_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Price data not found"
            )
        
        return price_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {symbol} on {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{exchange_id}/orderbook/{symbol}", response_model=OrderBook)
async def get_order_book(
    exchange_id: str,
    symbol: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get order book for a symbol"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        order_book = await exchange_service.get_order_book(exchange_id, symbol, limit)
        
        if not order_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order book not found"
            )
        
        return order_book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order book for {symbol} on {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{exchange_id}/orders", response_model=OrderResponse)
async def place_order(
    exchange_id: str,
    order_create: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Place a new order"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        order = await exchange_service.place_order(exchange_id, order_create)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to place order"
            )
        
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error placing order on {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{exchange_id}/orders", response_model=List[OrderResponse])
async def get_orders(
    exchange_id: str,
    symbol: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get open orders for an exchange"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        orders = await exchange_service.get_open_orders(exchange_id, symbol)
        
        if orders is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange not found"
            )
        
        return orders
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orders for {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{exchange_id}/orders/{order_id}")
async def cancel_order(
    exchange_id: str,
    order_id: str,
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel an order"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        success = await exchange_service.cancel_order(exchange_id, symbol, order_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel order"
            )
        
        return {"message": "Order cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order {order_id} on {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{exchange_id}/trades", response_model=List[TradeResponse])
async def get_trades(
    exchange_id: str,
    symbol: str,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recent trades for an exchange"""
    try:
        exchange_service = ExchangeService(db, current_user.id)
        trades = await exchange_service.get_trades(exchange_id, symbol, limit)
        
        if trades is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exchange not found"
            )
        
        return trades
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trades for {exchange_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.websocket("/ws/{exchange_id}/{symbol}")
async def websocket_endpoint(
    websocket: WebSocket,
    exchange_id: str,
    symbol: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time price feeds"""
    client_id = f"{exchange_id}_{symbol}"
    
    try:
        await manager.connect(websocket, client_id)
        
        # Subscribe to price feed
        # Note: In a real implementation, you'd want to manage subscriptions properly
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Echo back for testing
            await manager.send_personal_message(f"Message received: {data}", client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)
