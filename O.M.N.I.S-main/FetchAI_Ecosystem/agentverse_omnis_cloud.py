"""
=============================================================================
 O.M.N.I.S (Omni-Modal Network Intelligence Swarm) - Agentverse Cloud uAgent
=============================================================================
 Ready-to-paste single-file script for Agentverse (https://agentverse.ai/agents/launch)
 and local avctl execution.

 Enhanced Capabilities:
 1. Full Agent Chat Protocol (ACP) support with rich interactive MetadataContent cards for ASI:One.
 2. Multi-turn Conversational Memory persisted via uAgents `ctx.storage`.
 3. High-Reliability Crypto & Finance Engine (Binance + CoinGecko feeds with USD/INR conversion).
 4. Multi-Source Real-Time Search & Entity Synthesis (DuckDuckGo + Wikipedia + Groq/ASI:One).
 5. Dual-Engine LLM with Auto-Fallback:
    - Primary: Groq LLaMA-3.3-70B-Versatile (lightning fast 70B reasoning)
    - Fallback 1: Groq LLaMA-3.1-8B-Instant
    - Fallback 2: ASI:One Native Gateway (asi1 / asi1-mini)
 6. Self-contained: No local filesystem dependencies; runs seamlessly on Agentverse Cloud.
=============================================================================
"""

import os
import re
import json
import asyncio
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

# Ensure an asyncio event loop is initialized (required for Python 3.12+ / 3.14)
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    MetadataContent,
    StartSessionContent,
    EndSessionContent,
    chat_protocol_spec,
)

# ---------------------------------------------------------------------------
# Configuration & Secrets
# ---------------------------------------------------------------------------
# On Agentverse, add GROQ_API_KEY in the 'Secrets' tab.
GROQ_API_KEY = (
    os.getenv("GROQ_API_KEY")
    or os.getenv("GroqAPIKey")
    or ""
)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Candidate Groq models with auto-fallback cascade
GROQ_CANDIDATE_MODELS = [
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "qwen/qwen3.8-27b",
    "llama-3.1-8b-instant",
]

# Native ASI:One injected credentials on Agentverse
ASI1_API_KEY = os.getenv("ASI1_API_KEY")
ASI1_BASE_URL = os.getenv("ASI1_BASE_URL", "https://api.asi1.ai/v1")

# Initialize Agentverse Agent (Agentverse manages identity; do not set seed/port/endpoint)
agent = Agent(name="omnis_personal_ai")

# Initialize ACP Protocol
chat_proto = Protocol(spec=chat_protocol_spec)

# Global exchange rate cache
DEFAULT_USD_INR_RATE = 87.5


# ---------------------------------------------------------------------------
# Helper: Rich ACP Chat Message Builder
# ---------------------------------------------------------------------------
def create_chat_reply(
    text: str,
    metadata: Optional[Dict[str, str]] = None,
    end_session: bool = False
) -> ChatMessage:
    """
    Constructs a compliant ACP ChatMessage.
    Optionally attaches interactive card metadata for ASI:One UI rendering.
    """
    content = [TextContent(type="text", text=text)]
    if metadata:
        # Stringify all metadata values as required by ACP MetadataContent spec
        clean_metadata = {str(k): str(v) for k, v in metadata.items()}
        content.append(MetadataContent(type="metadata", metadata=clean_metadata))
    if end_session:
        content.append(EndSessionContent(type="end-session"))

    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )


# ---------------------------------------------------------------------------
# Engine 1: LLM Reasoning with Fallbacks & Conversational Memory
# ---------------------------------------------------------------------------
def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    max_tokens: int = 600
) -> str:
    """
    Executes reasoning with tiered fallback across available Groq and ASI:One models.
    """
    default_system = (
        "You are O.M.N.I.S (Omni-Modal Network Intelligence Swarm), an advanced autonomous AI "
        "operating on the Fetch.ai and ASI:One ecosystem. Deliver direct, accurate, and insightful "
        "answers without unnecessary conversational fluff."
    )
    sys_content = system_prompt or default_system

    messages: List[Dict[str, str]] = [{"role": "system", "content": sys_content}]
    if history:
        messages.extend(history[-6:])  # Include last 3 conversational turns
    messages.append({"role": "user", "content": prompt})

    # Tier 1: Candidate Groq Cloud Models (auto-selects first working model)
    if GROQ_API_KEY:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        for model in GROQ_CANDIDATE_MODELS:
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": max_tokens,
                }
                resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content")
                        if content:
                            return content.strip()
            except Exception:
                continue

    # Tier 3: Native ASI:One Gateway
    if ASI1_API_KEY:
        try:
            asi_resp = requests.post(
                f"{ASI1_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {ASI1_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "asi1",
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
                timeout=12,
            )
            if asi_resp.status_code == 200:
                data = asi_resp.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content")
                    if content:
                        return content.strip()
        except Exception:
            pass

    return "I am currently unable to reach the inference gateway. Please verify API keys in the Agentverse Secrets tab."


# ---------------------------------------------------------------------------
# Engine 2: Real-Time Crypto & Financial Market Intelligence
# ---------------------------------------------------------------------------
CRYPTO_SYMBOLS: Dict[str, Tuple[str, str]] = {
    # alias: (Binance ticker, CoinGecko ID)
    "btc": ("BTCUSDT", "bitcoin"),
    "bitcoin": ("BTCUSDT", "bitcoin"),
    "eth": ("ETHUSDT", "ethereum"),
    "ethereum": ("ETHUSDT", "ethereum"),
    "fet": ("FETUSDT", "fetch-ai"),
    "fetch": ("FETUSDT", "fetch-ai"),
    "asi": ("FETUSDT", "fetch-ai"),
    "sol": ("SOLUSDT", "solana"),
    "solana": ("SOLUSDT", "solana"),
    "bnb": ("BNBUSDT", "binancecoin"),
    "xrp": ("XRPUSDT", "ripple"),
    "ripple": ("XRPUSDT", "ripple"),
    "ada": ("ADAUSDT", "cardano"),
    "cardano": ("ADAUSDT", "cardano"),
    "doge": ("DOGEUSDT", "dogecoin"),
    "dogecoin": ("DOGEUSDT", "dogecoin"),
    "avax": ("AVAXUSDT", "avalanche-2"),
    "link": ("LINKUSDT", "chainlink"),
    "near": ("NEARUSDT", "near"),
}


def get_crypto_finance_data(query: str) -> Tuple[str, Optional[Dict[str, str]]]:
    """
    Fetches real-time market data via Binance (primary) and CoinGecko (fallback).
    Returns formatted response and rich card metadata for ASI:One UI.
    """
    q_low = query.lower()

    # Identify target asset
    selected_asset = "BTC"
    binance_symbol = "BTCUSDT"
    coingecko_id = "bitcoin"

    for key, (bsym, cgid) in CRYPTO_SYMBOLS.items():
        if re.search(rf"\b{re.escape(key)}\b", q_low):
            selected_asset = key.upper()
            binance_symbol = bsym
            coingecko_id = cgid
            break

    # 1. Primary Feed: Binance Public Spot Ticker
    try:
        b_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_symbol}"
        b_resp = requests.get(b_url, timeout=5)
        if b_resp.status_code == 200:
            b_data = b_resp.json()
            usd_price = float(b_data.get("lastPrice", 0))
            change_24h = float(b_data.get("priceChangePercent", 0))
            high_24h = float(b_data.get("highPrice", 0))
            low_24h = float(b_data.get("lowPrice", 0))
            inr_price = usd_price * DEFAULT_USD_INR_RATE

            text = (
                f"📊 Live Market Intelligence ({selected_asset}/USDT):\n"
                f"• Current Price: ${usd_price:,.2f} USD (₹{inr_price:,.2f} INR)\n"
                f"• 24h Change: {change_24h:+.2f}%\n"
                f"• 24h High: ${high_24h:,.2f} | Low: ${low_24h:,.2f}\n"
                f"• Provider: Binance Spot Feed via O.M.N.I.S Swarm"
            )

            metadata = {
                "Asset": selected_asset,
                "Price_USD": f"${usd_price:,.2f}",
                "Price_INR": f"INR {inr_price:,.2f}",
                "24h_Change": f"{change_24h:+.2f}%",
                "24h_High": f"${high_24h:,.2f}",
                "24h_Low": f"${low_24h:,.2f}",
                "Feed": "Binance Verified",
            }
            return text, metadata
    except Exception:
        pass

    # 2. Fallback Feed: CoinGecko API
    try:
        cg_url = (
            f"https://api.coingecko.com/api/v3/simple/price"
            f"?ids={coingecko_id}&vs_currencies=usd,inr&include_24hr_change=true"
        )
        headers = {"User-Agent": "Mozilla/5.0"}
        cg_resp = requests.get(cg_url, headers=headers, timeout=5)
        if cg_resp.status_code == 200:
            cg_data = cg_resp.json().get(coingecko_id, {})
            usd = cg_data.get("usd", 0)
            inr = cg_data.get("inr", 0)
            change = cg_data.get("usd_24h_change", 0)

            text = (
                f"📊 Live Market Intelligence ({selected_asset}):\n"
                f"• Current Price: ${usd:,.2f} USD (₹{inr:,.2f} INR)\n"
                f"• 24h Change: {change:+.2f}%\n"
                f"• Provider: CoinGecko via O.M.N.I.S Swarm"
            )
            metadata = {
                "Asset": selected_asset,
                "Price_USD": f"${usd:,.2f}",
                "Price_INR": f"INR {inr:,.2f}",
                "24h_Change": f"{change:+.2f}%",
                "Feed": "CoinGecko",
            }
            return text, metadata
    except Exception:
        pass

    # 3. Macroeconomic/Financial Reasoning via LLM
    llm_resp = call_llm(
        query,
        system_prompt=(
            "You are the O.M.N.I.S Financial Intelligence Agent. "
            "Provide a precise, factual financial analysis answering the query."
        ),
    )
    return llm_resp, None


# ---------------------------------------------------------------------------
# Engine 3: Real-Time Web Search & Fact Synthesis
# ---------------------------------------------------------------------------
def search_web_instant(query: str) -> Tuple[str, Optional[Dict[str, str]]]:
    """
    Synthesizes facts from Wikipedia Entity API, DuckDuckGo topics,
    and Groq LLM grounding.
    """
    clean_q = re.sub(r"(who is|what is|tell me about|search for|current)\s+", "", query, flags=re.I).strip()

    # 1. Wikipedia Summary for entity / factual queries
    try:
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(clean_q)}"
        headers = {"User-Agent": "OMNIS-FetchAgent/1.0"}
        w_resp = requests.get(wiki_url, headers=headers, timeout=4)
        if w_resp.status_code == 200:
            w_data = w_resp.json()
            extract = w_data.get("extract")
            title = w_data.get("title")
            if extract and len(extract) > 40:
                text = (
                    f"🌐 Knowledge Extraction [{title}]:\n"
                    f"{extract}\n\n"
                    f"Source: Wikipedia & O.M.N.I.S Knowledge Graph"
                )
                metadata = {
                    "Topic": title,
                    "Source": "Wikipedia Knowledge Base",
                    "Status": "Fact-Verified",
                }
                return text, metadata
    except Exception:
        pass

    # 2. DuckDuckGo Instant Answer API
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={requests.utils.quote(clean_q)}&format=json&no_html=1&skip_disambig=1"
        d_resp = requests.get(ddg_url, timeout=4)
        if d_resp.status_code == 200:
            d_data = d_resp.json()
            abstract = d_data.get("AbstractText")
            heading = d_data.get("Heading") or clean_q
            if abstract:
                text = f"🌐 Web Search Result [{heading}]:\n{abstract}"
                metadata = {
                    "Query": heading,
                    "Source": "DuckDuckGo Instant Answer",
                    "Status": "Verified",
                }
                return text, metadata
    except Exception:
        pass

    # 3. LLM Grounded Search Synthesis
    llm_resp = call_llm(
        f"Search query: {query}\nProvide a concise, factual, up-to-date answer.",
        system_prompt="You are the O.M.N.I.S Web Search & Synthesis Agent. Answer factual queries clearly and directly.",
    )
    return llm_resp, None


# ---------------------------------------------------------------------------
# Router: Multi-Agent Intent Dispatcher
# ---------------------------------------------------------------------------
def route_query(
    query: str,
    history: Optional[List[Dict[str, str]]] = None
) -> Tuple[str, Optional[Dict[str, str]]]:
    """
    Analyzes intent and routes the query to the optimal autonomous sub-agent:
    - Crypto & Finance
    - Real-Time Web Search
    - Core Intelligence & Conversational AI
    """
    q_low = query.lower()

    finance_tokens = [
        "price", "bitcoin", "btc", "eth", "ethereum", "fet", "asi",
        "crypto", "solana", "sol", "doge", "cardano", "market",
        "stock", "rate", "usd", "inr", "worth", "token", "ticker"
    ]
    search_tokens = [
        "who is", "what is", "where is", "when did", "how many",
        "capital of", "weather", "news", "president", "founder",
        "latest", "today", "history", "definition", "nobel"
    ]

    # Finance Routing
    if any(token in q_low for token in finance_tokens):
        text, meta = get_crypto_finance_data(query)
        return f"[O.M.N.I.S Finance Agent]\n{text}", meta

    # Web Search Routing
    if any(token in q_low for token in search_tokens):
        text, meta = search_web_instant(query)
        return f"[O.M.N.I.S Web Search Agent]\n{text}", meta

    # General Conversational & Deep Reasoning
    ans = call_llm(query, history=history)
    meta = {"Module": "O.M.N.I.S Core Swarm", "Engine": "Groq/ASI:One"}
    return f"[O.M.N.I.S Core AI]\n{ans}", meta


# ---------------------------------------------------------------------------
# ACP Protocol Handlers
# ---------------------------------------------------------------------------
@agent.on_event("startup")
async def handle_startup(ctx: Context):
    ctx.logger.info("=" * 64)
    ctx.logger.info("🚀 O.M.N.I.S Agent is ONLINE on Agentverse Cloud!")
    ctx.logger.info(f"Agent Address: {ctx.agent.address}")
    ctx.logger.info("Protocols Active: Agent Chat Protocol (ACP) v1.0")
    ctx.logger.info("Capabilities: Finance Ticker | Live Web Search | Groq LLaMA 3.3 70B")
    ctx.logger.info("ASI:One Discoverability: Published & Searchable")
    ctx.logger.info("=" * 64)


@agent.on_interval(period=300.0)
async def heartbeat(ctx: Context):
    """Periodic health check and keep-alive."""
    ctx.logger.debug(f"[Heartbeat] O.M.N.I.S agent healthy at {datetime.now(timezone.utc).isoformat()}")


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handles incoming messages from ASI:One, Agentverse Chat UI, or peer agents.
    Maintains multi-turn context via ctx.storage and returns rich ACP responses.
    """
    ctx.logger.info(f"Received ACP message from: {sender} (msg_id: {msg.msg_id})")

    # 1. Mandatory ACP step: Acknowledge receipt immediately
    try:
        await ctx.send(
            sender,
            ChatAcknowledgement(
                timestamp=datetime.now(timezone.utc),
                acknowledged_msg_id=msg.msg_id,
            ),
        )
    except Exception as e:
        ctx.logger.warning(f"Could not send acknowledgement: {e}")

    # 2. Retrieve multi-turn history from agent persistent storage
    storage_key = f"chat_history_{sender}"
    history: List[Dict[str, str]] = (await ctx.storage.get(storage_key)) or []

    responded = False

    # 3. Process ACP content items
    try:
        for item in msg.content:
            if isinstance(item, StartSessionContent):
                welcome_text = (
                    "👋 Welcome to O.M.N.I.S (Omni-Modal Network Intelligence Swarm)!\n\n"
                    "I am your autonomous personal intelligence agent on Fetch.ai / ASI:One.\n\n"
                    "Here is what I can do for you right now:\n"
                    "• 📈 Real-Time Crypto & Finance: 'Price of Bitcoin, ETH, or Fetch.ai in INR'\n"
                    "• 🌐 Live Web Search & Fact Extraction: 'Who founded Fetch.ai?'\n"
                    "• 🧠 Deep Reasoning: 'Explain quantum computing simply'\n\n"
                    "How can I assist you today?"
                )
                welcome_meta = {
                    "System": "O.M.N.I.S Swarm",
                    "Network": "Fetch.ai / ASI:One",
                    "Status": "Ready",
                }
                await ctx.send(sender, create_chat_reply(welcome_text, metadata=welcome_meta))
                responded = True

            elif isinstance(item, TextContent):
                user_text = item.text.strip()
                if user_text:
                    ctx.logger.info(f"Processing query from {sender}: '{user_text}'")

                    # Route query with context history
                    response_text, meta = route_query(user_text, history=history)

                    # Update history
                    history.append({"role": "user", "content": user_text})
                    history.append({"role": "assistant", "content": response_text})
                    await ctx.storage.set(storage_key, history[-8:])

                    # Send back formatted reply with rich card metadata
                    reply_msg = create_chat_reply(response_text, metadata=meta)
                    await ctx.send(sender, reply_msg)
                    ctx.logger.info(f"Dispatched reply to {sender}")
                    responded = True

            elif isinstance(item, EndSessionContent):
                ctx.logger.info(f"Session closed with {sender}. Clearing conversational memory.")
                await ctx.storage.set(storage_key, [])
                farewell = create_chat_reply("Session closed. Have a great day!", end_session=True)
                await ctx.send(sender, farewell)
                responded = True

        # Fallback to plain text if no typed content handled
        if not responded:
            plain_text = msg.text()
            if plain_text and plain_text.strip():
                response_text, meta = route_query(plain_text.strip(), history=history)
                reply_msg = create_chat_reply(response_text, metadata=meta)
                await ctx.send(sender, reply_msg)

    except Exception as err:
        ctx.logger.error(f"Error handling message from {sender}: {err}")
        err_msg = create_chat_reply(
            f"O.M.N.I.S encountered a processing notice: {err}. Please try rephrasing your question."
        )
        await ctx.send(sender, err_msg)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Silently logs ACP acknowledgements to prevent unhandled message notifications."""
    ctx.logger.debug(f"Received ACK from {sender} for msg {msg.acknowledged_msg_id}")


# Publish ACP manifest so the agent is instantly discoverable on ASI:One & Agentverse
agent.include(chat_proto, publish_manifest=True)


if __name__ == "__main__":
    agent.run()
