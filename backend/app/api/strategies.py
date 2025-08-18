from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.strategy import (
    StrategyCreate, StrategyUpdate, Strategy, StrategyStatus,
    StrategyAction, StrategyConfigUpdate, StrategyInfo
)
from app.services.strategy_manager import strategy_manager
from app.strategies.factory import StrategyFactory
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.strategy import Strategy as StrategyModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.get("/", response_model=List[Strategy])
async def get_strategies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all strategies for the current user"""
    try:
        strategies = db.query(StrategyModel).filter(
            StrategyModel.user_id == current_user.id
        ).all()
        
        return [strategy.to_dict() for strategy in strategies]
        
    except Exception as e:
        logger.error(f"Error fetching strategies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/available", response_model=List[StrategyInfo])
async def get_available_strategies():
    """Get list of available strategy types"""
    try:
        return StrategyFactory.get_available_strategies()
        
    except Exception as e:
        logger.error(f"Error fetching available strategies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{strategy_id}", response_model=Strategy)
async def get_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific strategy by ID"""
    try:
        strategy = db.query(StrategyModel).filter(
            StrategyModel.id == strategy_id,
            StrategyModel.user_id == current_user.id
        ).first()
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )
        
        return strategy.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategy {strategy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=Strategy, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_create: StrategyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new strategy"""
    try:
        # Validate strategy configuration
        default_config = StrategyFactory.get_default_config(strategy_create.type)
        if not default_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid strategy type"
            )
        
        # Merge with default config
        config = {**default_config, **strategy_create.config}
        
        # Create strategy instance to validate config
        strategy = StrategyFactory.create_strategy(
            strategy_create.type,
            config,
            str(current_user.id)
        )
        
        if not strategy or not strategy.validate_config():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid strategy configuration"
            )
        
        # Create database record
        db_strategy = StrategyModel(
            name=strategy_create.name,
            type=strategy_create.type,
            user_id=current_user.id,
            config=config
        )
        
        db.add(db_strategy)
        db.commit()
        db.refresh(db_strategy)
        
        logger.info(f"Strategy created: {db_strategy.name} for user {current_user.id}")
        return db_strategy.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{strategy_id}", response_model=Strategy)
async def update_strategy(
    strategy_id: str,
    strategy_update: StrategyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a strategy"""
    try:
        strategy = db.query(StrategyModel).filter(
            StrategyModel.id == strategy_id,
            StrategyModel.user_id == current_user.id
        ).first()
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )
        
        # Update fields
        update_data = strategy_update.dict(exclude_unset=True)
        
        if 'config' in update_data:
            # Validate new configuration
            temp_strategy = StrategyFactory.create_strategy(
                strategy.type,
                update_data['config'],
                str(current_user.id)
            )
            
            if not temp_strategy or not temp_strategy.validate_config():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid strategy configuration"
                )
        
        for field, value in update_data.items():
            setattr(strategy, field, value)
        
        db.commit()
        db.refresh(strategy)
        
        logger.info(f"Strategy updated: {strategy.name}")
        return strategy.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating strategy {strategy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a strategy"""
    try:
        strategy = db.query(StrategyModel).filter(
            StrategyModel.id == strategy_id,
            StrategyModel.user_id == current_user.id
        ).first()
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )
        
        # Stop if running
        if strategy.is_active:
            await strategy_manager.stop_strategy(strategy_id, str(current_user.id))
        
        db.delete(strategy)
        db.commit()
        
        logger.info(f"Strategy deleted: {strategy.name}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting strategy {strategy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{strategy_id}/action")
async def control_strategy(
    strategy_id: str,
    action: StrategyAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Control strategy (start/stop/pause/resume)"""
    try:
        # Verify strategy exists and belongs to user
        strategy = db.query(StrategyModel).filter(
            StrategyModel.id == strategy_id,
            StrategyModel.user_id == current_user.id
        ).first()
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found"
            )
        
        success = False
        
        if action.action == "start":
            success = await strategy_manager.start_strategy(db, strategy_id, str(current_user.id))
            if success:
                strategy.is_active = True
                db.commit()
                
        elif action.action == "stop":
            success = await strategy_manager.stop_strategy(strategy_id, str(current_user.id))
            if success:
                strategy.is_active = False
                db.commit()
                
        elif action.action == "pause":
            success = await strategy_manager.pause_strategy(strategy_id, str(current_user.id))
            
        elif action.action == "resume":
            success = await strategy_manager.resume_strategy(strategy_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to {action.action} strategy"
            )
        
        return {"message": f"Strategy {action.action}ed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error controlling strategy {strategy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{strategy_id}/status", response_model=StrategyStatus)
async def get_strategy_status(
    strategy_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get strategy execution status"""
    try:
        status = await strategy_manager.get_strategy_status(strategy_id, str(current_user.id))
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategy not found or not running"
            )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting strategy status {strategy_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{strategy_id}/config/default")
async def get_default_config(strategy_type: str):
    """Get default configuration for a strategy type"""
    try:
        config = StrategyFactory.get_default_config(strategy_type)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid strategy type"
            )
        
        return {"config": config}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting default config for {strategy_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )