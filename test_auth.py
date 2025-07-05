#!/usr/bin/env python3
"""
Test script to verify authorization is working with logging middleware
"""

import sys
import os

# Add the logging middleware to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'logging_middleware'))

try:
    from logger import Log, log_info, log_error
    
    print("✅ Logging middleware imported successfully")
    
    # Test a simple log with authorization
    print("\n📝 Testing logging with authorization...")
    result = Log("backend", "info", "test", "Testing logging middleware with auth")
    
    if result:
        print(f"✅ Log sent successfully: {result}")
        print("🎉 Authorization is working!")
    else:
        print("❌ Log failed to send - authorization issue")
    
    # Test error logging
    print("\n📝 Testing error logging...")
    result = log_error("frontend", "api", "Test error message", error_code="TEST_001")
    
    if result:
        print(f"✅ Error log sent successfully: {result}")
    else:
        print("❌ Error log failed to send")
    
    print("\n🎉 Authorization test completed!")
    
except ImportError as e:
    print(f"❌ Failed to import logging middleware: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1) 