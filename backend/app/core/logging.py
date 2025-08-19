import logging
import logging.handlers
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.log import LogEntry

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread,
        }
        
        # Add extra fields if they exist
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'strategy_id'):
            log_entry['strategy_id'] = record.strategy_id
        if hasattr(record, 'trade_id'):
            log_entry['trade_id'] = record.trade_id
        if hasattr(record, 'exchange'):
            log_entry['exchange'] = record.exchange
        if hasattr(record, 'symbol'):
            log_entry['symbol'] = record.symbol
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class DatabaseHandler(logging.Handler):
    """Custom handler to store logs in database"""
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            # Get database session
            db = next(get_db())
            
            # Create log entry
            log_entry = LogEntry(
                level=record.levelname,
                logger_name=record.name,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                line_number=record.lineno,
                process_id=record.process,
                thread_id=record.thread,
                user_id=getattr(record, 'user_id', None),
                strategy_id=getattr(record, 'strategy_id', None),
                trade_id=getattr(record, 'trade_id', None),
                exchange=getattr(record, 'exchange', None),
                symbol=getattr(record, 'symbol', None),
                extra_data=self._extract_extra_data(record)
            )
            
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            # Fallback to console if database logging fails
            sys.stderr.write(f"Database logging failed: {e}\n")
            sys.stderr.write(f"Original log: {record.getMessage()}\n")

    def _extract_extra_data(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract extra data from log record"""
        extra_data = {}
        
        # Get all attributes that aren't standard logging attributes
        standard_attrs = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process', 'getMessage',
            'exc_info', 'exc_text', 'stack_info', 'user_id', 'strategy_id',
            'trade_id', 'exchange', 'symbol'
        }
        
        for attr in dir(record):
            if not attr.startswith('_') and attr not in standard_attrs:
                try:
                    value = getattr(record, attr)
                    if value is not None:
                        extra_data[attr] = str(value)
                except:
                    pass
        
        return extra_data

class TradingLogger:
    """Main logging class for the trading platform"""
    
    def __init__(self, name: str = "trading_platform"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Console handler with structured formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = StructuredFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all logs
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "trading_platform.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = StructuredFormatter()
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
        
        # Database handler for critical logs
        db_handler = DatabaseHandler()
        db_handler.setLevel(logging.WARNING)
        self.logger.addHandler(db_handler)
        
        # Trading-specific file handler
        trading_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "trading.log",
            maxBytes=20*1024*1024,  # 20MB
            backupCount=10
        )
        trading_handler.setLevel(logging.INFO)
        trading_formatter = StructuredFormatter()
        trading_handler.setFormatter(trading_formatter)
        self.logger.addHandler(trading_handler)
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with additional context"""
        extra = {}
        for key, value in kwargs.items():
            if value is not None:
                extra[key] = value
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def trade(self, message: str, **kwargs):
        """Log trade-specific message"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def strategy(self, message: str, **kwargs):
        """Log strategy-specific message"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def risk(self, message: str, **kwargs):
        """Log risk-related message"""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def exchange(self, message: str, **kwargs):
        """Log exchange-related message"""
        self._log_with_context(logging.INFO, message, **kwargs)

# Global logger instance
logger = TradingLogger()

# Convenience functions
def log_trade(message: str, user_id: Optional[str] = None, 
              strategy_id: Optional[str] = None, trade_id: Optional[str] = None,
              exchange: Optional[str] = None, symbol: Optional[str] = None):
    """Log trade-related message"""
    logger.trade(message, user_id=user_id, strategy_id=strategy_id, 
                trade_id=trade_id, exchange=exchange, symbol=symbol)

def log_strategy(message: str, user_id: Optional[str] = None,
                strategy_id: Optional[str] = None, symbol: Optional[str] = None):
    """Log strategy-related message"""
    logger.strategy(message, user_id=user_id, strategy_id=strategy_id, symbol=symbol)

def log_risk(message: str, user_id: Optional[str] = None,
             strategy_id: Optional[str] = None, severity: str = "medium"):
    """Log risk-related message"""
    logger.risk(message, user_id=user_id, strategy_id=strategy_id, severity=severity)

def log_exchange(message: str, exchange: str, symbol: Optional[str] = None):
    """Log exchange-related message"""
    logger.exchange(message, exchange=exchange, symbol=symbol)
