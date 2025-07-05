#!/usr/bin/env python3
"""
Simple test script for the Logging Middleware
"""

import sys
import os

# Add the logging middleware to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'logging_middleware'))

try:
    from logger import Log, log_info, log_error
    
    print("✅ Logging middleware imported successfully")
    
    # Test a simple log
    print("\n📝 Testing basic logging...")
    result = Log("backend", "info", "test", "Testing logging middleware")
    if result:
        print(f"✅ Log sent successfully: {result}")
    else:
        print("❌ Log failed to send")
    
    # Test error logging
    print("\n📝 Testing error logging...")
    result = log_error("frontend", "api", "Test error message", error_code="TEST_001")
    if result:
        print(f"✅ Error log sent successfully: {result}")
    else:
        print("❌ Error log failed to send")
    
    # Test info logging
    print("\n📝 Testing info logging...")
    result = log_info("backend", "service", "Service test message", service_name="test_service")
    if result:
        print(f"✅ Info log sent successfully: {result}")
    else:
        print("❌ Info log failed to send")
    
    print("\n🎉 All tests completed!")
    
except ImportError as e:
    print(f"❌ Failed to import logging middleware: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1) 