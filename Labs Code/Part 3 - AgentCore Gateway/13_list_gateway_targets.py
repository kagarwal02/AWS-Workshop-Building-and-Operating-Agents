#!/usr/bin/env python3
"""
Script to list AgentCore Gateway targets.

Prerequisites:
- gateway_config.json (from gateway creation)
"""

import json
import boto3

print("="*80)
print("LIST AGENTCORE GATEWAY TARGETS")
print("="*80)
print("Region: us-west-2")
print()

# Load configuration
print("Step 1: Loading gateway configuration...")
with open('gateway_config.json') as f:
    gateway_config = json.load(f)
    print(f"✓ Loaded gateway config")
    print(f"  Gateway: {gateway_config['name']}")
    print(f"  Gateway ID: {gateway_config['gateway_id']}")
print()

# Initialize AgentCore control plane client
print("Step 2: Initializing AgentCore client...")
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')
print("✓ Client initialized")
print()

# List targets
print("Step 3: Retrieving gateway targets...")
try:
    response = gateway_client.list_gateway_targets(
        gatewayIdentifier=gateway_config["gateway_id"]
    )
    
    targets = response.get("items", [])
    
    print(f"✓ Found {len(targets)} target(s)")
    print()
    
    if targets:
        print("="*80)
        print("GATEWAY TARGETS")
        print("="*80)
        
        for i, target in enumerate(targets, 1):
            print(f"\nTarget {i}:")
            print(f"  {'─' * 76}")
            print(f"  Name: {target.get('name', 'N/A')}")
            print(f"  Target ID: {target.get('targetId', 'N/A')}")
            print(f"  Status: {target.get('status', 'unknown')}")
            print(f"  Description: {target.get('description', 'N/A')}")
            
            # Show creation time if available
            if 'createdAt' in target:
                print(f"  Created: {target['createdAt']}")
            
            # Show update time if available
            if 'updatedAt' in target:
                print(f"  Updated: {target['updatedAt']}")
        
        print()
        print("="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Gateway: {gateway_config['name']}")
        print(f"Gateway URL: {gateway_config['gateway_url']}")
        print(f"Total Targets: {len(targets)}")
        print()
        
        # List target names
        print("Available Targets:")
        for target in targets:
            status_icon = "✓" if target.get('status') == 'AVAILABLE' else "⚠️"
            print(f"  {status_icon} {target.get('name', 'N/A')} ({target.get('status', 'unknown')})")
        
        print()
        print("Agents can discover and use these targets as tools.")
        print("="*80)
        
    else:
        print("⚠️  No targets found")
        print()
        print("To add targets:")
        print("1. Create a Lambda function")
        print("2. Run the add_lambda_to_gateway script")
        print("3. The target will appear in this list")
    
except Exception as e:
    print(f"❌ Error listing targets: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
