#!/usr/bin/env python3
"""
Script to check AgentCore Runtime deployment status.

Monitors deployment until READY or FAILED state.
"""

import json
import os
import time
from bedrock_agentcore_starter_toolkit import Runtime

print("="*80)
print("AGENTCORE RUNTIME STATUS CHECK")
print("="*80)
print()

# Check if runtime config exists
if not os.path.exists('runtime_config.json'):
    print("✗ Error: Agent not deployed yet")
    print("  Please run 19_deploy_agent.py first")
    exit(1)

# Load configuration files
print("Loading configuration...")
try:
    with open('runtime_execution_role_config.json') as f:
        role_config = json.load(f)
    
    with open('cognito_config.json') as f:
        cognito_config = json.load(f)
    
    with open('runtime_config.json') as f:
        runtime_output = json.load(f)
    
    print(f"✓ Agent: {runtime_output['agent_name']}")
    print(f"✓ ARN: {runtime_output['agent_arn']}")
    print()
except FileNotFoundError as e:
    print(f"✗ Error: Configuration file not found: {e}")
    exit(1)

# Initialize Runtime
runtime = Runtime()

# Build authorizer configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Configure runtime (to load existing configuration)
print("Initializing runtime client...")
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
print("✓ Runtime client initialized")
print()

# Monitor status
print("="*80)
print("MONITORING DEPLOYMENT STATUS")
print("="*80)
print()

max_attempts = 60  # Monitor for up to 10 minutes (60 * 10 seconds)
attempt = 0

while attempt < max_attempts:
    try:
        # Check status
        status_response = runtime.status()
        status = status_response.endpoint.get("status", "UNKNOWN")
        
        # Display status
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Status: {status}")
        
        # Check if terminal state reached
        if status == "READY":
            print()
            print("="*80)
            print("✓ DEPLOYMENT SUCCESSFUL!")
            print("="*80)
            print()
            print("Agent Details:")
            print(f"  Name: {runtime_output['agent_name']}")
            print(f"  ARN: {runtime_output['agent_arn']}")
            print(f"  Status: {status}")
            print(f"  Region: us-west-2")
            print()
            print("Integrations:")
            print(f"  Memory: {runtime_output.get('memory_id', 'N/A')}")
            print(f"  Gateway: {runtime_output.get('gateway_url', 'N/A')}")
            print(f"  Knowledge Base: {runtime_output.get('knowledge_base_id', 'N/A')}")
            print()
            print("Next Steps:")
            print("  1. Get OAuth token from Cognito")
            print("  2. Invoke agent with bearer token")
            print("  3. Test with: 'Can you look up order ORD-001?'")
            print()
            print("="*80)
            break
        
        elif status in ["CREATE_FAILED", "UPDATE_FAILED", "FAILED"]:
            print()
            print("="*80)
            print("✗ DEPLOYMENT FAILED!")
            print("="*80)
            print()
            print("Status Details:")
            print(json.dumps(status_response.endpoint, indent=2, default=str))
            print()
            print("Troubleshooting:")
            print("  1. Check CloudWatch logs:")
            print(f"     Log group: /aws/bedrock-agentcore/runtime/{runtime_output['agent_name']}")
            print("  2. Verify execution role has all required permissions")
            print("  3. Check that requirements.txt has all dependencies")
            print("  4. Ensure 17_runtime_agent.py has no syntax errors")
            print()
            print("="*80)
            exit(1)
        
        elif status in ["CREATING", "UPDATING"]:
            # Still in progress
            if attempt == 0:
                print()
                print("⏳ Deployment in progress...")
                print("   This typically takes 5-10 minutes")
                print("   Checking status every 10 seconds...")
                print()
            
            # Wait before next check
            time.sleep(10)
            attempt += 1
        
        else:
            print(f"⚠️  Unknown status: {status}")
            print("   Continuing to monitor...")
            time.sleep(10)
            attempt += 1
    
    except KeyboardInterrupt:
        print()
        print()
        print("="*80)
        print("MONITORING INTERRUPTED")
        print("="*80)
        print()
        print("Deployment is still running in the background.")
        print("Run this script again to check status.")
        print("="*80)
        exit(0)
    
    except Exception as e:
        print()
        print(f"✗ Error checking status: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("Retrying in 10 seconds...")
        time.sleep(10)
        attempt += 1

if attempt >= max_attempts:
    print()
    print("="*80)
    print("⏱️  MONITORING TIMEOUT")
    print("="*80)
    print()
    print("Deployment is taking longer than expected (>10 minutes).")
    print()
    print("This could mean:")
    print("  - The build is still running (check CodeBuild console)")
    print("  - There's an issue with the deployment")
    print()
    print("Check CloudWatch logs for details:")
    print(f"  Log group: /aws/bedrock-agentcore/runtime/{runtime_output['agent_name']}")
    print()
    print("Run this script again to continue monitoring.")
    print("="*80)
