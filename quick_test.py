#!/usr/bin/env python3
"""
Quick test to verify authorization is working
"""

import sys
import os

# Add the logging middleware to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'logging_middleware'))

try:
    from logger import Log
    
    print("✅ Logging middleware imported successfully")
    
    # Test a simple log
    print("\n📝 Testing logging with authorization...")
    result = Log("backend", "info", "test", "Quick authorization test")
    
    if result:
        print(f"✅ Log sent successfully!")
        print("🎉 Authorization is working!")
    else:
        print("❌ Log failed to send")
    
    print("\n🎉 Test completed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc() 