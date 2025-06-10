"""
Logging decorators for FastAPI application.
"""
import time
import functools
from typing import Any, Callable, Optional
import asyncio
import inspect

from app.core.logging_config import get_logger, performance_logger


def log_function_call(
    logger_name: Optional[str] = None,
    log_args: bool = True,
    log_result: bool = True,
    log_duration: bool = True,
    level: str = "INFO"
):
    """
    Decorator to log function calls with arguments, results, and duration.
    
    Args:
        logger_name: Name of the logger to use (defaults to module name)
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        log_duration: Whether to log execution duration
        level: Log level to use
    """
    def decorator(func: Callable) -> Callable:
        # Get logger
        if logger_name:
            logger = get_logger(logger_name)
        else:
            logger = get_logger(func.__module__.split('.')[-1])
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            # Log function entry
            log_data = {
                "function": func.__name__,
                "module": func.__module__,
                "event_type": "function_entry"
            }
            
            if log_args:
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Filter out sensitive arguments
                safe_args = {}
                for name, value in bound_args.arguments.items():
                    if any(sensitive in name.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                        safe_args[name] = "[REDACTED]"
                    else:
                        safe_args[name] = str(value)[:200]  # Limit length
                
                log_data["arguments"] = safe_args
            
            logger.log(
                getattr(logging, level.upper()),
                f"Entering function: {func.__name__}",
                extra=log_data
            )
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Log function exit
                exit_log_data = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "event_type": "function_exit",
                    "success": True
                }
                
                if log_duration:
                    exit_log_data["duration_ms"] = duration_ms
                
                if log_result and result is not None:
                    # Safely log result (avoid logging sensitive data)
                    if isinstance(result, (str, int, float, bool)):
                        exit_log_data["result"] = str(result)[:200]
                    elif isinstance(result, (list, tuple)):
                        exit_log_data["result_type"] = type(result).__name__
                        exit_log_data["result_length"] = len(result)
                    elif isinstance(result, dict):
                        exit_log_data["result_type"] = "dict"
                        exit_log_data["result_keys"] = list(result.keys())[:10]
                    else:
                        exit_log_data["result_type"] = type(result).__name__
                
                logger.log(
                    getattr(logging, level.upper()),
                    f"Exiting function: {func.__name__} (duration: {duration_ms:.2f}ms)",
                    extra=exit_log_data
                )
                
                return result
                
            except Exception as exc:
                # Calculate duration for failed calls
                duration_ms = (time.time() - start_time) * 1000
                
                # Log function error
                error_log_data = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "event_type": "function_error",
                    "success": False,
                    "duration_ms": duration_ms,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc)
                }
                
                logger.error(
                    f"Function failed: {func.__name__} - {type(exc).__name__}: {str(exc)}",
                    extra=error_log_data,
                    exc_info=True
                )
                
                raise exc
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            # Log function entry (similar to async version)
            log_data = {
                "function": func.__name__,
                "module": func.__module__,
                "event_type": "function_entry"
            }
            
            if log_args:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                safe_args = {}
                for name, value in bound_args.arguments.items():
                    if any(sensitive in name.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                        safe_args[name] = "[REDACTED]"
                    else:
                        safe_args[name] = str(value)[:200]
                
                log_data["arguments"] = safe_args
            
            logger.log(
                getattr(logging, level.upper()),
                f"Entering function: {func.__name__}",
                extra=log_data
            )
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                exit_log_data = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "event_type": "function_exit",
                    "success": True
                }
                
                if log_duration:
                    exit_log_data["duration_ms"] = duration_ms
                
                if log_result and result is not None:
                    if isinstance(result, (str, int, float, bool)):
                        exit_log_data["result"] = str(result)[:200]
                    elif isinstance(result, (list, tuple)):
                        exit_log_data["result_type"] = type(result).__name__
                        exit_log_data["result_length"] = len(result)
                    elif isinstance(result, dict):
                        exit_log_data["result_type"] = "dict"
                        exit_log_data["result_keys"] = list(result.keys())[:10]
                    else:
                        exit_log_data["result_type"] = type(result).__name__
                
                logger.log(
                    getattr(logging, level.upper()),
                    f"Exiting function: {func.__name__} (duration: {duration_ms:.2f}ms)",
                    extra=exit_log_data
                )
                
                return result
                
            except Exception as exc:
                duration_ms = (time.time() - start_time) * 1000
                
                error_log_data = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "event_type": "function_error",
                    "success": False,
                    "duration_ms": duration_ms,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc)
                }
                
                logger.error(
                    f"Function failed: {func.__name__} - {type(exc).__name__}: {str(exc)}",
                    extra=error_log_data,
                    exc_info=True
                )
                
                raise exc
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_performance(threshold_ms: float = 1000.0, logger_name: Optional[str] = None):
    """
    Decorator to log performance warnings for slow functions.
    
    Args:
        threshold_ms: Threshold in milliseconds to trigger performance warning
        logger_name: Name of the logger to use
    """
    def decorator(func: Callable) -> Callable:
        if logger_name:
            logger = get_logger(logger_name)
        else:
            logger = get_logger("performance")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            if duration_ms > threshold_ms:
                logger.warning(
                    f"Slow function detected: {func.__name__} took {duration_ms:.2f}ms",
                    extra={
                        "function": func.__name__,
                        "module": func.__module__,
                        "duration_ms": duration_ms,
                        "threshold_ms": threshold_ms,
                        "event_type": "slow_function"
                    }
                )
            
            # Also log to performance logger
            performance_logger.logger.info(
                f"Function performance: {func.__name__}",
                extra={
                    "function": func.__name__,
                    "module": func.__module__,
                    "duration": duration_ms
                }
            )
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            if duration_ms > threshold_ms:
                logger.warning(
                    f"Slow function detected: {func.__name__} took {duration_ms:.2f}ms",
                    extra={
                        "function": func.__name__,
                        "module": func.__module__,
                        "duration_ms": duration_ms,
                        "threshold_ms": threshold_ms,
                        "event_type": "slow_function"
                    }
                )
            
            performance_logger.logger.info(
                f"Function performance: {func.__name__}",
                extra={
                    "function": func.__name__,
                    "module": func.__module__,
                    "duration": duration_ms
                }
            )
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_errors(logger_name: Optional[str] = None, reraise: bool = True):
    """
    Decorator to log errors with detailed context.
    
    Args:
        logger_name: Name of the logger to use
        reraise: Whether to reraise the exception after logging
    """
    def decorator(func: Callable) -> Callable:
        if logger_name:
            logger = get_logger(logger_name)
        else:
            logger = get_logger("errors")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                logger.error(
                    f"Error in function {func.__name__}: {type(exc).__name__}: {str(exc)}",
                    extra={
                        "function": func.__name__,
                        "module": func.__module__,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "event_type": "function_error"
                    },
                    exc_info=True
                )
                
                if reraise:
                    raise exc
                return None
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                logger.error(
                    f"Error in function {func.__name__}: {type(exc).__name__}: {str(exc)}",
                    extra={
                        "function": func.__name__,
                        "module": func.__module__,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "event_type": "function_error"
                    },
                    exc_info=True
                )
                
                if reraise:
                    raise exc
                return None
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
