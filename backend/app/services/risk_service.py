from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
import logging
import numpy as np
from app.models.risk import RiskProfile, RiskAlert
from app.schemas.risk import (
    RiskProfileCreate, RiskProfileUpdate, RiskAlertCreate, 
    RiskAlertUpdate, RiskMetrics, RiskCheckRequest, RiskCheckResponse
)
from app.core.deps import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

class RiskService:
    """Service for managing risk profiles and performing risk checks"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Risk Profile Management
    def create_risk_profile(self, user_id: str, risk_data: RiskProfileCreate) -> RiskProfile:
        """Create a new risk profile for a user"""
        try:
            # Check if user already has a risk profile
            existing_profile = self.db.query(RiskProfile).filter(
                and_(
                    RiskProfile.user_id == user_id,
                    RiskProfile.is_active == True
                )
            ).first()
            
            if existing_profile:
                # Deactivate existing profile
                existing_profile.is_active = False
                self.db.commit()
            
            # Create new profile
            risk_profile = RiskProfile(
                user_id=user_id,
                **risk_data.dict()
            )
            
            self.db.add(risk_profile)
            self.db.commit()
            self.db.refresh(risk_profile)
            
            logger.info(f"Created risk profile {risk_profile.id} for user {user_id}")
            return risk_profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating risk profile: {e}")
            raise
    
    def get_risk_profile(self, user_id: str) -> Optional[RiskProfile]:
        """Get the active risk profile for a user"""
        return self.db.query(RiskProfile).filter(
            and_(
                RiskProfile.user_id == user_id,
                RiskProfile.is_active == True
            )
        ).first()
    
    def update_risk_profile(self, user_id: str, risk_data: RiskProfileUpdate) -> Optional[RiskProfile]:
        """Update the active risk profile for a user"""
        try:
            risk_profile = self.get_risk_profile(user_id)
            if not risk_profile:
                return None
            
            # Update fields
            update_data = risk_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(risk_profile, field, value)
            
            risk_profile.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(risk_profile)
            
            logger.info(f"Updated risk profile {risk_profile.id} for user {user_id}")
            return risk_profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating risk profile: {e}")
            raise
    
    def delete_risk_profile(self, user_id: str) -> bool:
        """Delete the active risk profile for a user"""
        try:
            risk_profile = self.get_risk_profile(user_id)
            if not risk_profile:
                return False
            
            risk_profile.is_active = False
            self.db.commit()
            
            logger.info(f"Deleted risk profile {risk_profile.id} for user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting risk profile: {e}")
            raise
    
    # Risk Alerts Management
    def create_risk_alert(self, alert_data: RiskAlertCreate) -> RiskAlert:
        """Create a new risk alert"""
        try:
            risk_alert = RiskAlert(**alert_data.dict())
            self.db.add(risk_alert)
            self.db.commit()
            self.db.refresh(risk_alert)
            
            logger.info(f"Created risk alert {risk_alert.id} for user {alert_data.user_id}")
            return risk_alert
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating risk alert: {e}")
            raise
    
    def get_user_alerts(self, user_id: str, active_only: bool = True) -> List[RiskAlert]:
        """Get risk alerts for a user"""
        query = self.db.query(RiskAlert).filter(RiskAlert.user_id == user_id)
        
        if active_only:
            query = query.filter(RiskAlert.is_active == True)
        
        return query.order_by(desc(RiskAlert.created_at)).all()
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge a risk alert"""
        try:
            alert = self.db.query(RiskAlert).filter(RiskAlert.id == alert_id).first()
            if not alert:
                return False
            
            alert.is_acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            self.db.commit()
            
            logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error acknowledging alert: {e}")
            raise
    
    # Risk Checking
    def check_trade_risk(self, user_id: str, trade_request: RiskCheckRequest) -> RiskCheckResponse:
        """Check if a trade meets risk requirements"""
        try:
            risk_profile = self.get_risk_profile(user_id)
            if not risk_profile:
                return RiskCheckResponse(
                    is_allowed=False,
                    risk_score=100,
                    errors=["No risk profile found"]
                )
            
            warnings = []
            errors = []
            risk_factors = {}
            
            # Check trading hours
            if not self._check_trading_hours(risk_profile):
                errors.append("Trading outside allowed hours")
                risk_factors["trading_hours"] = "Outside allowed hours"
            
            # Check position limits (mock data for now)
            position_check = self._check_position_limits(risk_profile, trade_request)
            if not position_check["allowed"]:
                errors.extend(position_check["errors"])
                risk_factors["position_limits"] = position_check["details"]
            
            # Check loss limits (mock data for now)
            loss_check = self._check_loss_limits(risk_profile)
            if not loss_check["allowed"]:
                errors.extend(loss_check["errors"])
                risk_factors["loss_limits"] = loss_check["details"]
            
            # Check volatility (mock data for now)
            volatility_check = self._check_volatility(risk_profile, trade_request)
            if not volatility_check["allowed"]:
                warnings.extend(volatility_check["warnings"])
                risk_factors["volatility"] = volatility_check["details"]
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(risk_profile, trade_request, risk_factors)
            
            # Determine if trade is allowed
            is_allowed = len(errors) == 0
            
            # Generate suggestions
            suggested_quantity = self._suggest_quantity(risk_profile, trade_request) if not is_allowed else None
            suggested_price = self._suggest_price(risk_profile, trade_request) if not is_allowed else None
            
            return RiskCheckResponse(
                is_allowed=is_allowed,
                risk_score=risk_score,
                warnings=warnings,
                errors=errors,
                suggested_quantity=suggested_quantity,
                suggested_price=suggested_price,
                risk_factors=risk_factors
            )
            
        except Exception as e:
            logger.error(f"Error checking trade risk: {e}")
            return RiskCheckResponse(
                is_allowed=False,
                risk_score=100,
                errors=[f"Risk check error: {str(e)}"]
            )
    
    def get_risk_metrics(self, user_id: str) -> RiskMetrics:
        """Get current risk metrics for a user"""
        try:
            # Mock data - in real app, this would calculate from actual portfolio data
            current_portfolio_value = 125000.0
            daily_pnl = 2500.0
            daily_pnl_percent = 2.04
            weekly_pnl = 8500.0
            weekly_pnl_percent = 7.28
            monthly_pnl = 18500.0
            monthly_pnl_percent = 17.38
            total_pnl = 25000.0
            total_pnl_percent = 25.0
            
            # Get risk profile
            risk_profile = self.get_risk_profile(user_id)
            if not risk_profile:
                # Return default metrics
                return RiskMetrics(
                    current_portfolio_value=current_portfolio_value,
                    daily_pnl=daily_pnl,
                    daily_pnl_percent=daily_pnl_percent,
                    weekly_pnl=weekly_pnl,
                    weekly_pnl_percent=weekly_pnl_percent,
                    monthly_pnl=monthly_pnl,
                    monthly_pnl_percent=monthly_pnl_percent,
                    total_pnl=total_pnl,
                    total_pnl_percent=total_pnl_percent,
                    current_risk_level="medium",
                    portfolio_risk_percent=5.0,
                    max_drawdown=8.5,
                    sharpe_ratio=1.2,
                    volatility=25.0,
                    open_positions=3,
                    total_position_value=45000.0,
                    largest_position=20000.0,
                    position_concentration=16.0,
                    daily_loss_limit_remaining=1000.0,
                    weekly_loss_limit_remaining=5000.0,
                    monthly_loss_limit_remaining=20000.0,
                    total_loss_limit_remaining=50000.0,
                    active_alerts_count=0,
                    critical_alerts_count=0
                )
            
            # Calculate remaining limits
            daily_loss_limit_remaining = risk_profile.daily_loss_limit + daily_pnl
            weekly_loss_limit_remaining = risk_profile.weekly_loss_limit + weekly_pnl
            monthly_loss_limit_remaining = risk_profile.monthly_loss_limit + monthly_pnl
            total_loss_limit_remaining = risk_profile.total_loss_limit + total_pnl
            
            # Determine risk level
            current_risk_level = self._calculate_risk_level(
                daily_pnl_percent, weekly_pnl_percent, monthly_pnl_percent
            )
            
            # Get active alerts count
            active_alerts = self.get_user_alerts(user_id, active_only=True)
            active_alerts_count = len(active_alerts)
            critical_alerts_count = len([a for a in active_alerts if a.severity == "critical"])
            
            return RiskMetrics(
                current_portfolio_value=current_portfolio_value,
                daily_pnl=daily_pnl,
                daily_pnl_percent=daily_pnl_percent,
                weekly_pnl=weekly_pnl,
                weekly_pnl_percent=weekly_pnl_percent,
                monthly_pnl=monthly_pnl,
                monthly_pnl_percent=monthly_pnl_percent,
                total_pnl=total_pnl,
                total_pnl_percent=total_pnl_percent,
                current_risk_level=current_risk_level,
                portfolio_risk_percent=5.0,
                max_drawdown=8.5,
                sharpe_ratio=1.2,
                volatility=25.0,
                open_positions=3,
                total_position_value=45000.0,
                largest_position=20000.0,
                position_concentration=16.0,
                daily_loss_limit_remaining=daily_loss_limit_remaining,
                weekly_loss_limit_remaining=weekly_loss_limit_remaining,
                monthly_loss_limit_remaining=monthly_loss_limit_remaining,
                total_loss_limit_remaining=total_loss_limit_remaining,
                active_alerts_count=active_alerts_count,
                critical_alerts_count=critical_alerts_count
            )
            
        except Exception as e:
            logger.error(f"Error getting risk metrics: {e}")
            raise
    
    # Private helper methods
    def _check_trading_hours(self, risk_profile: RiskProfile) -> bool:
        """Check if current time is within trading hours"""
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        current_weekday = now.weekday()
        
        # Check weekend trading
        if current_weekday >= 5 and not risk_profile.weekend_trading:
            return False
        
        # Check trading hours
        if not (risk_profile.trading_hours_start <= current_time <= risk_profile.trading_hours_end):
            return False
        
        return True
    
    def _check_position_limits(self, risk_profile: RiskProfile, trade_request: RiskCheckRequest) -> Dict[str, Any]:
        """Check position limits"""
        # Mock data - in real app, this would check actual positions
        current_positions = 3
        current_position_value = 45000.0
        
        errors = []
        details = {}
        
        # Check max positions
        if current_positions >= risk_profile.max_positions:
            errors.append(f"Maximum positions limit reached ({current_positions}/{risk_profile.max_positions})")
            details["max_positions"] = f"{current_positions}/{risk_profile.max_positions}"
        
        # Check position size
        if trade_request.quantity * (trade_request.price or 50000) > risk_profile.max_position_size:
            errors.append(f"Position size exceeds limit")
            details["position_size"] = "Exceeds limit"
        
        return {
            "allowed": len(errors) == 0,
            "errors": errors,
            "details": details
        }
    
    def _check_loss_limits(self, risk_profile: RiskProfile) -> Dict[str, Any]:
        """Check loss limits"""
        # Mock data - in real app, this would check actual P&L
        daily_pnl = 2500.0
        weekly_pnl = 8500.0
        monthly_pnl = 18500.0
        total_pnl = 25000.0
        
        errors = []
        details = {}
        
        # Check daily loss limit
        if daily_pnl < -risk_profile.daily_loss_limit:
            errors.append("Daily loss limit exceeded")
            details["daily_loss"] = f"${daily_pnl:.2f}"
        
        # Check weekly loss limit
        if weekly_pnl < -risk_profile.weekly_loss_limit:
            errors.append("Weekly loss limit exceeded")
            details["weekly_loss"] = f"${weekly_pnl:.2f}"
        
        # Check monthly loss limit
        if monthly_pnl < -risk_profile.monthly_loss_limit:
            errors.append("Monthly loss limit exceeded")
            details["monthly_loss"] = f"${monthly_pnl:.2f}"
        
        # Check total loss limit
        if total_pnl < -risk_profile.total_loss_limit:
            errors.append("Total loss limit exceeded")
            details["total_loss"] = f"${total_pnl:.2f}"
        
        return {
            "allowed": len(errors) == 0,
            "errors": errors,
            "details": details
        }
    
    def _check_volatility(self, risk_profile: RiskProfile, trade_request: RiskCheckRequest) -> Dict[str, Any]:
        """Check volatility limits"""
        # Mock data - in real app, this would calculate actual volatility
        current_volatility = 25.0
        
        warnings = []
        details = {}
        
        if current_volatility > risk_profile.max_volatility_threshold:
            warnings.append("High volatility detected")
            details["volatility"] = f"{current_volatility:.1f}%"
        
        return {
            "allowed": True,  # Volatility is a warning, not a blocker
            "warnings": warnings,
            "details": details
        }
    
    def _calculate_risk_score(self, risk_profile: RiskProfile, trade_request: RiskCheckRequest, risk_factors: Dict[str, Any]) -> float:
        """Calculate a risk score (0-100, lower is better)"""
        base_score = 50.0
        
        # Adjust based on risk factors
        if "trading_hours" in risk_factors:
            base_score += 20
        
        if "position_limits" in risk_factors:
            base_score += 15
        
        if "loss_limits" in risk_factors:
            base_score += 25
        
        if "volatility" in risk_factors:
            base_score += 10
        
        # Adjust based on trade size relative to limits
        if trade_request.price:
            trade_value = trade_request.quantity * trade_request.price
            if trade_value > risk_profile.max_position_size * 0.8:
                base_score += 10
        
        return min(100.0, max(0.0, base_score))
    
    def _suggest_quantity(self, risk_profile: RiskProfile, trade_request: RiskCheckRequest) -> Optional[float]:
        """Suggest a safer quantity based on risk limits"""
        if not trade_request.price:
            return None
        
        max_value = risk_profile.max_position_size * 0.8  # 80% of max position size
        suggested_quantity = max_value / trade_request.price
        
        return min(suggested_quantity, trade_request.quantity)
    
    def _suggest_price(self, risk_profile: RiskProfile, trade_request: RiskCheckRequest) -> Optional[float]:
        """Suggest a safer price based on risk limits"""
        if trade_request.order_type == "market":
            return None
        
        # For limit orders, suggest adding some buffer
        if trade_request.side == "buy":
            return trade_request.price * 0.98 if trade_request.price else None
        else:
            return trade_request.price * 1.02 if trade_request.price else None
    
    def _calculate_risk_level(self, daily_pnl_percent: float, weekly_pnl_percent: float, monthly_pnl_percent: float) -> str:
        """Calculate current risk level based on P&L"""
        if daily_pnl_percent < -5 or weekly_pnl_percent < -15 or monthly_pnl_percent < -25:
            return "critical"
        elif daily_pnl_percent < -3 or weekly_pnl_percent < -10 or monthly_pnl_percent < -20:
            return "high"
        elif daily_pnl_percent < -1 or weekly_pnl_percent < -5 or monthly_pnl_percent < -10:
            return "medium"
        else:
            return "low"