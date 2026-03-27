#!/usr/bin/env python3
"""
Script to create Cognito User Pool for AgentCore Gateway authentication.

This script sets up OAuth authentication for secure agent-to-gateway communication.
"""

import json
import boto3
import time
from botocore.exceptions import ClientError

REGION = "us-west-2"

print("="*80)
print("COGNITO USER POOL SETUP FOR AGENTCORE GATEWAY")
print("="*80)
print(f"Region: {REGION}")
print()

# Create Cognito client
cognito_client = boto3.client('cognito-idp', region_name=REGION)

# Generate unique domain prefix
timestamp = str(int(time.time()))
domain_prefix = f"returns-agent-{timestamp}"

try:
    # Step 1: Create User Pool
    print("Step 1: Creating Cognito User Pool...")
    user_pool_response = cognito_client.create_user_pool(
        PoolName=f"returns-agent-pool-{timestamp}",
        Policies={
            'PasswordPolicy': {
                'MinimumLength': 8,
                'RequireUppercase': False,
                'RequireLowercase': False,
                'RequireNumbers': False,
                'RequireSymbols': False
            }
        },
        AutoVerifiedAttributes=[],
        Schema=[
            {
                'Name': 'email',
                'AttributeDataType': 'String',
                'Mutable': True,
                'Required': False
            }
        ]
    )
    
    user_pool_id = user_pool_response['UserPool']['Id']
    print(f"✓ User Pool created: {user_pool_id}")
    print()
    
    # Step 2: Create User Pool Domain
    print(f"Step 2: Creating User Pool Domain (prefix: {domain_prefix})...")
    try:
        cognito_client.create_user_pool_domain(
            Domain=domain_prefix,
            UserPoolId=user_pool_id
        )
        print(f"✓ Domain created: {domain_prefix}.auth.{REGION}.amazoncognito.com")
        print()
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterException':
            print(f"⚠️  Domain prefix already exists, trying alternative...")
            domain_prefix = f"returns-agent-{timestamp}-alt"
            cognito_client.create_user_pool_domain(
                Domain=domain_prefix,
                UserPoolId=user_pool_id
            )
            print(f"✓ Domain created: {domain_prefix}.auth.{REGION}.amazoncognito.com")
            print()
        else:
            raise
    
    # Step 3: Create Resource Server with OAuth scopes
    print("Step 3: Creating Resource Server with OAuth scopes...")
    resource_server_response = cognito_client.create_resource_server(
        UserPoolId=user_pool_id,
        Identifier='gateway-api',
        Name='Gateway API',
        Scopes=[
            {
                'ScopeName': 'read',
                'ScopeDescription': 'Read access to gateway resources'
            },
            {
                'ScopeName': 'write',
                'ScopeDescription': 'Write access to gateway resources'
            }
        ]
    )
    print("✓ Resource server created with read/write scopes")
    print()
    
    # Step 4: Create App Client with OAuth support
    print("Step 4: Creating App Client for machine-to-machine authentication...")
    app_client_response = cognito_client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=f"returns-agent-client-{timestamp}",
        GenerateSecret=True,
        ExplicitAuthFlows=[],
        AllowedOAuthFlows=['client_credentials'],
        AllowedOAuthScopes=['gateway-api/read', 'gateway-api/write'],
        AllowedOAuthFlowsUserPoolClient=True,
        SupportedIdentityProviders=[]
    )
    
    client_id = app_client_response['UserPoolClient']['ClientId']
    print(f"✓ App Client created: {client_id}")
    print()
    
    # Step 5: Get client secret
    print("Step 5: Retrieving client secret...")
    client_details = cognito_client.describe_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id
    )
    
    client_secret = client_details['UserPoolClient']['ClientSecret']
    print("✓ Client secret retrieved")
    print()
    
    # Step 6: Build configuration URLs
    print("Step 6: Building configuration URLs...")
    
    # Token endpoint (hosted UI domain)
    token_endpoint = f"https://{domain_prefix}.auth.{REGION}.amazoncognito.com/oauth2/token"
    
    # Discovery URL (IDP domain - CRITICAL for AgentCore)
    discovery_url = f"https://cognito-idp.{REGION}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
    
    print(f"✓ Token endpoint: {token_endpoint}")
    print(f"✓ Discovery URL: {discovery_url}")
    print()
    
    # Step 7: Save configuration
    print("Step 7: Saving configuration to cognito_config.json...")
    config = {
        "user_pool_id": user_pool_id,
        "domain_prefix": domain_prefix,
        "client_id": client_id,
        "client_secret": client_secret,
        "token_endpoint": token_endpoint,
        "discovery_url": discovery_url,
        "region": REGION
    }
    
    with open('cognito_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration saved to cognito_config.json")
    print()
    
    # Summary
    print("="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print(f"User Pool ID: {user_pool_id}")
    print(f"Domain Prefix: {domain_prefix}")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:20]}...")
    print()
    print("OAuth Scopes: gateway-api/read, gateway-api/write")
    print()
    print("Next steps:")
    print("1. Use this Cognito configuration to create an AgentCore Gateway")
    print("2. The gateway will use these credentials for authentication")
    print("3. Your agent will get OAuth tokens to securely call gateway tools")
    print("="*80)
    
except ClientError as e:
    print(f"❌ Error: {e}")
    print()
    print("If the user pool was partially created, you may need to clean up manually.")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
