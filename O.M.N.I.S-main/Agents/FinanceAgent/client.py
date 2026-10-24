import os
import sys
import asyncio

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

try:
    from Agents.FinanceAgent.protocol import FinanceQA, Response
    from Agents.FinanceAgent.finance_agent import execute_finance_qa, AGENTVERSE_FINANCE_AGENT
except ImportError:
    from protocol import FinanceQA, Response
    from finance_agent import execute_finance_qa, AGENTVERSE_FINANCE_AGENT

AGENT_PORT = 8002
AGENT_ENDPOINT = f"http://127.0.0.1:{AGENT_PORT}/submit"

def query_finance_agent(question: str) -> str:
    """
    Synchronous interface for O.M.N.I.S.
    Attempts to query the running Fetch.ai Finance Agent;
    falls back cleanly to in-process financial reasoning and real-time live price lookups.
    """
    try:
        from uagents.query import query as uagent_query
        import json

        req = FinanceQA(question=question)

        async def _ask_agent():
            response = await uagent_query(
                destination=AGENT_ENDPOINT,
                message=req,
                timeout=10
            )
            if response:
                try:
                    payload = json.loads(response.decode_payload())
                    return payload.get("text", "")
                except Exception:
                    return str(response)
            return None

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(_ask_agent(), loop)
                res = future.result(timeout=10)
            else:
                res = asyncio.run(_ask_agent())
            if res:
                return res
        except Exception:
            pass
    except ImportError:
        pass

    # Seamless fallback: execute logic directly
    return execute_finance_qa(question)


if __name__ == "__main__":
    test_queries = [
        "What is the difference between stocks and bonds?",
        "What is the current Bitcoin price?"
    ]
    for q in test_queries:
        print(f"\n--- Question: '{q}' ---")
        answer = query_finance_agent(q)
        print(f"Answer:\n{answer}")
