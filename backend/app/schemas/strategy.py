from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class StrategyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., regex="^(grid|mean_reversion|momentum)$")
    config: Dict[str, Any]

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, regex="^(grid|mean_reversion|momentum)$")
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class StrategyInDB(StrategyBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Strategy(StrategyInDB):
    pass

class StrategyStatus(BaseModel):
    id: str
    name: str
    type: str
    status: str
    is_running: bool
    last_execution: Optional[datetime]
    total_trades: int
    total_pnl: float
    config: Dict[str, Any]

class StrategyInfo(BaseModel):
    name: str
    description: str
    type: str
    parameters: List[Dict[str, str]]

class StrategyList(BaseModel):
    strategies: List[Strategy]
    total: int

class StrategyAction(BaseModel):
    action: str = Field(..., regex="^(start|stop|pause|resume)$")

class StrategyConfigUpdate(BaseModel):
    config: Dict[str, Any]

class StrategyMetrics(BaseModel):
    strategy_id: str
    metrics: Dict[str, Any]
    timestamp: datetime