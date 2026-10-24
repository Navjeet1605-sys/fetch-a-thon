import os
import sys
import requests
from dotenv import dotenv_values
from groq import Groq

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
except ImportError:
    from protocol import FinanceQA, Response

# Target Agent Address on Agentverse Marketplace
AGENTVERSE_FINANCE_AGENT = "agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl"

# Load environment variables
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(CURRENT_DIR)), ".env")
env_vars = dotenv_values(ENV_PATH) if os.path.exists(ENV_PATH) else {}
GroqAPIKey = env_vars.get("GroqAPIKey") or os.environ.get("GroqAPIKey")

groq_client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None


def get_live_crypto_price(query: str) -> str:
    """Check CoinGecko free API for live crypto prices if query mentions crypto."""
    q_lower = query.lower()
    crypto_map = {
        "bitcoin": "bitcoin",
        "btc": "bitcoin",
        "ethereum": "ethereum",
        "eth": "ethereum",
        "fetch": "fetch-ai",
        "fet": "fetch-ai",
        "asi": "fetch-ai",
        "solana": "solana",
        "sol": "solana",
        "doge": "dogecoin",
        "dogecoin": "dogecoin",
        "cardano": "cardano",
        "ada": "cardano",
        "ripple": "ripple",
        "xrp": "ripple"
    }

    for token, coin_id in crypto_map.items():
        if token in q_lower:
            try:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,inr&include_24hr_change=true"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json().get(coin_id, {})
                    usd_val = data.get("usd")
                    inr_val = data.get("inr")
                    change = data.get("usd_24h_change", 0)
                    if usd_val:
                        sign = "+" if change >= 0 else ""
                        return (f"The current live price of {token.upper()} is ${usd_val:,.2f} USD "
                                f"(approx ₹{inr_val:,.2f} INR), with a 24-hour change of {sign}{change:.2f}%.")
            except Exception:
                pass
    return ""


def execute_finance_qa(question: str) -> str:
    """Answers finance, economics, crypto, and market questions with TTS-friendly format."""
    # 1. Fast-path: Check live crypto ticker price first
    crypto_price = get_live_crypto_price(question)
    if crypto_price and ("price" in question.lower() or "rate" in question.lower() or "worth" in question.lower()):
        return crypto_price

    # 2. Financial Economics & Market Explanation via Groq
    if groq_client:
        try:
            prompt = f"""You are the official Finance & Economics AI Agent for O.M.N.I.S.
Answer the following question about finance, stock markets, macroeconomics, or cryptocurrency clearly, concisely, and accurately.
Provide a direct, conversational explanation (2 to 3 sentences maximum) suitable to be read aloud via Text-to-Speech.
Do not use markdown links, asterisks, bullet points, or filler phrases.

Question: {question}
"""
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=250,
            )
            answer = completion.choices[0].message.content.strip()
            answer = answer.replace('\u202f', ' ').replace('\xa0', ' ').replace('\u2013', '-').replace('\u2014', '-')
            return answer
        except Exception as e:
            pass

    # Fallback to web search agent if available
    try:
        from Agents.WebSearchAgent import query_web_search
        return query_web_search(question)
    except Exception:
        return "I am currently unable to retrieve the latest financial information."


# Setup Fetch.ai uAgent runner
try:
    from uagents import Agent, Context

    AGENT_SEED = "omnis_finance_agent_seed_2026"
    AGENT_PORT = 8002

    agent = Agent(
        name="finance_agent",
        port=AGENT_PORT,
        seed=AGENT_SEED,
        endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
    )

    @agent.on_event("startup")
    async def introduce(ctx: Context):
        ctx.logger.info("O.M.N.I.S Finance Agent is LIVE!")
        ctx.logger.info(f"Local Agent Address: {agent.address}")
        ctx.logger.info(f"Target Agentverse Address: {AGENTVERSE_FINANCE_AGENT}")
        ctx.logger.info(f"Listening on port: {AGENT_PORT}")

    @agent.on_message(model=FinanceQA, replies={Response})
    async def handle_finance_qa(ctx: Context, sender: str, msg: FinanceQA):
        ctx.logger.info(f"Received finance question: '{msg.question}' from {sender}")
        answer_text = execute_finance_qa(msg.question)
        await ctx.send(sender, Response(text=answer_text))

except Exception:
    agent = None


if __name__ == "__main__":
    if agent:
        print("Starting standalone Fetch.ai Finance Agent...")
        agent.run()
    else:
        test_q = "What causes inflation?"
        print(f"Direct Mode Testing: '{test_q}'")
        res = execute_finance_qa(test_q)
        print(f"Answer:\n{res}")
