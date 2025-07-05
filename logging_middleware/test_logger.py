#!/usr/bin/env python3
"""
Test script for the Logging Middleware
Tests various scenarios including valid and invalid inputs
"""

import sys
import os
import time

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger import Log, log_info, log_error, log_warn, log_debug, log_fatal

def test_valid_logs():
    """Test valid logging scenarios."""
    print("=== Testing Valid Logs ===")
    
    # Test backend logs
    print("\n1. Testing Backend Logs:")
    
    # Database operations
    result = Log("backend", "info", "db", "Database connection established successfully", 
                connection_id="conn_123", db_name="url_shortener")
    print(f"DB Info Log: {'✓' if result else '✗'}")
    
    result = Log("backend", "error", "db", "Database query failed", 
                query="SELECT * FROM urls", error_code="DB_001")
    print(f"DB Error Log: {'✓' if result else '✗'}")
    
    # Handler operations
    result = Log("backend", "info", "handler", "URL shortening request received", 
                url_length=45, user_ip="192.168.1.1")
    print(f"Handler Info Log: {'✓' if result else '✗'}")
    
    result = Log("backend", "error", "handler", "Invalid URL format received", 
                received_url="not-a-url", expected_format="https://...")
    print(f"Handler Error Log: {'✓' if result else '✗'}")
    
    # Service operations
    result = Log("backend", "info", "service", "URL shortener service started", 
                port=5000, host="localhost")
    print(f"Service Info Log: {'✓' if result else '✗'}")
    
    result = Log("backend", "warn", "service", "High memory usage detected", 
                memory_usage="85%", threshold="80%")
    print(f"Service Warning Log: {'✓' if result else '✗'}")
    
    # Route operations
    result = Log("backend", "debug", "route", "Route handler called", 
                method="POST", endpoint="/shorturls")
    print(f"Route Debug Log: {'✓' if result else '✗'}")
    
    # Fatal error
    result = Log("backend", "fatal", "db", "Critical database connection failure", 
                error="Connection timeout", retry_count=3)
    print(f"Fatal Log: {'✓' if result else '✗'}")

def test_frontend_logs():
    """Test frontend logging scenarios."""
    print("\n2. Testing Frontend Logs:")
    
    # API operations
    result = Log("frontend", "info", "api", "API request sent to backend", 
                endpoint="/shorturls", method="POST")
    print(f"API Info Log: {'✓' if result else '✗'}")
    
    result = Log("frontend", "error", "api", "API request failed", 
                status_code=500, error_message="Internal server error")
    print(f"API Error Log: {'✓' if result else '✗'}")
    
    # Component operations
    result = Log("frontend", "info", "components", "URL form component rendered", 
                component_name="UrlShortenerForm")
    print(f"Component Info Log: {'✓' if result else '✗'}")
    
    result = Log("frontend", "warn", "components", "Component state update failed", 
                component="UrlsList", state_property="urls")
    print(f"Component Warning Log: {'✓' if result else '✗'}")
    
    # Page operations
    result = Log("frontend", "info", "page", "Page navigation occurred", 
                from_page="Create URL", to_page="Manage URLs")
    print(f"Page Info Log: {'✓' if result else '✗'}")
    
    # State operations
    result = Log("frontend", "debug", "state", "Application state updated", 
                action="SET_URLS", payload_size=2)
    print(f"State Debug Log: {'✓' if result else '✗'}")

def test_shared_packages():
    """Test shared package logging."""
    print("\n3. Testing Shared Packages:")
    
    # Auth operations
    result = Log("backend", "info", "auth", "User authentication successful", 
                user_id="user_123", method="token")
    print(f"Backend Auth Log: {'✓' if result else '✗'}")
    
    result = Log("frontend", "error", "auth", "Authentication token expired", 
                token_age="2h", max_age="1h")
    print(f"Frontend Auth Log: {'✓' if result else '✗'}")
    
    # Utils operations
    result = Log("backend", "debug", "utils", "URL validation utility called", 
                input_url="https://example.com", is_valid=True)
    print(f"Backend Utils Log: {'✓' if result else '✗'}")
    
    result = Log("frontend", "info", "utils", "Date formatting utility used", 
                input_date="2025-07-05T10:30:00Z", format="local")
    print(f"Frontend Utils Log: {'✓' if result else '✗'}")
    
    # Config operations
    result = Log("backend", "info", "config", "Configuration loaded", 
                config_file="app.py", env="development")
    print(f"Backend Config Log: {'✓' if result else '✗'}")
    
    result = Log("frontend", "warn", "config", "Configuration validation warning", 
                missing_key="API_TIMEOUT", default_value=5000)
    print(f"Frontend Config Log: {'✓' if result else '✗'}")

def test_convenience_functions():
    """Test convenience functions."""
    print("\n4. Testing Convenience Functions:")
    
    result = log_info("backend", "service", "Service health check", status="healthy")
    print(f"log_info: {'✓' if result else '✗'}")
    
    result = log_error("frontend", "api", "Network request timeout", timeout_ms=5000)
    print(f"log_error: {'✓' if result else '✗'}")
    
    result = log_warn("backend", "db", "Database connection pool running low", 
                     available_connections=2, min_connections=5)
    print(f"log_warn: {'✓' if result else '✗'}")
    
    result = log_debug("frontend", "components", "Component re-render triggered", 
                      component="UrlForm", reason="state_change")
    print(f"log_debug: {'✓' if result else '✗'}")
    
    result = log_fatal("backend", "db", "Database corruption detected", 
                      table="urls", corruption_type="index")
    print(f"log_fatal: {'✓' if result else '✗'}")

def test_invalid_inputs():
    """Test invalid input handling."""
    print("\n5. Testing Invalid Inputs:")
    
    # Invalid stack
    result = Log("invalid_stack", "info", "db", "This should fail")
    print(f"Invalid stack: {'✗' if result is None else '✓'}")
    
    # Invalid level
    result = Log("backend", "invalid_level", "db", "This should fail")
    print(f"Invalid level: {'✗' if result is None else '✓'}")
    
    # Invalid package for backend
    result = Log("backend", "info", "components", "This should fail")
    print(f"Invalid backend package: {'✗' if result is None else '✓'}")
    
    # Invalid package for frontend
    result = Log("frontend", "info", "db", "This should fail")
    print(f"Invalid frontend package: {'✗' if result is None else '✓'}")

def test_performance():
    """Test logging performance."""
    print("\n6. Testing Performance:")
    
    start_time = time.time()
    successful_logs = 0
    total_logs = 10
    
    for i in range(total_logs):
        result = Log("backend", "info", "service", f"Performance test log {i+1}", 
                    test_number=i+1, timestamp=time.time())
        if result:
            successful_logs += 1
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"Total logs: {total_logs}")
    print(f"Successful logs: {successful_logs}")
    print(f"Failed logs: {total_logs - successful_logs}")
    print(f"Total time: {elapsed_time:.3f} seconds")
    print(f"Average time per log: {elapsed_time/total_logs:.3f} seconds")
    print(f"Success rate: {(successful_logs/total_logs)*100:.1f}%")

def main():
    """Run all tests."""
    print("🚀 Starting Logging Middleware Tests")
    print("=" * 50)
    
    try:
        test_valid_logs()
        time.sleep(1)  # Small delay between test sections
        
        test_frontend_logs()
        time.sleep(1)
        
        test_shared_packages()
        time.sleep(1)
        
        test_convenience_functions()
        time.sleep(1)
        
        test_invalid_inputs()
        time.sleep(1)
        
        test_performance()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("Check the logging_middleware.log file for detailed logs.")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 