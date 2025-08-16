import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(verbose: bool = False, log_file: str = None) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        verbose: Enable debug level logging
        log_file: Optional file path for logging output
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger('crypto_technicals')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def get_timestamped_filename(base_name: str, extension: str = '.log') -> str:
    """
    Generate a timestamped filename.
    
    Args:
        base_name: Base name for the file
        extension: File extension (default: .log)
    
    Returns:
        Timestamped filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{timestamp}{extension}"

def log_performance(func):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_performance
        def my_function():
            # function code
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('crypto_technicals')
        start_time = time.time()
        
        logger.debug(f"Starting execution of {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"Completed {func.__name__} in {duration:.2f} seconds")
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            logger.error(f"Failed {func.__name__} after {duration:.2f} seconds: {str(e)}")
            raise
    
    return wrapper