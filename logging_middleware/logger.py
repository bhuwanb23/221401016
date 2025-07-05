import requests
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
import logging

class LoggingMiddleware:
    """
    A comprehensive logging middleware that sends logs to the evaluation service.
    Supports all required stacks, levels, and packages with proper validation.
    """
    
    def __init__(self, api_url: str = "http://20.244.56.144/evaluation-service/logs"):
        self.api_url = api_url
        self.session = requests.Session()
        
        # Configure session headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'LoggingMiddleware/1.0'
        })
        
        # Valid values for validation
        self.valid_stacks = {"backend", "frontend"}
        self.valid_levels = {"debug", "info", "warn", "error", "fatal"}
        self.valid_backend_packages = {
            "cache", "controller", "cron_job", "db", "domain", 
            "handler", "respoistory", "route", "service"
        }
        self.valid_frontend_packages = {
            "api", "components", "hooks", "page", "state", "style"
        }
        self.valid_shared_packages = {
            "auth", "config", "middleware", "utils"
        }
        
        # Setup local logging for debugging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logging_middleware.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _validate_stack(self, stack: str) -> bool:
        """Validate the stack parameter."""
        if stack.lower() not in self.valid_stacks:
            self.logger.error(f"Invalid stack: {stack}. Valid values: {self.valid_stacks}")
            return False
        return True
    
    def _validate_level(self, level: str) -> bool:
        """Validate the level parameter."""
        if level.lower() not in self.valid_levels:
            self.logger.error(f"Invalid level: {level}. Valid values: {self.valid_levels}")
            return False
        return True
    
    def _validate_package(self, package: str, stack: str) -> bool:
        """Validate the package parameter based on stack."""
        package_lower = package.lower()
        
        if stack.lower() == "backend":
            valid_packages = self.valid_backend_packages | self.valid_shared_packages
        elif stack.lower() == "frontend":
            valid_packages = self.valid_frontend_packages | self.valid_shared_packages
        else:
            self.logger.error(f"Invalid stack for package validation: {stack}")
            return False
        
        if package_lower not in valid_packages:
            self.logger.error(f"Invalid package '{package}' for stack '{stack}'. Valid packages: {valid_packages}")
            return False
        return True
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format the message with additional context if provided."""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | Context: {context}"
        return message
    
    def log(self, stack: str, level: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Send a log entry to the evaluation service.
        
        Args:
            stack: "backend" or "frontend"
            level: "debug", "info", "warn", "error", or "fatal"
            package: Valid package for the given stack
            message: Log message
            **kwargs: Additional context to include in the message
        
        Returns:
            Response data if successful, None if failed
        """
        try:
            # Validate inputs
            if not self._validate_stack(stack):
                return None
            if not self._validate_level(level):
                return None
            if not self._validate_package(package, stack):
                return None
            
            # Format message with context
            formatted_message = self._format_message(message, **kwargs)
            
            # Prepare request payload
            payload = {
                "stack": stack.lower(),
                "level": level.lower(),
                "package": package.lower(),
                "message": formatted_message
            }
            
            # Make API call
            start_time = time.time()
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            elapsed_time = time.time() - start_time
            
            # Log the API call locally for debugging
            self.logger.info(f"Log API call - Status: {response.status_code}, Time: {elapsed_time:.3f}s")
            
            if response.status_code == 200:
                response_data = response.json()
                self.logger.info(f"Log created successfully - ID: {response_data.get('logID', 'N/A')}")
                return response_data
            else:
                self.logger.error(f"Log API failed - Status: {response.status_code}, Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error("Log API call timed out")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Log API request failed: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in logging middleware: {str(e)}")
            return None
    
    def debug(self, stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log a debug message."""
        return self.log(stack, "debug", package, message, **kwargs)
    
    def info(self, stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log an info message."""
        return self.log(stack, "info", package, message, **kwargs)
    
    def warn(self, stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log a warning message."""
        return self.log(stack, "warn", package, message, **kwargs)
    
    def error(self, stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log an error message."""
        return self.log(stack, "error", package, message, **kwargs)
    
    def fatal(self, stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log a fatal message."""
        return self.log(stack, "fatal", package, message, **kwargs)

# Global logger instance
logger = LoggingMiddleware()

# Convenience functions for easy usage
def Log(stack: str, level: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Convenience function to log messages.
    
    Args:
        stack: "backend" or "frontend"
        level: "debug", "info", "warn", "error", or "fatal"
        package: Valid package for the given stack
        message: Log message
        **kwargs: Additional context
    
    Returns:
        Response data if successful, None if failed
    """
    return logger.log(stack, level, package, message, **kwargs)

def log_debug(stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log a debug message."""
    return logger.debug(stack, package, message, **kwargs)

def log_info(stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log an info message."""
    return logger.info(stack, package, message, **kwargs)

def log_warn(stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log a warning message."""
    return logger.warn(stack, package, message, **kwargs)

def log_error(stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log an error message."""
    return logger.error(stack, package, message, **kwargs)

def log_fatal(stack: str, package: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log a fatal message."""
    return logger.fatal(stack, package, message, **kwargs) 