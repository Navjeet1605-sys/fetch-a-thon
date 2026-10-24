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
    from Agents.WebSearchAgent.protocol import SearchRequest, SearchResponse
    from Agents.WebSearchAgent.search_agent import execute_search_and_summarize
except ImportError:
    from protocol import SearchRequest, SearchResponse
    from search_agent import execute_search_and_summarize

AGENT_PORT = 8001
AGENT_ENDPOINT = f"http://127.0.0.1:{AGENT_PORT}/submit"

def query_web_search(query: str, max_results: int = 5) -> str:
    """
    Synchronous interface for O.M.N.I.S.
    Attempts to query the live Fetch.ai Web Search Agent; if not reachable,
    falls back cleanly to direct in-process search execution.
    """
    try:
        # Check if uagents query is possible
        from uagents.query import query as uagent_query
        import json

        req = SearchRequest(query=query, max_results=max_results)
        
        # Async query runner
        async def _ask_agent():
            response = await uagent_query(
                destination=AGENT_ENDPOINT,
                message=req,
                timeout=10
            )
            if response:
                try:
                    payload = json.loads(response.decode_payload())
                    return payload.get("summary", "")
                except Exception:
                    return str(response)
            return None

        # Try communicating with running agent
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
    result = execute_search_and_summarize(query, max_results)
    return result.get("summary", "I was unable to find any information on that.")

if __name__ == "__main__":
    q = "What is the latest price of Ethereum?"
    print(f"Testing WebSearchClient with query: '{q}'")
    answer = query_web_search(q)
    print(f"\nResponse:\n{answer}")
