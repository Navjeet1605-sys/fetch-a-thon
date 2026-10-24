import sys
import os

# Add directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from Agents.agent_hub import interactive_cli

if __name__ == "__main__":
    interactive_cli()
