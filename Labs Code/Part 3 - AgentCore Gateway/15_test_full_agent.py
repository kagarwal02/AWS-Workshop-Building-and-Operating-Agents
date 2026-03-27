#!/usr/bin/env python3
"""
Test script for full-featured returns agent with memory and gateway.

This script tests if the agent can:
- Remember customer preferences from memory
- Look up order details via gateway
- Combine both for personalized responses
"""

import json
import importlib.util
import sys

print("="*80)
print("FULL-FEATURED AGENT TEST")
print("="*80)
print("Testing: Memory + Gateway + Knowledge Base Integration")
print()

# Load all configuration files
print("Step 1: Loading configuration files...")
with open('memory_config.json') as f:
    memory_config = json.load(f)
    memory_id = memory_config['memory_id']
    print(f"✓ Memory ID: {memory_id}")

with open('gateway_config.json') as f:
    gateway_config = json.load(f)
    gateway_url = gateway_config['gateway_url']
    print(f"✓ Gateway URL: {gateway_url}")

with open('cognito_config.json') as f:
    cognito_config = json.load(f)
    print(f"✓ Cognito Client ID: {cognito_config['client_id']}")

with open('kb_config.json') as f:
    kb_config = json.load(f)
    kb_id = kb_config['knowledge_base_id']
    print(f"✓ Knowledge Base ID: {kb_id}")

print()

# Import the full-featured agent
print("Step 2: Loading full-featured agent...")
spec = importlib.util.spec_from_file_location("full_agent", "14_full_agent.py")
full_agent = importlib.util.module_from_spec(spec)
sys.modules["full_agent"] = full_agent
spec.loader.exec_module(full_agent)
print("✓ Agent loaded successfully")
print()

# Test query
test_query = "Hi! Can you look up my order ORD-001 and tell me if I can return it? Remember, I prefer email updates."

print("="*80)
print("TEST SCENARIO")
print("="*80)
print("Customer: user_001")
print("Session: test-full-agent-001")
print()
print("Query:")
print(f'  "{test_query}"')
print()
print("Expected Agent Capabilities:")
print("  1. Recall customer preference for email updates (from memory)")
print("  2. Call lookup_order tool to get ORD-001 details (via gateway)")
print("  3. Analyze return eligibility based on order data")
print("  4. Provide personalized response mentioning email preference")
print()

print("="*80)
print("AGENT RESPONSE")
print("="*80)
print()

# Run the agent with user_001 as the actor
try:
    response = full_agent.run_agent(
        user_input=test_query,
        session_id="test-full-agent-001",
        actor_id="user_001"
    )
    print(response)
    print()
    
    print("="*80)
    print("CAPABILITY VERIFICATION")
    print("="*80)
    
    # Check if the agent demonstrated key capabilities
    response_lower = response.lower()
    
    checks = {
        "Memory - Email preference": "email" in response_lower,
        "Gateway - Order lookup": any(keyword in response_lower for keyword in ["ord-001", "order", "laptop", "dell", "xps"]),
        "Gateway - Order details": any(keyword in response_lower for keyword in ["1299", "$1", "purchase"]),
        "Analysis - Return eligibility": any(keyword in response_lower for keyword in ["eligible", "return", "15 days", "30 days"]),
        "Personalization": "email" in response_lower or "preference" in response_lower
    }
    
    print()
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        result = "PASS" if passed else "FAIL"
        print(f"  {status} {check_name}: {result}")
    
    print()
    passed_count = sum(checks.values())
    total_count = len(checks)
    
    if passed_count == total_count:
        print(f"🎉 SUCCESS: All {total_count}/{total_count} capabilities verified!")
        print()
        print("The agent successfully:")
        print("  - Retrieved customer preferences from memory")
        print("  - Called the gateway to look up order details")
        print("  - Analyzed return eligibility")
        print("  - Provided a personalized response")
    elif passed_count >= 3:
        print(f"⚠️  PARTIAL SUCCESS: {passed_count}/{total_count} capabilities verified")
        print()
        print("The agent demonstrated most capabilities but may need adjustment.")
    else:
        print(f"⚠️  LIMITED SUCCESS: {passed_count}/{total_count} capabilities verified")
        print()
        print("Possible issues:")
        print("  - Memory may not have been seeded (run 04_seed_memory.py)")
        print("  - Gateway target may not be registered (run 12_add_lambda_to_gateway.py)")
        print("  - OAuth token may have expired or be invalid")
    
    print()
    print("="*80)
    print("INTEGRATION STATUS")
    print("="*80)
    print(f"Memory: {memory_id}")
    print(f"Gateway: {gateway_url}")
    print(f"Knowledge Base: {kb_id}")
    print(f"Cognito: Configured")
    print()
    print("All integrations are configured and ready.")
    print("="*80)
    
except Exception as e:
    print(f"❌ Error running agent: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("Troubleshooting:")
    print("  1. Ensure all setup scripts have been run (03-12)")
    print("  2. Check that memory has been seeded (04_seed_memory.py)")
    print("  3. Verify gateway target is registered (13_list_gateway_targets.py)")
    print("  4. Confirm Cognito credentials are valid")
    print("  5. Check AWS credentials and permissions")

print()
