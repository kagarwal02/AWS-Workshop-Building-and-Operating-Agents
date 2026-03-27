#!/usr/bin/env python3
"""
Script to create IAM role for AgentCore Gateway.

This role allows the gateway to invoke Lambda functions on behalf of the agent.
"""

import json
import boto3
import time
from botocore.exceptions import ClientError

REGION = "us-west-2"

print("="*80)
print("IAM ROLE SETUP FOR AGENTCORE GATEWAY")
print("="*80)
print(f"Region: {REGION}")
print()

# Create IAM client
iam_client = boto3.client('iam', region_name=REGION)
sts_client = boto3.client('sts', region_name=REGION)

# Get AWS account ID
account_id = sts_client.get_caller_identity()['Account']
print(f"AWS Account ID: {account_id}")
print()

# Generate unique role name
timestamp = str(int(time.time()))
role_name = f"AgentCoreGatewayRole-{timestamp}"
policy_name = f"AgentCoreGatewayPolicy-{timestamp}"

try:
    # Step 1: Create trust policy for AgentCore Gateway
    print("Step 1: Creating IAM role with trust policy...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_response = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="IAM role for AgentCore Gateway to invoke Lambda functions",
        MaxSessionDuration=3600
    )
    
    role_arn = role_response['Role']['Arn']
    print(f"✓ Role created: {role_name}")
    print(f"  ARN: {role_arn}")
    print()
    
    # Step 2: Create policy for Lambda invocation
    print("Step 2: Creating IAM policy for Lambda invocation...")
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": f"arn:aws:lambda:{REGION}:{account_id}:function:*"
            }
        ]
    }
    
    policy_response = iam_client.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document),
        Description="Policy allowing AgentCore Gateway to invoke Lambda functions"
    )
    
    policy_arn = policy_response['Policy']['Arn']
    print(f"✓ Policy created: {policy_name}")
    print(f"  ARN: {policy_arn}")
    print()
    
    # Step 3: Attach policy to role
    print("Step 3: Attaching policy to role...")
    
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    
    print("✓ Policy attached to role")
    print()
    
    # Step 4: Wait for IAM propagation
    print("Step 4: Waiting for IAM propagation (10 seconds)...")
    time.sleep(10)
    print("✓ IAM propagation complete")
    print()
    
    # Step 5: Save configuration
    print("Step 5: Saving configuration to gateway_role_config.json...")
    
    config = {
        "role_arn": role_arn,
        "role_name": role_name,
        "policy_arn": policy_arn,
        "policy_name": policy_name,
        "region": REGION,
        "account_id": account_id
    }
    
    with open('gateway_role_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration saved to gateway_role_config.json")
    print()
    
    # Summary
    print("="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print(f"Role Name: {role_name}")
    print(f"Role ARN: {role_arn}")
    print()
    print("Permissions granted:")
    print("  - lambda:InvokeFunction on all Lambda functions in this account")
    print()
    print("Trust relationship:")
    print("  - bedrock-agentcore.amazonaws.com can assume this role")
    print()
    print("Next steps:")
    print("1. Use this role ARN when creating an AgentCore Gateway")
    print("2. The gateway will use this role to invoke Lambda functions")
    print("3. Create Lambda functions that the gateway will expose as tools")
    print("="*80)
    
except ClientError as e:
    error_code = e.response['Error']['Code']
    
    if error_code == 'EntityAlreadyExists':
        print(f"⚠️  Role or policy already exists")
        print("   Try deleting the existing resources or use a different name")
    else:
        print(f"❌ AWS Error: {e}")
    
    exit(1)
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
