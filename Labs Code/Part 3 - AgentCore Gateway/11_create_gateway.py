#!/usr/bin/env python3
"""
Script to create AgentCore Gateway.

Prerequisites:
- cognito_config.json (from Cognito setup)
- gateway_role_config.json (from IAM role setup)
"""

import json
import boto3

print("="*80)
print("AGENTCORE GATEWAY CREATION")
print("="*80)
print("Region: us-west-2")
print()

# Load configuration
print("Step 1: Loading configuration files...")
with open('cognito_config.json') as f:
    cognito_config = json.load(f)
    print(f"✓ Loaded Cognito config")
    print(f"  Client ID: {cognito_config['client_id']}")
    print(f"  Discovery URL: {cognito_config['discovery_url']}")

with open('gateway_role_config.json') as f:
    role_config = json.load(f)
    print(f"✓ Loaded IAM role config")
    print(f"  Role ARN: {role_config['role_arn']}")
print()

# Initialize AgentCore control plane client
print("Step 2: Initializing AgentCore client...")
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')
print("✓ Client initialized")
print()

# Build auth configuration for Cognito JWT
print("Step 3: Building authentication configuration...")
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}
print("✓ Auth configuration built")
print()

# Create gateway
print("Step 4: Creating AgentCore Gateway: ReturnsRefundsGateway...")
try:
    create_response = gateway_client.create_gateway(
        name="ReturnsRefundsGateway",
        roleArn=role_config["role_arn"],
        protocolType="MCP",
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration=auth_config,
        description="Gateway for returns and refunds agent to access order lookup tools"
    )
    
    # Extract gateway details
    gateway_id = create_response["gatewayId"]
    gateway_url = create_response["gatewayUrl"]
    gateway_arn = create_response["gatewayArn"]
    
    print(f"✓ Gateway created successfully!")
    print(f"  Gateway ID: {gateway_id}")
    print(f"  Gateway URL: {gateway_url}")
    print(f"  Gateway ARN: {gateway_arn}")
    print()
    
    # Save gateway config
    print("Step 5: Saving configuration to gateway_config.json...")
    config = {
        "gateway_id": gateway_id,
        "gateway_url": gateway_url,
        "gateway_arn": gateway_arn,
        "name": "ReturnsRefundsGateway",
        "region": "us-west-2"
    }
    
    with open('gateway_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration saved to gateway_config.json")
    print()
    
    # Summary
    print("="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print(f"Gateway Name: ReturnsRefundsGateway")
    print(f"Gateway ID: {gateway_id}")
    print(f"Gateway URL: {gateway_url}")
    print()
    print("Authentication:")
    print(f"  - Type: CUSTOM_JWT (Cognito OAuth)")
    print(f"  - Client ID: {cognito_config['client_id']}")
    print(f"  - Discovery URL: {cognito_config['discovery_url']}")
    print()
    print("Permissions:")
    print(f"  - Role: {role_config['role_arn']}")
    print(f"  - Can invoke Lambda functions")
    print()
    print("Next steps:")
    print("1. Add Lambda functions as gateway targets")
    print("2. Configure your agent to use this gateway")
    print("3. Agent will discover and call tools through the gateway")
    print("="*80)
    
except Exception as e:
    print(f"❌ Error creating gateway: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
