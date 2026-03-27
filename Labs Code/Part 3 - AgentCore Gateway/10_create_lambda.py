#!/usr/bin/env python3
"""
Script to create Lambda function for order lookup.

This Lambda function will be exposed through AgentCore Gateway as a tool.
"""

import json
import boto3
import time
import zipfile
import io
from botocore.exceptions import ClientError

REGION = "us-west-2"

print("="*80)
print("LAMBDA FUNCTION SETUP FOR AGENTCORE GATEWAY")
print("="*80)
print(f"Region: {REGION}")
print()

# Create clients
lambda_client = boto3.client('lambda', region_name=REGION)
iam_client = boto3.client('iam', region_name=REGION)
sts_client = boto3.client('sts', region_name=REGION)

# Get AWS account ID
account_id = sts_client.get_caller_identity()['Account']
print(f"AWS Account ID: {account_id}")
print()

# Generate unique names
timestamp = str(int(time.time()))
function_name = "OrderLookupFunction"
lambda_role_name = f"LambdaExecutionRole-{timestamp}"

try:
    # Step 1: Create Lambda execution role
    print("Step 1: Creating Lambda execution role...")
    
    lambda_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    lambda_role_response = iam_client.create_role(
        RoleName=lambda_role_name,
        AssumeRolePolicyDocument=json.dumps(lambda_trust_policy),
        Description="Execution role for OrderLookupFunction Lambda"
    )
    
    lambda_role_arn = lambda_role_response['Role']['Arn']
    print(f"✓ Lambda role created: {lambda_role_name}")
    print(f"  ARN: {lambda_role_arn}")
    print()
    
    # Attach basic Lambda execution policy
    print("Step 2: Attaching CloudWatch Logs policy...")
    iam_client.attach_role_policy(
        RoleName=lambda_role_name,
        PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    )
    print("✓ Policy attached")
    print()
    
    # Wait for IAM propagation
    print("Step 3: Waiting for IAM propagation (10 seconds)...")
    time.sleep(10)
    print("✓ IAM propagation complete")
    print()
    
    # Step 4: Create Lambda function code
    print("Step 4: Creating Lambda function code...")
    
    lambda_code = '''
import json
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Look up order details by order ID.
    
    Returns order information including eligibility for returns.
    """
    
    # Mock order database
    orders = {
        "ORD-001": {
            "order_id": "ORD-001",
            "product_name": "Dell XPS 15 Laptop",
            "purchase_date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "amount": 1299.99,
            "category": "electronics",
            "condition": "unopened",
            "eligible_for_return": True,
            "days_remaining": 15
        },
        "ORD-002": {
            "order_id": "ORD-002",
            "product_name": "iPhone 13 Pro",
            "purchase_date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
            "amount": 999.99,
            "category": "electronics",
            "condition": "used",
            "eligible_for_return": False,
            "days_remaining": 0
        },
        "ORD-003": {
            "order_id": "ORD-003",
            "product_name": "Samsung Galaxy Tab S8",
            "purchase_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "amount": 649.99,
            "category": "electronics",
            "condition": "defective",
            "eligible_for_return": True,
            "days_remaining": 25
        }
    }
    
    # Extract order_id from event
    order_id = event.get("order_id", "").strip().upper()
    
    if not order_id:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "order_id is required"
            })
        }
    
    # Look up order
    order = orders.get(order_id)
    
    if not order:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "error": f"Order {order_id} not found",
                "available_orders": list(orders.keys())
            })
        }
    
    # Return order details
    return {
        "statusCode": 200,
        "body": json.dumps(order)
    }
'''
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    zip_content = zip_buffer.read()
    
    print("✓ Lambda code packaged")
    print()
    
    # Step 5: Create Lambda function
    print(f"Step 5: Creating Lambda function: {function_name}...")
    
    try:
        lambda_response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.10',
            Role=lambda_role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Look up order details by order ID for returns processing',
            Timeout=30,
            MemorySize=128
        )
        
        function_arn = lambda_response['FunctionArn']
        print(f"✓ Lambda function created: {function_name}")
        print(f"  ARN: {function_arn}")
        print()
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print(f"⚠️  Function {function_name} already exists, retrieving ARN...")
            existing_function = lambda_client.get_function(FunctionName=function_name)
            function_arn = existing_function['Configuration']['FunctionArn']
            print(f"  ARN: {function_arn}")
            print()
        else:
            raise
    
    # Step 6: Add permission for AgentCore Gateway to invoke
    print("Step 6: Adding permission for AgentCore Gateway...")
    
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f'AllowAgentCoreGateway-{timestamp}',
            Action='lambda:InvokeFunction',
            Principal='bedrock-agentcore.amazonaws.com',
            SourceAccount=account_id
        )
        print("✓ Permission added for AgentCore Gateway")
        print()
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print("⚠️  Permission already exists")
            print()
        else:
            raise
    
    # Step 7: Define tool schema for MCP
    print("Step 7: Creating MCP tool schema...")
    
    tool_schema = [
        {
            "name": "lookup_order",
            "description": "Look up order details by order ID. Returns order information including product name, purchase date, amount, and return eligibility.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to look up (e.g., ORD-001, ORD-002, ORD-003)"
                    }
                },
                "required": ["order_id"]
            }
        }
    ]
    
    print("✓ Tool schema created")
    print()
    
    # Step 8: Save configuration
    print("Step 8: Saving configuration to lambda_config.json...")
    
    config = {
        "function_name": function_name,
        "function_arn": function_arn,
        "lambda_role_arn": lambda_role_arn,
        "lambda_role_name": lambda_role_name,
        "tool_schema": tool_schema,
        "region": REGION,
        "sample_orders": ["ORD-001", "ORD-002", "ORD-003"]
    }
    
    with open('lambda_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration saved to lambda_config.json")
    print()
    
    # Summary
    print("="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print(f"Function Name: {function_name}")
    print(f"Function ARN: {function_arn}")
    print()
    print("Sample Orders:")
    print("  - ORD-001: Dell XPS 15 Laptop (15 days ago, eligible)")
    print("  - ORD-002: iPhone 13 Pro (45 days ago, not eligible)")
    print("  - ORD-003: Samsung Galaxy Tab S8 (5 days ago, defective, eligible)")
    print()
    print("Tool Schema:")
    print(f"  - Tool name: lookup_order")
    print(f"  - Input: order_id (string)")
    print(f"  - Output: order details with return eligibility")
    print()
    print("Next steps:")
    print("1. Create an AgentCore Gateway")
    print("2. Add this Lambda function as a gateway target")
    print("3. Your agent will be able to call lookup_order(order_id='ORD-001')")
    print("="*80)
    
except ClientError as e:
    print(f"❌ AWS Error: {e}")
    exit(1)
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
