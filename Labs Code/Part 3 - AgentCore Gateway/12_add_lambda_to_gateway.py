#!/usr/bin/env python3
"""
Script to add Lambda target to AgentCore Gateway.

Prerequisites:
- gateway_config.json (from gateway creation)
- lambda_config.json (from Lambda creation)
"""

import json
import boto3

print("="*80)
print("ADD LAMBDA TARGET TO AGENTCORE GATEWAY")
print("="*80)
print("Region: us-west-2")
print()

# Load configuration
print("Step 1: Loading configuration files...")
with open('gateway_config.json') as f:
    gateway_config = json.load(f)
    print(f"✓ Loaded gateway config")
    print(f"  Gateway ID: {gateway_config['gateway_id']}")

with open('lambda_config.json') as f:
    lambda_config = json.load(f)
    print(f"✓ Loaded Lambda config")
    print(f"  Function ARN: {lambda_config['function_arn']}")
    print(f"  Tool Schema: {len(lambda_config['tool_schema'])} tool(s)")
print()

# Initialize AgentCore control plane client
print("Step 2: Initializing AgentCore client...")
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')
print("✓ Client initialized")
print()

# Build Lambda target configuration with MCP protocol
print("Step 3: Building Lambda target configuration...")
lambda_target_config = {
    "mcp": {
        "lambda": {
            "lambdaArn": lambda_config["function_arn"],
            "toolSchema": {
                "inlinePayload": lambda_config["tool_schema"]
            }
        }
    }
}

# Use gateway's IAM role for Lambda invocation
credential_config = [{"credentialProviderType": "GATEWAY_IAM_ROLE"}]
print("✓ Target configuration built")
print()

# Create target
print("Step 4: Adding Lambda target to gateway...")
print(f"  Gateway: {gateway_config['name']}")
print(f"  Target Name: OrderLookup")
print(f"  Lambda: {lambda_config['function_name']}")
print()

try:
    create_response = gateway_client.create_gateway_target(
        gatewayIdentifier=gateway_config["gateway_id"],
        name="OrderLookup",
        description="Lambda function to look up order details for returns processing",
        targetConfiguration=lambda_target_config,
        credentialProviderConfigurations=credential_config
    )
    
    target_id = create_response["targetId"]
    
    print(f"✓ Lambda target added successfully!")
    print(f"  Target ID: {target_id}")
    print(f"  Target Name: OrderLookup")
    print()
    
    # Update gateway config with target info
    print("Step 5: Updating gateway_config.json with target information...")
    if "targets" not in gateway_config:
        gateway_config["targets"] = []
    
    gateway_config["targets"].append({
        "target_id": target_id,
        "target_name": "OrderLookup",
        "lambda_arn": lambda_config["function_arn"],
        "tool_schema": lambda_config["tool_schema"]
    })
    
    with open('gateway_config.json', 'w') as f:
        json.dump(gateway_config, f, indent=2)
    
    print("✓ Configuration updated")
    print()
    
    # Summary
    print("="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print(f"Gateway: {gateway_config['name']}")
    print(f"Gateway URL: {gateway_config['gateway_url']}")
    print()
    print("Target Added:")
    print(f"  - Name: OrderLookup")
    print(f"  - Target ID: {target_id}")
    print(f"  - Lambda: {lambda_config['function_name']}")
    print()
    print("Available Tools:")
    for tool in lambda_config["tool_schema"]:
        print(f"  - {tool['name']}: {tool['description']}")
    print()
    print("Next steps:")
    print("1. Configure your agent to connect to this gateway")
    print("2. Agent will discover the lookup_order tool automatically")
    print("3. Agent can call: lookup_order(order_id='ORD-001')")
    print("="*80)
    
except Exception as e:
    print(f"❌ Error adding Lambda target: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
