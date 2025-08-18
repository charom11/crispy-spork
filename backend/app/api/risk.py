from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.risk_service import RiskService
from app.schemas.risk import (
    RiskProfile, RiskProfileCreate, RiskProfileUpdate,
    RiskAlert, RiskAlertUpdate, RiskMetrics,
    RiskCheckRequest, RiskCheckResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/risk", tags=["risk-management"])

@router.get("/profile", response_model=RiskProfile)
async def get_risk_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's risk profile"""
    risk_service = RiskService(db)
    risk_profile = risk_service.get_risk_profile(str(current_user.id))
    
    if not risk_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No risk profile found. Please create one first."
        )
    
    return risk_profile

@router.post("/profile", response_model=RiskProfile, status_code=status.HTTP_201_CREATED)
async def create_risk_profile(
    risk_data: RiskProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new risk profile for the current user"""
    risk_service = RiskService(db)
    
    try:
        risk_profile = risk_service.create_risk_profile(str(current_user.id), risk_data)
        return risk_profile
    except Exception as e:
        logger.error(f"Error creating risk profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create risk profile"
        )

@router.put("/profile", response_model=RiskProfile)
async def update_risk_profile(
    risk_data: RiskProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's risk profile"""
    risk_service = RiskService(db)
    
    try:
        risk_profile = risk_service.update_risk_profile(str(current_user.id), risk_data)
        if not risk_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No risk profile found to update"
            )
        return risk_profile
    except Exception as e:
        logger.error(f"Error updating risk profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update risk profile"
        )

@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete the current user's risk profile"""
    risk_service = RiskService(db)
    
    try:
        success = risk_service.delete_risk_profile(str(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No risk profile found to delete"
            )
    except Exception as e:
        logger.error(f"Error deleting risk profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete risk profile"
        )

@router.get("/metrics", response_model=RiskMetrics)
async def get_risk_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current risk metrics for the user"""
    risk_service = RiskService(db)
    
    try:
        metrics = risk_service.get_risk_metrics(str(current_user.id))
        return metrics
    except Exception as e:
        logger.error(f"Error getting risk metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get risk metrics"
        )

@router.post("/check", response_model=RiskCheckResponse)
async def check_trade_risk(
    trade_request: RiskCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a trade meets risk requirements"""
    risk_service = RiskService(db)
    
    try:
        response = risk_service.check_trade_risk(str(current_user.id), trade_request)
        return response
    except Exception as e:
        logger.error(f"Error checking trade risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check trade risk"
        )

@router.get("/alerts", response_model=List[RiskAlert])
async def get_risk_alerts(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk alerts for the current user"""
    risk_service = RiskService(db)
    
    try:
        alerts = risk_service.get_user_alerts(str(current_user.id), active_only)
        return alerts
    except Exception as e:
        logger.error(f"Error getting risk alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get risk alerts"
        )

@router.post("/alerts/{alert_id}/acknowledge", response_model=RiskAlert)
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge a risk alert"""
    risk_service = RiskService(db)
    
    try:
        success = risk_service.acknowledge_alert(alert_id, str(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Return the updated alert
        alerts = risk_service.get_user_alerts(str(current_user.id), active_only=False)
        alert = next((a for a in alerts if str(a.id) == alert_id), None)
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found after acknowledgment"
            )
        
        return alert
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert"
        )

@router.get("/profile/default", response_model=RiskProfileCreate)
async def get_default_risk_profile():
    """Get default risk profile settings"""
    return RiskProfileCreate(
        name="Default Risk Profile",
        max_position_size=10000.0,
        max_positions=10,
        max_leverage=1.0,
        daily_loss_limit=1000.0,
        weekly_loss_limit=5000.0,
        monthly_loss_limit=20000.0,
        total_loss_limit=50000.0,
        default_stop_loss_percent=5.0,
        default_take_profit_percent=10.0,
        trailing_stop_enabled=False,
        trailing_stop_percent=2.0,
        max_risk_per_trade=2.0,
        max_portfolio_risk=10.0,
        max_volatility_threshold=50.0,
        correlation_limit=0.7,
        trading_hours_start="09:00",
        trading_hours_end="17:00",
        weekend_trading=False
    )

@router.get("/health", response_model=dict)
async def risk_health_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Health check for risk management system"""
    try:
        risk_service = RiskService(db)
        risk_profile = risk_service.get_risk_profile(str(current_user.id))
        
        return {
            "status": "healthy",
            "risk_profile_exists": risk_profile is not None,
            "user_id": str(current_user.id),
            "timestamp": "2024-01-01T00:00:00Z"  # Mock timestamp
        }
    except Exception as e:
        logger.error(f"Risk health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "user_id": str(current_user.id),
            "timestamp": "2024-01-01T00:00:00Z"  # Mock timestamp
        }