#!/usr/bin/env python3
"""
Script to create IAM execution role for AgentCore Runtime.

This script creates an IAM role with permissions for:
- Bedrock model access
- AgentCore Memory operations
- Knowledge Base retrieval
- CloudWatch logging
- X-Ray tracing
- Gateway invocation
- ECR container access
"""

import json
import boto3
import time

# Configuration
REGION = "us-west-2"
ROLE_NAME = f"AgentCoreRuntimeExecutionRole-{int(time.time())}"
POLICY_NAME = f"AgentCoreRuntimePolicy-{int(time.time())}"

print("="*80)
print("IAM EXECUTION ROLE SETUP FOR AGENTCORE RUNTIME")
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

try:
    # Step 1: Define trust policy for bedrock-agentcore.amazonaws.com
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
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Execution role for AgentCore Runtime with full permissions"
    )
    role_arn = role_response['Role']['Arn']
    print(f"✓ Role created: {ROLE_NAME}")
    print(f"  ARN: {role_arn}")
    print()
    
    # Step 2: Create comprehensive permissions policy
    print("Step 2: Creating permissions policy...")
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockModelAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            },
            {
                "Sid": "AgentCoreMemoryAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetMemory",
                    "bedrock-agentcore:CreateEvent",
                    "bedrock-agentcore:GetLastKTurns",
                    "bedrock-agentcore:RetrieveMemory",
                    "bedrock-agentcore:ListEvents"
                ],
                "Resource": f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:*"
            },
            {
                "Sid": "KnowledgeBaseAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock:Retrieve"
                ],
                "Resource": f"arn:aws:bedrock:{REGION}:{account_id}:knowledge-base/*"
            },
            {
                "Sid": "CloudWatchLogsAccess",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams"
                ],
                "Resource": [
                    f"arn:aws:logs:{REGION}:{account_id}:log-group:/aws/bedrock-agentcore/*",
                    f"arn:aws:logs:{REGION}:{account_id}:log-group:*"
                ]
            },
            {
                "Sid": "XRayAccess",
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords"
                ],
                "Resource": "*"
            },
            {
                "Sid": "GatewayAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:InvokeGateway",
                    "bedrock-agentcore:GetGateway",
                    "bedrock-agentcore:ListGatewayTargets"
                ],
                "Resource": f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:gateway/*"
            },
            {
                "Sid": "ECRAccess",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage"
                ],
                "Resource": "*"
            },
            {
                "Sid": "WorkloadIdentityAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
                ],
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:workload-identity-directory/default/workload-identity/*"
                ]
            }
        ]
    }
    
    policy_response = iam_client.create_policy(
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(permissions_policy),
        Description="Permissions for AgentCore Runtime execution"
    )
    policy_arn = policy_response['Policy']['Arn']
    print(f"✓ Policy created: {POLICY_NAME}")
    print(f"  ARN: {policy_arn}")
    print()
    
    # Step 3: Attach policy to role
    print("Step 3: Attaching policy to role...")
    iam_client.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn=policy_arn
    )
    print("✓ Policy attached to role")
    print()
    
    # Step 4: Wait for role to propagate
    print("Step 4: Waiting for IAM propagation (10 seconds)...")
    time.sleep(10)
    print("✓ IAM propagation complete")
    print()
    
    # Step 5: Save configuration
    print("Step 5: Saving configuration to runtime_execution_role_config.json...")
    config = {
        "role_name": ROLE_NAME,
        "role_arn": role_arn,
        "policy_name": POLICY_NAME,
        "policy_arn": policy_arn,
        "region": REGION,
        "account_id": account_id
    }
    
    with open('runtime_execution_role_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration saved")
    print()
    
    # Summary
    print("="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print(f"Role Name: {ROLE_NAME}")
    print(f"Role ARN: {role_arn}")
    print()
    print("Permissions granted:")
    print("  ✓ Bedrock - InvokeModel, InvokeModelWithResponseStream")
    print("  ✓ Memory - GetMemory, CreateEvent, GetLastKTurns, RetrieveMemory, ListEvents")
    print("  ✓ Knowledge Base - Retrieve (bedrock:Retrieve)")
    print("  ✓ CloudWatch Logs - CreateLogGroup, CreateLogStream, PutLogEvents, DescribeLogStreams")
    print("  ✓ X-Ray - PutTraceSegments, PutTelemetryRecords")
    print("  ✓ Gateway - InvokeGateway, GetGateway, ListGatewayTargets")
    print("  ✓ ECR - GetAuthorizationToken, BatchCheckLayerAvailability, GetDownloadUrlForLayer, BatchGetImage")
    print("  ✓ Workload Identity - Secure credential management")
    print()
    print("Trust relationship:")
    print("  - bedrock-agentcore.amazonaws.com can assume this role")
    print()
    print("Next steps:")
    print("1. Use this role ARN when deploying to AgentCore Runtime")
    print("2. Runtime will use this role to access all required services")
    print("3. Your agent will have full access to Memory, Gateway, and Knowledge Base")
    print("="*80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Cleaning up resources...")
    try:
        if 'policy_arn' in locals():
            iam_client.detach_role_policy(RoleName=ROLE_NAME, PolicyArn=policy_arn)
            iam_client.delete_policy(PolicyArn=policy_arn)
        if 'role_arn' in locals():
            iam_client.delete_role(RoleName=ROLE_NAME)
        print("✓ Cleanup complete")
    except:
        pass
    exit(1)
