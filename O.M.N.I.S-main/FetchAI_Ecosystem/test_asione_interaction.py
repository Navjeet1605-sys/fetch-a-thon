import os
import sys

# Ensure path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Agents.agent_hub import process_query

def simulate_asione_interaction():
    print("=" * 70)
    print(" 🌐 Fetch-A-Thon 3.0: ASI:One & Agent Chat Protocol (ACP) Simulation")
    print("=" * 70)

    test_conversations = [
        ("User via ASI:One", "What is the live price of Bitcoin and Fetch.ai today?"),
        ("User via ASI:One", "Explain the difference between stocks and bonds for a beginner."),
        ("User via ASI:One", "Who won the latest Nobel Prize in Physics?"),
        ("User via ASI:One", "Hello OMNIS, what can you do as a multi-agent system?")
    ]

    for sender, prompt in test_conversations:
        print(f"\n[Incoming ACP Message] {sender}: '{prompt}'")
        print("  ├── 1. ChatAcknowledgement Sent (timestamp & msg_id)")
        print("  ├── 2. Intent Analysis via Cohere DMM Model...")
        result = process_query(prompt)
        print(f"  ├── 3. Orchestrated Agent: {result['agent']}")
        print(f"  └── 4. Reply Payload (ACP TextContent):")
        print(f"\n{result['response']}\n")
        print("-" * 70)

if __name__ == "__main__":
    simulate_asione_interaction()
