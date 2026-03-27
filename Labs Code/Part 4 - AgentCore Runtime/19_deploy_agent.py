#!/usr/bin/env python3
"""
Script to deploy agent to AgentCore Runtime.

This script:
1. Loads all configuration files
2. Configures runtime deployment settings
3. Launches agent to production
4. Saves agent ARN to runtime_config.json
"""

import json
import os
from bedrock_agentcore_starter_toolkit import Runtime

print("="*80)
print("AGENTCORE RUNTIME DEPLOYMENT")
print("="*80)
print()

# Step 1: Load all configuration files
print("Step 1: Loading configuration files...")

try:
    with open('memory_config.json') as f:
        memory_config = json.load(f)
        print(f"✓ Memory ID: {memory_config['memory_id']}")
except FileNotFoundError:
    print("✗ memory_config.json not found")
    exit(1)

try:
    with open('gateway_config.json') as f:
        gateway_config = json.load(f)
        print(f"✓ Gateway URL: {gateway_config['gateway_url']}")
except FileNotFoundError:
    print("✗ gateway_config.json not found")
    exit(1)

try:
    with open('cognito_config.json') as f:
        cognito_config = json.load(f)
        print(f"✓ Cognito Client ID: {cognito_config['client_id']}")
except FileNotFoundError:
    print("✗ cognito_config.json not found")
    exit(1)

try:
    with open('runtime_execution_role_config.json') as f:
        role_config = json.load(f)
        print(f"✓ Execution Role: {role_config['role_arn']}")
except FileNotFoundError:
    print("✗ runtime_execution_role_config.json not found")
    exit(1)

try:
    with open('kb_config.json') as f:
        kb_config = json.load(f)
        print(f"✓ Knowledge Base ID: {kb_config['knowledge_base_id']}")
except FileNotFoundError:
    print("✗ kb_config.json not found")
    exit(1)

print()

# Step 2: Initialize Runtime
print("Step 2: Initializing AgentCore Runtime...")
runtime = Runtime()
print("✓ Runtime initialized")
print()

# Step 3: Configure runtime deployment
print("Step 3: Configuring runtime deployment...")

# Build authorizer configuration for Cognito JWT
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

runtime.configure(
    entrypoint="17_runtime_agent.py",
    agent_name="returns_refunds_agent",
    execution_role=role_config["role_arn"],
    auto_create_ecr=True,
    memory_mode="NO_MEMORY",  # We handle memory in the agent code
    requirements_file="requirements.txt",
    region="us-west-2",
    authorizer_configuration=auth_config
)

print("✓ Runtime configured")
print("  Entrypoint: 17_runtime_agent.py")
print("  Agent name: returns_refunds_agent")
print("  Region: us-west-2")
print()

# Step 4: Build environment variables
print("Step 4: Building environment variables...")

env_vars = {
    "MEMORY_ID": memory_config["memory_id"],
    "GATEWAY_URL": gateway_config["gateway_url"],
    "COGNITO_CLIENT_ID": cognito_config["client_id"],
    "COGNITO_CLIENT_SECRET": cognito_config["client_secret"],
    "COGNITO_DISCOVERY_URL": cognito_config["discovery_url"],
    "KNOWLEDGE_BASE_ID": kb_config["knowledge_base_id"],
    "OAUTH_SCOPES": "gateway-api/read gateway-api/write"
}

print("✓ Environment variables configured:")
for key in env_vars:
    if "SECRET" in key:
        print(f"  {key}: ***")
    else:
        print(f"  {key}: {env_vars[key]}")
print()

# Step 5: Launch to runtime
print("="*80)
print("LAUNCHING AGENT TO AGENTCORE RUNTIME")
print("="*80)
print()
print("This process will:")
print("  1. Create CodeBuild project")
print("  2. Build Docker container from your agent code")
print("  3. Push container to Amazon ECR")
print("  4. Deploy to AgentCore Runtime")
print()
print("⏱️  Expected time: 5-10 minutes")
print()
print("☕ Grab a coffee while the deployment runs...")
print("="*80)
print()

try:
    launch_result = runtime.launch(
        env_vars=env_vars,
        auto_update_on_conflict=True
    )
    
    agent_arn = launch_result.agent_arn
    
    print()
    print("="*80)
    print("DEPLOYMENT INITIATED!")
    print("="*80)
    print(f"Agent ARN: {agent_arn}")
    print()
    
    # Step 6: Save configuration
    print("Step 6: Saving configuration to runtime_config.json...")
    
    runtime_output_config = {
        "agent_arn": agent_arn,
        "agent_name": "returns_refunds_agent",
        "region": "us-west-2",
        "memory_id": memory_config["memory_id"],
        "gateway_url": gateway_config["gateway_url"],
        "knowledge_base_id": kb_config["knowledge_base_id"]
    }
    
    with open('runtime_config.json', 'w') as f:
        json.dump(runtime_output_config, f, indent=2)
    
    print("✓ Configuration saved to runtime_config.json")
    print()
    
    # Summary
    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print()
    print("1. Monitor deployment status:")
    print("   The build process is running in CodeBuild")
    print("   Check status with: runtime.status()")
    print()
    print("2. Wait for status to show 'READY':")
    print("   This may take 5-10 minutes for the first deployment")
    print("   Status will change: CREATING → READY")
    print()
    print("3. Once READY, your agent will be accessible via:")
    print(f"   Agent ARN: {agent_arn}")
    print("   Authentication: OAuth via Cognito")
    print()
    print("4. Test your deployed agent:")
    print("   - Get OAuth token from Cognito")
    print("   - Invoke agent with bearer token")
    print("   - Agent will have access to Memory, Gateway, and Knowledge Base")
    print()
    print("="*80)
    print()
    print("Deployment configuration:")
    print(f"  Memory: {memory_config['memory_id']}")
    print(f"  Gateway: {gateway_config['gateway_url']}")
    print(f"  Knowledge Base: {kb_config['knowledge_base_id']}")
    print(f"  Execution Role: {role_config['role_arn']}")
    print(f"  Cognito: {cognito_config['client_id']}")
    print("="*80)
    
except Exception as e:
    print()
    print("="*80)
    print("DEPLOYMENT FAILED")
    print("="*80)
    print(f"Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("Troubleshooting:")
    print("  1. Verify all configuration files exist and are valid")
    print("  2. Check that the execution role has all required permissions")
    print("  3. Ensure requirements.txt is present")
    print("  4. Verify 17_runtime_agent.py exists")
    print("  5. Check AWS credentials and permissions")
    print("="*80)
    exit(1)
