from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from datetime import datetime

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.trading_mode_service import TradingModeService
from app.schemas.trading_mode import (
    TradingMode, TradingModeCreate, TradingModeUpdate,
    TradingModeSummary, TradingModeSwitch, TradingModeSwitchResponse,
    TradingStatistics, TradingModeValidation
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trading-mode", tags=["trading-mode"])

@router.get("/", response_model=TradingModeSummary)
async def get_trading_mode_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trading mode summary for the current user"""
    trading_mode_service = TradingModeService(db)
    
    try:
        summary = trading_mode_service.get_trading_mode_summary(str(current_user.id))
        return summary
    except Exception as e:
        logger.error(f"Error getting trading mode summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trading mode summary"
        )

@router.get("/full", response_model=TradingMode)
async def get_trading_mode(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full trading mode configuration for the current user"""
    trading_mode_service = TradingModeService(db)
    
    try:
        trading_mode = trading_mode_service.get_trading_mode(str(current_user.id))
        if not trading_mode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No trading mode configured. Please create one first."
            )
        return trading_mode
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trading mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trading mode"
        )

@router.post("/", response_model=TradingMode, status_code=status.HTTP_201_CREATED)
async def create_trading_mode(
    mode_data: TradingModeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create trading mode configuration for the current user"""
    trading_mode_service = TradingModeService(db)
    
    try:
        trading_mode = trading_mode_service.create_trading_mode(str(current_user.id), mode_data)
        return trading_mode
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating trading mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create trading mode"
        )

@router.put("/", response_model=TradingMode)
async def update_trading_mode(
    mode_data: TradingModeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update trading mode configuration for the current user"""
    trading_mode_service = TradingModeService(db)
    
    try:
        trading_mode = trading_mode_service.update_trading_mode(str(current_user.id), mode_data)
        if not trading_mode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No trading mode found to update"
            )
        return trading_mode
    except Exception as e:
        logger.error(f"Error updating trading mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update trading mode"
        )

@router.post("/switch", response_model=TradingModeSwitchResponse)
async def switch_trading_mode(
    switch_data: TradingModeSwitch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Switch between paper and live trading modes"""
    trading_mode_service = TradingModeService(db)
    
    try:
        if switch_data.target_mode.lower() == "paper":
            success = trading_mode_service.switch_to_paper_trading(str(current_user.id))
            if success:
                return TradingModeSwitchResponse(
                    success=True,
                    message="Successfully switched to paper trading",
                    new_mode="paper",
                    previous_mode="live",
                    timestamp=datetime.utcnow()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to switch to paper trading"
                )
        
        elif switch_data.target_mode.lower() == "live":
            # Additional confirmation required for live trading
            if not switch_data.confirm_live_trading:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Live trading confirmation required"
                )
            
            success, message = trading_mode_service.switch_to_live_trading(str(current_user.id))
            if success:
                return TradingModeSwitchResponse(
                    success=True,
                    message=message,
                    new_mode="live",
                    previous_mode="paper",
                    timestamp=datetime.utcnow()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=message
                )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid target mode. Must be 'paper' or 'live'"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching trading mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch trading mode"
        )

@router.get("/statistics", response_model=TradingStatistics)
async def get_trading_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trading statistics for the current user"""
    trading_mode_service = TradingModeService(db)
    
    try:
        stats = trading_mode_service.get_trading_statistics(str(current_user.id))
        return TradingStatistics(**stats)
    except Exception as e:
        logger.error(f"Error getting trading statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trading statistics"
        )

@router.post("/validate-trade", response_model=TradingModeValidation)
async def validate_trade_request(
    trade_value: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate if a trade request is allowed"""
    trading_mode_service = TradingModeService(db)
    
    try:
        is_allowed, message = trading_mode_service.validate_trade_request(
            str(current_user.id), trade_value
        )
        
        # Get additional validation details
        trading_mode = trading_mode_service.get_trading_mode(str(current_user.id))
        stats = trading_mode_service.get_trading_statistics(str(current_user.id))
        
        if trading_mode:
            daily_trades_remaining = max(0, trading_mode.max_daily_trades - stats.get('daily_trades', 0))
            max_volume = float(trading_mode.max_daily_volume.replace(',', ''))
            daily_volume_remaining = max(0, max_volume - stats.get('daily_volume', 0))
            max_position_size = trading_mode.max_live_position_size if not trading_mode.is_paper_trading else "10000"
        else:
            daily_trades_remaining = 0
            daily_volume_remaining = 0
            max_position_size = "0"
        
        return TradingModeValidation(
            is_allowed=is_allowed,
            message=message,
            trading_mode="paper" if trading_mode and trading_mode.is_paper_trading else "live",
            daily_trades_remaining=daily_trades_remaining,
            daily_volume_remaining=daily_volume_remaining,
            max_position_size=max_position_size
        )
        
    except Exception as e:
        logger.error(f"Error validating trade request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate trade request"
        )

@router.post("/reset-paper-balance")
async def reset_paper_trading_balance(
    new_balance: str = "100000",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset paper trading balance (for testing purposes)"""
    trading_mode_service = TradingModeService(db)
    
    try:
        success = trading_mode_service.reset_paper_trading_balance(
            str(current_user.id), new_balance
        )
        
        if success:
            return {
                "success": True,
                "message": f"Paper trading balance reset to ${new_balance}",
                "new_balance": new_balance
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reset balance. User may not be in paper trading mode."
            )
            
    except Exception as e:
        logger.error(f"Error resetting paper trading balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset paper trading balance"
        )

@router.get("/health", response_model=Dict[str, Any])
async def trading_mode_health_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Health check for trading mode system"""
    try:
        trading_mode_service = TradingModeService(db)
        trading_mode = trading_mode_service.get_trading_mode(str(current_user.id))
        
        return {
            "status": "healthy",
            "trading_mode_configured": trading_mode is not None,
            "current_mode": trading_mode.mode if trading_mode else "none",
            "user_id": str(current_user.id),
            "timestamp": "2024-01-01T00:00:00Z"  # Mock timestamp
        }
    except Exception as e:
        logger.error(f"Trading mode health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "user_id": str(current_user.id),
            "timestamp": "2024-01-01T00:00:00Z"  # Mock timestamp
        }