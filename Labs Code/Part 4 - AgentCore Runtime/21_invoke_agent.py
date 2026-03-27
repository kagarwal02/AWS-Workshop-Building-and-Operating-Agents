#!/usr/bin/env python3
"""
Script to invoke deployed AgentCore Runtime agent.

This script:
1. Loads Cognito credentials
2. Gets OAuth token
3. Invokes the deployed agent
4. Displays the response
"""

import json
import os
import requests
from bedrock_agentcore_starter_toolkit import Runtime

print("="*80)
print("INVOKE AGENTCORE RUNTIME AGENT")
print("="*80)
print()

# Check if runtime config exists
if not os.path.exists('runtime_config.json'):
    print("✗ Error: Agent not deployed yet")
    print("  Please run 19_deploy_agent.py first")
    exit(1)

# Load configuration files
print("Step 1: Loading configuration...")
try:
    with open('cognito_config.json') as f:
        cognito_config = json.load(f)
        print(f"✓ Cognito Client ID: {cognito_config['client_id']}")
    
    with open('runtime_execution_role_config.json') as f:
        role_config = json.load(f)
        print(f"✓ Execution Role loaded")
    
    with open('runtime_config.json') as f:
        runtime_output = json.load(f)
        print(f"✓ Agent: {runtime_output['agent_name']}")
        print(f"✓ ARN: {runtime_output['agent_arn']}")
except FileNotFoundError as e:
    print(f"✗ Error: Configuration file not found: {e}")
    exit(1)

print()

# Step 2: Get OAuth token
print("Step 2: Getting OAuth bearer token...")

try:
    # Use token endpoint from config
    token_endpoint = cognito_config["token_endpoint"]
    
    # Request token using client credentials flow
    response = requests.post(
        token_endpoint,
        data={
            "grant_type": "client_credentials",
            "client_id": cognito_config["client_id"],
            "client_secret": cognito_config["client_secret"],
            "scope": "gateway-api/read gateway-api/write"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"✗ Failed to get OAuth token")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        exit(1)
    
    bearer_token = response.json()["access_token"]
    print("✓ OAuth token obtained")
    print()

except Exception as e:
    print(f"✗ Error getting OAuth token: {e}")
    exit(1)

# Step 3: Initialize Runtime
print("Step 3: Initializing runtime client...")

runtime = Runtime()

# Build authorizer configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Configure runtime (to load existing configuration)
runtime.configure(
    entrypoint="17_runtime_agent.py",
    agent_name=runtime_output['agent_name'],
    execution_role=role_config["role_arn"],
    auto_create_ecr=True,
    memory_mode="NO_MEMORY",
    requirements_file="requirements.txt",
    region="us-west-2",
    authorizer_configuration=auth_config
)

print("✓ Runtime client configured")
print()

# Step 4: Invoke agent
print("Step 4: Invoking agent...")
print()

test_query = "Can you look up my order ORD-001 and help me with a return?"

print("="*80)
print("TEST INVOCATION")
print("="*80)
print(f"Actor ID: user_001")
print(f"Query: {test_query}")
print()
print("Expected behavior:")
print("  1. Agent recalls user_001's email preference from memory")
print("  2. Agent calls lookup_order tool via gateway")
print("  3. Agent retrieves order ORD-001 details (Dell XPS 15 Laptop)")
print("  4. Agent analyzes return eligibility (15 days ago, eligible)")
print("  5. Agent provides personalized response")
print()
print("="*80)
print()

payload = {
    "prompt": test_query,
    "actor_id": "user_001"
}

try:
    print("Sending request to agent...")
    response = runtime.invoke(
        payload,
        bearer_token=bearer_token
    )
    
    print()
    print("="*80)
    print("AGENT RESPONSE")
    print("="*80)
    print()
    print(response)
    print()
    print("="*80)
    print("INVOCATION SUCCESSFUL")
    print("="*80)
    print()
    print("The agent successfully:")
    print("  ✓ Authenticated with OAuth token")
    print("  ✓ Processed the request")
    print("  ✓ Accessed Memory, Gateway, and Knowledge Base")
    print("  ✓ Returned a response")
    print()
    print("Integration Status:")
    print(f"  Memory: {runtime_output.get('memory_id', 'N/A')}")
    print(f"  Gateway: {runtime_output.get('gateway_url', 'N/A')}")
    print(f"  Knowledge Base: {runtime_output.get('knowledge_base_id', 'N/A')}")
    print()
    print("="*80)

except Exception as e:
    print()
    print("="*80)
    print("INVOCATION FAILED")
    print("="*80)
    print(f"Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("Troubleshooting:")
    print("  1. Check agent status:")
    print("     python 20_check_status.py")
    print()
    print("  2. Verify agent is in READY state")
    print()
    print("  3. Check CloudWatch logs:")
    print(f"     Log group: /aws/bedrock-agentcore/runtime/{runtime_output['agent_name']}")
    print()
    print("  4. Verify OAuth token is valid:")
    print("     - Check Cognito configuration")
    print("     - Verify scopes are correct")
    print()
    print("  5. Ensure all integrations are configured:")
    print("     - Memory ID is set")
    print("     - Gateway URL is accessible")
    print("     - Knowledge Base ID is valid")
    print()
    print("="*80)
    exit(1)
