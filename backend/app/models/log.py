from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid

class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Log metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger_name = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # Source information
    module = Column(String(100), nullable=True)
    function = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    process_id = Column(Integer, nullable=True)
    thread_id = Column(Integer, nullable=True)
    
    # Context information
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey('strategies.id'), nullable=True, index=True)
    trade_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    exchange = Column(String(50), nullable=True, index=True)
    symbol = Column(String(20), nullable=True, index=True)
    
    # Additional data
    extra_data = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="log_entries")
    strategy = relationship("Strategy", back_populates="log_entries")
    
    def __repr__(self):
        return f"<LogEntry(id={self.id}, level='{self.level}', message='{self.message[:50]}...')>"
    
    def to_dict(self):
        """Convert log entry to dictionary"""
        return {
            'id': str(self.id),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'level': self.level,
            'logger_name': self.logger_name,
            'message': self.message,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'process_id': self.process_id,
            'thread_id': self.thread_id,
            'user_id': str(self.user_id) if self.user_id else None,
            'strategy_id': str(self.strategy_id) if self.strategy_id else None,
            'trade_id': str(self.trade_id) if self.trade_id else None,
            'exchange': self.exchange,
            'symbol': self.symbol,
            'extra_data': self.extra_data
        }
    
    @classmethod
    def get_logs_by_user(cls, db, user_id: str, limit: int = 100):
        """Get logs for a specific user"""
        return db.query(cls).filter(
            cls.user_id == user_id
        ).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_level(cls, db, level: str, limit: int = 100):
        """Get logs by severity level"""
        return db.query(cls).filter(
            cls.level == level.upper()
        ).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_strategy(cls, db, strategy_id: str, limit: int = 100):
        """Get logs for a specific strategy"""
        return db.query(cls).filter(
            cls.strategy_id == strategy_id
        ).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_exchange(cls, db, exchange: str, limit: int = 100):
        """Get logs for a specific exchange"""
        return db.query(cls).filter(
            cls.exchange == exchange
        ).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_symbol(cls, db, symbol: str, limit: int = 100):
        """Get logs for a specific trading symbol"""
        return db.query(cls).filter(
            cls.symbol == symbol
        ).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_time_range(cls, db, start_time, end_time, limit: int = 100):
        """Get logs within a time range"""
        return db.query(cls).filter(
            cls.timestamp >= start_time,
            cls.timestamp <= end_time
        ).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def cleanup_old_logs(cls, db, days_to_keep: int = 30):
        """Clean up old log entries"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = db.query(cls).filter(
            cls.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        return deleted_count