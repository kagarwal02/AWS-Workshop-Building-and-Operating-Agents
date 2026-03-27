#!/usr/bin/env python3
"""
Script to test memory retrieval from AgentCore Memory.

This script retrieves and displays what the agent remembers about a customer.
"""

import json

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

print("="*60)
print("AgentCore Memory Retrieval Test")
print("="*60)
print(f"Memory ID: {memory_id}")
print(f"Customer ID: user_001")
print(f"Region: us-west-2")
print()

# Create memory client
memory_client = MemoryClient(region_name='us-west-2')

# Retrieve memories from preferences namespace
print("─" * 60)
print("RETRIEVING: User Preferences")
print("─" * 60)
print(f"Namespace: app/user_001/preferences")
print(f"Query: 'customer preferences and communication'")
print()

try:
    memories = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/preferences",
        query="customer preferences and communication",
        top_k=3,
        # relevance_score=0.2
    )
    
    if memories:
        print(f"✓ Retrieved {len(memories)} preference memories")
        print()
        
        for i, memory in enumerate(memories, 1):
            print(f"Preference Memory {i}:")
            print(f"  {'─' * 56}")
            content = memory.get('content', {})
            if isinstance(content, dict):
                text = content.get('text', 'N/A')
            else:
                text = str(content)
            print(f"  Content: {text}")
            
            relevance = memory.get('relevanceScore', 'N/A')
            if isinstance(relevance, (int, float)):
                print(f"  Relevance Score: {relevance:.3f}")
            else:
                print(f"  Relevance Score: {relevance}")
            print()
    else:
        print("⚠️  No preference memories found")
        print("   Memory extraction may still be processing (takes 20-30 seconds)")
        print()
        
except Exception as e:
    print(f"❌ Error retrieving preferences: {e}")
    print()

# Also retrieve from semantic namespace
print("─" * 60)
print("RETRIEVING: Semantic Memories (Facts)")
print("─" * 60)
print(f"Namespace: app/user_001/semantic")
print(f"Query: 'customer preferences and communication'")
print()

try:
    semantic_memories = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="app/user_001/semantic",
        query="customer preferences and communication",
        top_k=3,
        # relevance_score=0.2
    )
    
    if semantic_memories:
        print(f"✓ Retrieved {len(semantic_memories)} semantic memories")
        print()
        
        for i, memory in enumerate(semantic_memories, 1):
            print(f"Semantic Memory {i}:")
            print(f"  {'─' * 56}")
            content = memory.get('content', {})
            if isinstance(content, dict):
                text = content.get('text', 'N/A')
            else:
                text = str(content)
            print(f"  Content: {text}")
            
            relevance = memory.get('relevanceScore', 'N/A')
            if isinstance(relevance, (int, float)):
                print(f"  Relevance Score: {relevance:.3f}")
            else:
                print(f"  Relevance Score: {relevance}")
            print()
    else:
        print("⚠️  No semantic memories found")
        print()
        
except Exception as e:
    print(f"❌ Error retrieving semantic memories: {e}")
    print()

print("="*60)
print("Memory Test Complete")
print("="*60)
