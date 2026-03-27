#!/usr/bin/env python3
"""
Test script for memory-enabled returns agent.

This script tests if the agent can recall customer preferences and history from memory.
"""

import json
import importlib.util
import sys

# Load memory configuration
with open('memory_config.json') as f:
    memory_config = json.load(f)
    memory_id = memory_config['memory_id']

print("="*80)
print("MEMORY-ENABLED AGENT TEST")
print("="*80)
print(f"Memory ID: {memory_id}")
print(f"Customer ID: user_001")
print(f"Session ID: test-session-001")
print()

# Import the memory-enabled agent
print("Loading memory-enabled agent...")
spec = importlib.util.spec_from_file_location("memory_agent", "06_memory_enabled_agent.py")
memory_agent = importlib.util.module_from_spec(spec)
sys.modules["memory_agent"] = memory_agent
spec.loader.exec_module(memory_agent)
print("✓ Agent loaded successfully")
print()

# Test query
test_query = "Hi! I'm thinking about returning something. What do you remember about my preferences?"

print("="*80)
print("TEST QUERY:")
print("="*80)
print(f'"{test_query}"')
print()

print("="*80)
print("AGENT RESPONSE:")
print("="*80)

# Run the agent with user_001 as the actor
try:
    response = memory_agent.run_agent(
        user_input=test_query,
        session_id="test-session-001",
        actor_id="user_001"
    )
    print(response)
    print()
    
    print("="*80)
    print("MEMORY RECALL CHECK:")
    print("="*80)
    
    # Check if the agent mentioned key information from seeded memory
    response_lower = response.lower()
    
    checks = {
        "Email preferences": "email" in response_lower,
        "Past laptop return": "laptop" in response_lower or "defective" in response_lower,
        "Electronics knowledge": "electronics" in response_lower or "30" in response_lower or "return window" in response_lower
    }
    
    print("Expected memories from seeded conversations:")
    for check_name, found in checks.items():
        status = "✓" if found else "✗"
        print(f"  {status} {check_name}: {'Recalled' if found else 'Not mentioned'}")
    
    print()
    if all(checks.values()):
        print("🎉 SUCCESS: Agent successfully recalled customer information from memory!")
    elif any(checks.values()):
        print("⚠️  PARTIAL: Agent recalled some but not all customer information")
    else:
        print("⚠️  NOTE: Agent may not have recalled specific details")
        print("   This could mean:")
        print("   - Memory processing is still in progress (takes 20-30 seconds)")
        print("   - Memory retrieval didn't find relevant matches")
        print("   - Run 04_seed_memory.py first if you haven't already")
    
except Exception as e:
    print(f"❌ Error running agent: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
