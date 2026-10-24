# Hosted uAgents reference

Curated patterns for Agentverse hosted agents. Agentverse manages identity — never set seed, mailbox, port, or endpoint in code. Do not use Bureau.

## Valid imports

Copy these import paths exactly — do not invent modules:

- from uagents import Agent
- from uagents import Context
- from uagents import Model
- from uagents import Protocol
- from uagents import Field
- from uagents.experimental.chat_agent import ChatAgent
- from uagents.experimental.quota import QuotaProtocol
- from uagents.experimental.dialogues import Dialogue
- from uagents_core.contrib.protocols.chat import ChatAcknowledgement, ChatMessage, MetadataContent, TextContent, chat_protocol_spec
- from openai import OpenAI (ASI:One and other OpenAI-compatible endpoints — see Pattern F)

## File layout

- **agent.py** — always required. Minimal bootstrap: `Agent()` or `ChatAgent()`, imports, `agent.include(...)`, `if __name__ == "__main__": agent.run()`.
- **protocols.py** — optional. Protocol handlers and Model classes for multi-file agents.
- **http_client.py** — optional. External HTTP/API calls; import functions from agent.py or protocols.py. Never name this file `requests.py` — that shadows the pip `requests` package and breaks `import requests` / `requests.RequestException`.
- **.env** — always include; keep empty unless secrets are required (use placeholder comments only).

Secrets and env vars can be loaded in the code with os.environ. Document anything the user needs to add in the README.

Agentverse injects `ASI1_API_KEY` and `ASI1_BASE_URL` into every hosted agent, so read those from `os.environ` and never ask the user for a key. `ChatAgent()` picks them up on its own; pass `LLMConfig.asi1(model="asi1-ultra")` only to choose a different model. A plain `Agent()` calls the model through an OpenAI client — see Pattern F. Calls are metered against the owner's LLM token quota.

## Readme (markdown)

The `readme` field is shown on the agent profile and used for marketplace discovery. Write clear markdown with:

- **Overview** — what the agent does and who it is for
- **Features** — bullet list of main capabilities
- **Limitations** — optional caveats (API keys, rate limits, scope)

Starter prompts (example messages users can send to call the agent) are returned separately in the `starter_prompts` JSON field — do not include them in the readme.

The short profile description is returned separately in the `description` JSON field — plain text only, no markdown.

Keep dependencies to the uAgents standard library only (stdlib `requests` is acceptable for HTTP).

## Pattern A: Plain-text chat (Agentverse chat UI)

Use `Agent()` with the chat protocol — not `@agent.on_message()`.

```python
# agent.py
from datetime import datetime
from uuid import uuid4

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

agent = Agent()
protocol = Protocol(spec=chat_protocol_spec)


@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )
    text = msg.text()
    if not text:
        return
    reply = f"You said: {text}"
    content = [TextContent(type="text", text=reply)]
    await ctx.send(
        sender,
        ChatMessage(timestamp=datetime.utcnow(), msg_id=uuid4(), content=content),
    )


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass


agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
```

Rules:
- Every file must import every name it uses (stdlib, third-party, and local). Imports are per-file and do not carry across modules.
- Handler signature: `async def handle_message(ctx: Context, sender: str, msg: ChatMessage)`
- Always acknowledge incoming messages before replying
- Never construct `ChatMessage` with `text=` or `type=` kwargs — use `TextContent` in a `content` list
- Interactive cards: use `MetadataContent(type="metadata", metadata={...})` — the field is `metadata`, never `data` (`data=` raises TypeError)
- End with `agent.include(protocol, publish_manifest=True)`

## Pattern B: Structured chat (ChatAgent + QuotaProtocol)

Use when the agent extracts typed fields from plain-text user messages into Model classes.

```python
# agent.py
from uagents import Context, Model
from uagents.experimental.chat_agent import ChatAgent
from uagents.experimental.quota import QuotaProtocol

agent = ChatAgent()


class SquareRequest(Model):
    number: int


class SquareResponse(Model):
    number: int
    square: int


proto = QuotaProtocol(
    storage_reference=agent.storage, name="Simple-ChatAgent", version="0.1.0"
)


@proto.on_message(model=SquareRequest, replies=SquareResponse)
async def square_handler(ctx: Context, sender: str, msg: SquareRequest):
    await ctx.send(
        sender, SquareResponse(number=msg.number, square=msg.number * msg.number)
    )


agent.include(proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
```

`uagents.experimental.dialogues` exports `Dialogue` for multi-step protocols, not `ChatAgent`.

## Pattern C: Periodic and startup tasks

Use `@agent.on_event("startup")` for one-shot initialization, or `@agent.on_interval(period=...)` for recurring work.

```python
# agent.py
from uagents import Agent, Context

agent = Agent()


@agent.on_event("startup")
async def say_hello(ctx: Context):
    ctx.logger.info(f"Hello from {ctx.agent.address}")


@agent.on_interval(period=60.0)
async def tick(ctx: Context):
    ctx.logger.info("Tick")


if __name__ == "__main__":
    agent.run()
```

Use `ctx.storage.get()` / `ctx.storage.set()` to persist state between interval runs.

## Pattern D: Agent-to-agent messaging

Define Model classes with Field descriptions. Use `@agent.on_message(model=...)` or a custom Protocol.

```python
# agent.py
from uagents import Agent, Context, Field, Model

agent = Agent()


class GreetingRequest(Model):
    message: str = Field(description="Greeting text to log")


class GreetingResponse(Model):
    reply: str = Field(description="Reply message")


@agent.on_message(model=GreetingRequest, replies=GreetingResponse)
async def handle_greeting(ctx: Context, sender: str, msg: GreetingRequest):
    ctx.logger.info(f"Received from {sender}: {msg.message}")
    await ctx.send(sender, GreetingResponse(reply=f"Hello back! You said: {msg.message}"))


if __name__ == "__main__":
    agent.run()
```

For multi-file agents, put models and protocol handlers in `protocols.py` and import them from `agent.py`.

## Pattern E: External HTTP (multi-file)

Keep HTTP calls in `http_client.py`. Import helper functions where needed. Only `http_client.py` may `import requests` (the pip package). Other files must use `from http_client import ...`, never `import requests`.

```python
# http_client.py
import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast?"


def fetch_temperature(latitude: float, longitude: float, hour: int = 12) -> float | None:
    url = (
        OPEN_METEO_URL
        + f"latitude={latitude}&longitude={longitude}"
        + "&hourly=temperature_2m&forecast_days=1"
    )
    try:
        response = requests.get(url=url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["hourly"]["temperature_2m"][hour]
    except requests.RequestException:
        return None
```

```python
# agent.py
from uagents import Agent, Context

from http_client import fetch_temperature

agent = Agent()

LATITUDE = 52.2
LONGITUDE = 0.1


@agent.on_event("startup")
async def report_weather(ctx: Context):
    temp = fetch_temperature(LATITUDE, LONGITUDE)
    if temp is not None:
        ctx.logger.info(f"Local temperature: {temp}°C")


if __name__ == "__main__":
    agent.run()
```

For protocol-based agents that call external APIs, put the protocol and models in `protocols.py`:

```python
# protocols.py
from uagents import Context, Field, Model, Protocol

from http_client import fetch_temperature

weather_protocol = Protocol("Weather")


class WeatherRequest(Model):
    latitude: float = Field(description="Latitude in decimal degrees")
    longitude: float = Field(description="Longitude in decimal degrees")


class WeatherResponse(Model):
    temperature_c: float = Field(description="Temperature in Celsius")


@weather_protocol.on_message(model=WeatherRequest, replies=WeatherResponse)
async def handle_weather(ctx: Context, sender: str, msg: WeatherRequest):
    temp = fetch_temperature(msg.latitude, msg.longitude)
    if temp is None:
        await ctx.send(sender, WeatherResponse(temperature_c=0.0))
        return
    await ctx.send(sender, WeatherResponse(temperature_c=temp))
```

```python
# agent.py
from uagents import Agent

from protocols import weather_protocol

agent = Agent()
agent.include(weather_protocol)

if __name__ == "__main__":
    agent.run()
```

## Pattern F: Calling ASI:One directly (OpenAI client)

Use when a plain `Agent()` needs a language model and
`ChatAgent` is not a fit. Agentverse injects `ASI1_API_KEY` and `ASI1_BASE_URL`, so read both from
`os.environ` and never ask the user for a key.

```python
# llm_client.py
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ASI1_API_KEY"],
    base_url=os.environ["ASI1_BASE_URL"],
)


def ask_asi1(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="asi1",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return completion.choices[0].message.content or ""
```

Rules:
- Models: `asi1` (default), `asi1-mini`, `asi1-ultra`
- Streaming is not supported — never pass `stream=True`.

## Anti-patterns (never generate for hosted agents)

- `Agent(seed=...)`, `Agent(mailbox=True)`, `Agent(port=...)`, `Agent(endpoint=...)`
- `Bureau()` or multi-agent local orchestration
- A file named `requests.py` — shadows the pip `requests` package; use `http_client.py` for HTTP helpers instead
- `import requests` or `requests.RequestException` in agent.py or protocols.py — import functions from `http_client` instead; only `http_client.py` may import the pip `requests` package
- `@agent.on_message(ChatMessage)` — register chat handlers on a `Protocol(spec=chat_protocol_spec)` instead
- `from uagents import ChatAgent` — use `from uagents.experimental.chat_agent import ChatAgent`
- `MetadataContent(type="metadata", data=...)` — TypeError; use `metadata=` for the `dict[str, str]` of card keys
- LangChain, CrewAI, Postgres, or other heavy third-party dependencies unless explicitly required
- Local-only patterns: mailbox setup, seed phrases, inspector, wallet funding
