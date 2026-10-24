import os
import sys
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None
import requests
from dotenv import dotenv_values
from groq import Groq

# Ensure current folder is in path for protocol imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from protocol import SearchRequest, SearchResponse

# Load environment variables
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(CURRENT_DIR)), ".env")
env_vars = dotenv_values(ENV_PATH) if os.path.exists(ENV_PATH) else {}
GroqAPIKey = env_vars.get("GroqAPIKey") or os.environ.get("GroqAPIKey")

# Initialize Groq client if key is available
groq_client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None


def execute_search_and_summarize(query: str, max_results: int = 5) -> dict:
    """Core logic to search the web and produce a speech-friendly summary."""
    sources = []
    snippets = []

    # 1. Fetch search results from DuckDuckGo or Wikipedia fallback
    if DDGS:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                for item in results:
                    title = item.get("title", "")
                    body = item.get("body", "")
                    href = item.get("href", "")
                    sources.append(href or title)
                    snippets.append(f"Title: {title}\nSnippet: {body}")
        except Exception as e:
            snippets.append(f"DDGS lookup note: {e}")

    # Fallback to direct Wikipedia/DDG API if snippets are empty
    if not snippets:
        try:
            w_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(query)}"
            r = requests.get(w_url, headers={"User-Agent": "OMNIS/1.0"}, timeout=4)
            if r.status_code == 200:
                extract = r.json().get("extract")
                if extract:
                    snippets.append(f"Source: Wikipedia\nSummary: {extract}")
                    sources.append("https://en.wikipedia.org")
        except Exception:
            pass

    raw_context = "\n\n".join(snippets)

    # 2. Synthesize using Groq for voice-friendly summary
    if groq_client and raw_context:
        try:
            prompt = f"""You are the Web Search Agent for the O.M.N.I.S assistant.
Based strictly on the following web search results, provide a clear, accurate, direct, and concise summary (2-3 sentences max) that can be easily read aloud to the user via Text-to-Speech.
Do not use markdown links, asterisks, bullet points, or filler words.

Query: {query}

Search Results:
{raw_context}
"""
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=250,
            )
            summary = completion.choices[0].message.content.strip()
            # Normalize whitespace/unicode to be friendly with all consoles and TTS
            summary = summary.replace('\u202f', ' ').replace('\xa0', ' ').replace('\u2013', '-').replace('\u2014', '-')
            return {"query": query, "summary": summary, "sources": sources}
        except Exception as e:
            pass

    # Fallback if Groq is not available or fails
    fallback_summary = snippets[0] if snippets else "No relevant information found."
    fallback_summary = fallback_summary.replace('\u202f', ' ').replace('\xa0', ' ')
    return {"query": query, "summary": fallback_summary, "sources": sources}



# Try setting up Fetch.ai uAgent
try:
    from uagents import Agent, Context

    AGENT_SEED = "omnis_web_search_agent_seed_2026"
    AGENT_PORT = 8001

    agent = Agent(
        name="web_search_agent",
        port=AGENT_PORT,
        seed=AGENT_SEED,
        endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
    )

    @agent.on_event("startup")
    async def introduce(ctx: Context):
        ctx.logger.info(f"O.M.N.I.S Web Search Agent is LIVE!")
        ctx.logger.info(f"Agent Address: {agent.address}")
        ctx.logger.info(f"Listening on port: {AGENT_PORT}")

    @agent.on_message(model=SearchRequest, replies={SearchResponse})
    async def handle_search(ctx: Context, sender: str, msg: SearchRequest):
        ctx.logger.info(f"Received search task: '{msg.query}' from {sender}")
        result = execute_search_and_summarize(msg.query, msg.max_results)
        response = SearchResponse(
            query=result["query"],
            summary=result["summary"],
            sources=result["sources"]
        )
        await ctx.send(sender, response)
        ctx.logger.info(f"Responded to {sender} with summary.")

except Exception as err:
    agent = None


if __name__ == "__main__":
    if agent:
        print(f"Starting standalone Fetch.ai Web Search Agent...")
        agent.run()
    else:
        print("Running in direct execution mode (uagents framework not initialized).")
        test_q = "What is Fetch.ai uagents?"
        res = execute_search_and_summarize(test_q)
        print(f"Query: {test_q}\nResult: {res['summary']}")
