#!/usr/bin/env python3
"""
Script to seed AgentCore Memory with sample customer conversations.

This script stores sample conversations to demonstrate memory capabilities.
"""

import json
import time

try:
    from bedrock_agentcore.memory import MemoryClient
except ImportError:
    print("✗ Error: bedrock_agentcore package not found")
    print("  Install with: pip install bedrock-agentcore")
    exit(1)

# Load memory_id from config
with open('memory_config.json') as f:
    config = json.load(f)
    memory_id = config['memory_id']

print(f"Using Memory ID: {memory_id}")
print(f"Customer ID: user_001")
print()

# Create memory client
memory_client = MemoryClient(region_name='us-west-2')

# Conversation 1: Customer mentions preferences and past return
print("Storing Conversation 1: Customer preferences and past return...")
messages_1 = [
    ("I prefer email notifications for all updates. I previously returned a defective laptop last month.", "USER"),
    ("Thank you for letting me know. I've noted your preference for email notifications. I can help you with any questions about your previous laptop return or future returns.", "ASSISTANT")
]

memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_001",
    messages=messages_1
)
print(f"✓ Stored {len(messages_1)} messages from conversation 1")

# Conversation 2: Customer asks about return windows
print("\nStoring Conversation 2: Return window inquiry...")
messages_2 = [
    ("What's the return window for electronics? I'm thinking about buying a tablet.", "USER"),
    ("For most electronics, Amazon offers a 30-day return window from the date of delivery. This applies to tablets, laptops, and similar devices. Would you like more details about the return policy?", "ASSISTANT"),
    ("Yes, that's helpful. Good to know I have 30 days.", "USER")
]

memory_client.create_event(
    memory_id=memory_id,
    actor_id="user_001",
    session_id="session_002",
    messages=messages_2
)
print(f"✓ Stored {len(messages_2)} messages from conversation 2")

# Wait for memory processing
print("\n" + "="*60)
print("Note: Memory processing takes 20-30 seconds to:")
print("  - Extract user preferences → USER_PREFERENCE namespace")
print("  - Identify facts → SEMANTIC namespace")
print("  - Generate summaries → SUMMARY namespace")
print("="*60)
print("\nWaiting 30 seconds for memory processing...")

for i in range(30, 0, -5):
    print(f"  {i} seconds remaining...")
    time.sleep(5)

print("\n✓ Memory processing complete!")
print("\nMemory now contains:")
print("  - User preference: email notifications")
print("  - Past interaction: returned defective laptop")
print("  - Knowledge: interested in electronics return windows")
