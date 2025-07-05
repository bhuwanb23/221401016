import requests
import json
import time
import os
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
        
        # Load authorization token
        self.auth_token = self._load_auth_token()
        
        # Configure session headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'LoggingMiddleware/1.0',
            'Authorization': f'Bearer {self.auth_token}'
        })
    
    def _load_auth_token(self):
        """Load authorization token from file or use default."""
        try:
            # Try to load from authorization file
            auth_file_path = os.path.join(os.path.dirname(__file__), '..', 'register', 'client_auth.txt')
            if os.path.exists(auth_file_path):
                with open(auth_file_path, 'r') as f:
                    content = f.read()
                    # Extract token from the file content
                    import re
                    token_match = re.search(r'"access_token":\s*"([^"]+)"', content)
                    if token_match:
                        return token_match.group(1)
            
            # Fallback to hardcoded token
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiIyMjE0MDEwMTZAcmFqYWxha3NobWkuZWR1LmluIiwiZXhwIjoxNzUxNjkzOTE3LCJpYXQiOjE3NTE2OTMwMTcsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiIxZDU4YmFlOC01NWM2LTQ4M2UtOTcwMy1lMDc1MWE5MmY2YzIiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJiaHV3YW4gYiIsInN1YiI6ImZkNjNmNmI0LTkzNjYtNGVlZS1hMTk2LTM1OTFmNzE1MDkxOCJ9LCJlbWFpbCI6IjIyMTQwMTAxNkByYWphbGFrc2htaS5lZHUuaW4iLCJuYW1lIjoiYmh1d2FuIGIiLCJyb2xsTm8iOiIyMjE0MDEwMTYiLCJhY2Nlc3NDb2RlIjoiY1d5YVhXIiwiY2xpZW50SUQiOiJmZDYzZjZiNC05MzY2LTRlZWUtYTE5Ni0zNTkxZjcxNTA5MTgiLCJjbGllbnRTZWNyZXQiOiJRR05XWndyZXpFakRiWlFnIn0.Gb7oKr3iaABMhbn80I0HJkgMcrywbDgkovbi-awy6zQ"
        except Exception as e:
            print(f"Failed to load auth token: {e}")
            # Return the hardcoded token as fallback
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiIyMjE0MDEwMTZAcmFqYWxha3NobWkuZWR1LmluIiwiZXhwIjoxNzUxNjkzOTE3LCJpYXQiOjE3NTE2OTMwMTcsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiIxZDU4YmFlOC01NWM2LTQ4M2UtOTcwMy1lMDc1MWE5MmY2YzIiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJiaHV3YW4gYiIsInN1YiI6ImZkNjNmNmI0LTkzNjYtNGVlZS1hMTk2LTM1OTFmNzE1MDkxOCJ9LCJlbWFpbCI6IjIyMTQwMTAxNkByYWphbGFrc2htaS5lZHUuaW4iLCJuYW1lIjoiYmh1d2FuIGIiLCJyb2xsTm8iOiIyMjE0MDEwMTYiLCJhY2Nlc3NDb2RlIjoiY1d5YVhXIiwiY2xpZW50SUQiOiJmZDYzZjZiNC05MzY2LTRlZWUtYTE5Ni0zNTkxZjcxNTA5MTgiLCJjbGllbnRTZWNyZXQiOiJRR05XWndyZXpFakRiWlFnIn0.Gb7oKr3iaABMhbn80I0HJkgMcrywbDgkovbi-awy6zQ"
    
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
    
    def _validate_package(self, package_name: str, stack: str) -> bool:
        """Validate the package parameter based on stack."""
        package_lower = package_name.lower()
        
        if stack.lower() == "backend":
            valid_packages = self.valid_backend_packages | self.valid_shared_packages
        elif stack.lower() == "frontend":
            valid_packages = self.valid_frontend_packages | self.valid_shared_packages
        else:
            self.logger.error(f"Invalid stack for package validation: {stack}")
            return False
        
        if package_lower not in valid_packages:
            self.logger.error(f"Invalid package '{package_name}' for stack '{stack}'. Valid packages: {valid_packages}")
            return False
        return True
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format the message with additional context if provided."""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | Context: {context}"
        return message
    
    def log(self, stack: str, level: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Send a log entry to the evaluation service.
        
        Args:
            stack: "backend" or "frontend"
            level: "debug", "info", "warn", "error", or "fatal"
            package_name: Valid package for the given stack
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
            if not self._validate_package(package_name, stack):
                return None
            
            # Format message with context
            formatted_message = self._format_message(message, **kwargs)
            
            # Prepare request payload
            payload = {
                "stack": stack.lower(),
                "level": level.lower(),
                "package": package_name.lower(),
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
    
    def debug(self, stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log a debug message."""
        return self.log(stack, "debug", package_name, message, **kwargs)
    
    def info(self, stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log an info message."""
        return self.log(stack, "info", package_name, message, **kwargs)
    
    def warn(self, stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log a warning message."""
        return self.log(stack, "warn", package_name, message, **kwargs)
    
    def error(self, stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log an error message."""
        return self.log(stack, "error", package_name, message, **kwargs)
    
    def fatal(self, stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Log a fatal message."""
        return self.log(stack, "fatal", package_name, message, **kwargs)

# Global logger instance
logger = LoggingMiddleware()

# Convenience functions for easy usage
def Log(stack: str, level: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Convenience function to log messages.
    
    Args:
        stack: "backend" or "frontend"
        level: "debug", "info", "warn", "error", or "fatal"
        package_name: Valid package for the given stack
        message: Log message
        **kwargs: Additional context
    
    Returns:
        Response data if successful, None if failed
    """
    return logger.log(stack, level, package_name, message, **kwargs)

def log_debug(stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log a debug message."""
    return logger.debug(stack, package_name, message, **kwargs)

def log_info(stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log an info message."""
    return logger.info(stack, package_name, message, **kwargs)

def log_warn(stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log a warning message."""
    return logger.warn(stack, package_name, message, **kwargs)

def log_error(stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log an error message."""
    return logger.error(stack, package_name, message, **kwargs)

def log_fatal(stack: str, package_name: str, message: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Log a fatal message."""
    return logger.fatal(stack, package_name, message, **kwargs) 