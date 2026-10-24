import os
import sys
import asyncio
from typing import Dict, Any

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Backend.Model import FirstLayerDMM
from Backend.Chatbot import ChatBot
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Agents.WebSearchAgent import query_web_search
from Agents.FinanceAgent import query_finance_agent

try:
    from Backend.Automation import Automation
except Exception:
    Automation = None

AUTOMATION_FUNCS = ["open", "close", "play", "volume", "content", "google search", "youtube search"]


def process_query(query: str, speak: bool = False) -> Dict[str, Any]:
    """
    Unified Agent Router:
    Takes any natural language query, uses the Cohere Decision-Making Model to
    classify the intent, delegates the task to the specialized agent, and returns the result.
    """
    if not query or not query.strip():
        return {"agent": "None", "response": "Empty query received."}

    query_clean = query.strip()
    
    # 1. Use Decision-Making Model (Cohere FirstLayerDMM)
    try:
        decisions = FirstLayerDMM(query_clean)
    except Exception as e:
        decisions = ["general " + query_clean]

    if not isinstance(decisions, list):
        decisions = [decisions]

    print(f"\n[DMM Router] Detected Intents: {decisions}")

    responses = []
    active_agent = "General Chatbot"

    # 2. Check for Automation tasks (e.g. open apps, play songs)
    for task in decisions:
        if Automation and any(task.startswith(func) for func in AUTOMATION_FUNCS):
            active_agent = "Desktop Automation Agent"
            try:
                asyncio.run(Automation([task]))
                responses.append(f"Executed automation command: {task}")
            except Exception as e:
                responses.append(f"Automation execution notice: {e}")

    # 3. Check for Specialized Agents
    for task in decisions:
        # A. Crypto & Finance Agent
        if task.startswith("finance"):
            active_agent = "Crypto & Finance Agent (Agentverse)"
            sub_query = task.replace("finance", "", 1).strip()
            answer = query_finance_agent(sub_query or query_clean)
            responses.append(answer)

        # B. Realtime Web Search Agent
        elif task.startswith("realtime") or task.startswith("google search"):
            active_agent = "Web Search Agent (DuckDuckGo + Groq)"
            sub_query = task.replace("realtime", "", 1).replace("google search", "", 1).strip()
            answer = query_web_search(sub_query or query_clean)
            responses.append(answer)

        # C. General Conversational Agent
        elif task.startswith("general"):
            active_agent = "Conversational AI Agent (Groq)"
            sub_query = task.replace("general", "", 1).strip()
            answer = ChatBot(sub_query or query_clean)
            responses.append(answer)

    # Fallback if no specific response was generated
    if not responses:
        active_agent = "Web Search Agent"
        answer = query_web_search(query_clean)
        responses.append(answer)

    final_answer = "\n\n".join(responses)

    return {
        "agent": active_agent,
        "query": query_clean,
        "decisions": decisions,
        "response": final_answer
    }


def interactive_cli():
    """Interactive Command Center for anyone to ask any question and let the agents work."""
    print("=" * 68)
    print(" 🤖 O.M.N.I.S Autonomous Multi-Agent Command Center")
    print("=" * 68)
    print("Ask ANYTHING: Financial data, live web search, facts, or system actions.")
    print("\nExamples you can try right now:")
    print("  • Finance/Crypto:   'What is the price of Bitcoin and Fetch.ai?'")
    print("  • Economics:        'What is the difference between stocks and bonds?'")
    print("  • Live Web Search:  'Who is the current Prime Minister of the UK?'")
    print("  • General Chat:     'Explain quantum computing in simple words'")
    print("  • System Action:    'Open notepad and google search artificial intelligence'")
    print("\nType 'exit' or 'quit' to close.\n")

    while True:
        try:
            user_input = input("\n[OMNIS] Ask any question >>> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye! O.M.N.I.S shutting down.")
                break

            print("\n🔄 Dispatching to Autonomous Agents...")
            result = process_query(user_input, speak=False)

            print(f"🎯 Assigned Agent: [{result['agent']}]")
            print(f"📝 Answer:\n{result['response']}")

        except KeyboardInterrupt:
            print("\nSession interrupted.")
            break
        except Exception as err:
            print(f"\nError processing query: {err}")


if __name__ == "__main__":
    interactive_cli()
