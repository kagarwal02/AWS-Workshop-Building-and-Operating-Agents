#!/usr/bin/env python3
"""
Script to get CloudWatch log group information for agent logs.

Provides log group name and AWS CLI commands for viewing logs.
"""

import json
import os
from datetime import datetime

print("="*80)
print("CLOUDWATCH LOGS INFORMATION")
print("="*80)
print()

# Check if runtime config exists
if not os.path.exists('runtime_config.json'):
    print("✗ Error: Agent not deployed yet")
    print("  Please run 19_deploy_agent.py first")
    exit(1)

# Load configuration
print("Loading agent configuration...")
with open('runtime_config.json') as f:
    runtime_config = json.load(f)

agent_arn = runtime_config["agent_arn"]
agent_name = runtime_config["agent_name"]

# Extract agent ID from ARN
agent_id = agent_arn.split('/')[-1]

# Build log group name
log_group = f"/aws/bedrock-agentcore/runtimes/{agent_id}-DEFAULT"

# Get current date for log stream prefix
current_date = datetime.now().strftime("%Y/%m/%d")

print(f"✓ Agent: {agent_name}")
print(f"✓ Agent ID: {agent_id}")
print()

print("="*80)
print("LOG GROUP DETAILS")
print("="*80)
print()
print(f"Log Group: {log_group}")
print(f"Region: us-west-2")
print(f"Log Stream Prefix: {current_date}/[runtime-logs]")
print()

print("="*80)
print("AWS CLI COMMANDS")
print("="*80)
print()

# Tail logs (real-time)
tail_command = f'aws logs tail {log_group} --follow --region us-west-2'
print("1. Tail logs (real-time):")
print(f"   {tail_command}")
print()

# View recent logs
recent_command = f'aws logs tail {log_group} --since 1h --region us-west-2'
print("2. View recent logs (last hour):")
print(f"   {recent_command}")
print()

# View logs from specific time
time_command = f'aws logs tail {log_group} --since 30m --region us-west-2'
print("3. View logs from last 30 minutes:")
print(f"   {time_command}")
print()

# Filter logs
filter_command = f'aws logs tail {log_group} --filter-pattern "ERROR" --region us-west-2'
print("4. Filter logs (errors only):")
print(f"   {filter_command}")
print()

print("="*80)
print("CONSOLE ACCESS")
print("="*80)
print()
console_url = f"https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#logsV2:log-groups/log-group/{log_group.replace('/', '$252F')}"
print("View logs in AWS Console:")
print(f"  {console_url}")
print()

print("="*80)
print("WHAT TO LOOK FOR IN LOGS")
print("="*80)
print()
print("Agent Initialization:")
print("  - 'AGENTCORE RUNTIME AGENT: returns_agent_runtime'")
print("  - 'Model initialized'")
print("  - 'Memory ID loaded'")
print("  - 'Gateway configured'")
print()
print("Request Processing:")
print("  - 'AGENT INVOCATION'")
print("  - 'User input: ...'")
print("  - 'Processing...'")
print("  - Tool calls (lookup_order, check_return_eligibility, etc.)")
print()
print("Memory Operations:")
print("  - 'Memory session manager configured'")
print("  - Memory retrievals from namespaces")
print()
print("Gateway Operations:")
print("  - 'Gateway configured: ...'")
print("  - 'Loaded X gateway tool(s)'")
print("  - Tool invocations via gateway")
print()
print("Errors:")
print("  - 'Error: ...'")
print("  - Stack traces")
print("  - 'Agent invocation failed'")
print()

print("="*80)
print("TROUBLESHOOTING TIPS")
print("="*80)
print()
print("If you see errors in logs:")
print()
print("1. Authentication errors:")
print("   - Check Cognito credentials")
print("   - Verify OAuth scopes")
print()
print("2. Memory errors:")
print("   - Verify MEMORY_ID environment variable")
print("   - Check memory exists and is accessible")
print()
print("3. Gateway errors:")
print("   - Verify GATEWAY_URL is correct")
print("   - Check gateway targets are registered")
print("   - Verify OAuth token has correct scopes")
print()
print("4. Knowledge Base errors:")
print("   - Verify KNOWLEDGE_BASE_ID is correct")
print("   - Check KB exists and is accessible")
print()
print("5. Model errors:")
print("   - Check execution role has bedrock:InvokeModel permission")
print("   - Verify model ID is correct")
print()
print("="*80)
print()
print("Quick Start:")
print(f"  aws logs tail {log_group} --follow --region us-west-2")
print()
print("="*80)
