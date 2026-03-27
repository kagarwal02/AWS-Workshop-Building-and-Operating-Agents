"""
Test script for returns_refunds_agent
Tests various customer service scenarios
"""

import importlib.util
import sys
import os

# Set environment variable for Knowledge Base ID
os.environ["KNOWLEDGE_BASE_ID"] = "W3TAAPOVCZ"

# Import run_agent from 01_returns_refunds_agent.py using importlib
spec = importlib.util.spec_from_file_location("returns_refunds_agent", "01_returns_refunds_agent.py")
agent_module = importlib.util.module_from_spec(spec)
sys.modules["returns_refunds_agent"] = agent_module
spec.loader.exec_module(agent_module)

# Get the run_agent function
run_agent = agent_module.run_agent

def print_test_header(test_num: int, question: str):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"TEST {test_num}: {question}")
    print("="*80)

def run_test(test_num: int, question: str):
    """Run a single test and print results"""
    print_test_header(test_num, question)
    try:
        response = run_agent(question)
        print("\nAGENT RESPONSE:")
        print("-" * 80)
        print(response)
        print("-" * 80)
        return True
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def main():
    """Run all test cases"""
    print("\n" + "🧪" * 40)
    print("RETURNS & REFUNDS AGENT - TEST SUITE")
    print("🧪" * 40)
    
    tests = [
        "What time is it?",
        "Can I return a laptop I purchased 25 days ago?",
        "Calculate my refund for a $500 item returned due to defect in like-new condition",
        "Explain the return policy for electronics in a simple way",
        "Use the retrieve tool to search the knowledge base for 'Amazon return policy for electronics'"
    ]
    
    results = []
    for i, test_question in enumerate(tests, 1):
        success = run_test(i, test_question)
        results.append((i, test_question, success))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    
    for test_num, question, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status} - Test {test_num}: {question[:60]}...")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*80)

if __name__ == "__main__":
    main()
