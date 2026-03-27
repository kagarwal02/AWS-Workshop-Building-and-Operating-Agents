#!/usr/bin/env python3
"""
Script to get CloudWatch GenAI Observability dashboard URL.

Provides access to monitoring and tracing for your deployed agent.
"""

import json
import os

print("="*80)
print("CLOUDWATCH GENAI OBSERVABILITY DASHBOARD")
print("="*80)
print()

# Load runtime config if available
agent_name = "returns_refunds_agent"
agent_arn = None

if os.path.exists('runtime_config.json'):
    try:
        with open('runtime_config.json') as f:
            runtime_config = json.load(f)
            agent_name = runtime_config.get('agent_name', agent_name)
            agent_arn = runtime_config.get('agent_arn')
        print(f"Agent: {agent_name}")
        if agent_arn:
            print(f"ARN: {agent_arn}")
        print()
    except:
        pass

# Build dashboard URL
region = "us-west-2"
dashboard_url = f"https://console.aws.amazon.com/cloudwatch/home?region={region}#gen-ai-observability/agent-core"

print("Dashboard Access:")
print(f"  URL: {dashboard_url}")
print(f"  Region: {region}")
print()

print("="*80)
print("DASHBOARD FEATURES")
print("="*80)
print()
print("The GenAI Observability dashboard provides:")
print()
print("1. Request Tracing:")
print("   - Complete conversation flow")
print("   - Tool invocations (lookup_order, check_return_eligibility, etc.)")
print("   - Memory retrievals")
print("   - Gateway calls")
print("   - Knowledge Base queries")
print()
print("2. Performance Metrics:")
print("   - Response times")
print("   - Success rates")
print("   - Error rates")
print("   - Token usage")
print()
print("3. Session History:")
print("   - User interactions")
print("   - Conversation threads")
print("   - Actor-based filtering")
print()
print("4. Debugging:")
print("   - Error patterns")
print("   - Bottleneck identification")
print("   - Tool performance")
print()
print("="*80)
print("LOG ACCESS")
print("="*80)
print()
print("CloudWatch Logs:")
print(f"  Log Group: /aws/bedrock-agentcore/runtime/{agent_name}")
print(f"  Region: {region}")
print()
print("View logs with AWS CLI:")
print(f"  aws logs tail /aws/bedrock-agentcore/runtime/{agent_name} --follow --region {region}")
print()
print("="*80)
print("QUICK START")
print("="*80)
print()
print("1. Open the dashboard URL in your browser")
print("2. Sign in to AWS Console if prompted")
print("3. Navigate to 'Agent Core' section")
print("4. Filter by your agent name or ARN")
print("5. View traces, metrics, and logs")
print()
print("Dashboard URL:")
print(f"  {dashboard_url}")
print()
print("="*80)
