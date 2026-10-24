import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

# Ensure project root is accessible
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Agents.agent_hub import process_query

# Import official Fetch.ai ACP (Agent Chat Protocol) components
try:
    from uagents import Agent, Context, Protocol
    from uagents_core.contrib.protocols.chat import (
        ChatAcknowledgement,
        ChatMessage,
        EndSessionContent,
        MetadataContent,
        StartSessionContent,
        TextContent,
        chat_protocol_spec,
    )
    HAS_UAGENTS = True
except Exception as e:
    HAS_UAGENTS = False


if HAS_UAGENTS:
    AGENT_PORT = 8000
    AGENT_SEED = "omnis_asione_agent_seed_fetchathon_2026"
    MAILBOX_KEY = os.getenv("AGENTVERSE_MAILBOX_KEY", "").strip()

    # Initialize the primary O.M.N.I.S Agent (Mailbox or Local HTTP Server)
    if MAILBOX_KEY:
        agent = Agent(
            name="omnis_personal_ai",
            seed=AGENT_SEED,
            mailbox=f"{MAILBOX_KEY}@https://agentverse.ai",
        )
    else:
        agent = Agent(
            name="omnis_personal_ai",
            port=AGENT_PORT,
            seed=AGENT_SEED,
            endpoint=[f"http://127.0.0.1:{AGENT_PORT}/submit"],
        )

    # Initialize the chat protocol with the standard ACP spec for ASI:One
    chat_proto = Protocol(spec=chat_protocol_spec)

    def create_text_chat(text: str, metadata: dict = None, end_session: bool = False) -> ChatMessage:
        """Utility function to wrap plain text and optional rich metadata into an official ACP ChatMessage."""
        content = [TextContent(type="text", text=text)]
        if metadata:
            content.append(MetadataContent(type="metadata", metadata={str(k): str(v) for k, v in metadata.items()}))
        if end_session:
            content.append(EndSessionContent(type="end-session"))
        return ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=content,
        )

    @agent.on_event("startup")
    async def handle_startup(ctx: Context):
        ctx.logger.info("=" * 60)
        ctx.logger.info("🚀 O.M.N.I.S Agent Chat Protocol (ACP) Server is LIVE!")
        ctx.logger.info(f"Agent Address: {agent.address}")
        ctx.logger.info(f"Listening on port: {AGENT_PORT}")
        ctx.logger.info("Discoverable via Agentverse & ASI:One")
        ctx.logger.info("=" * 60)

    @chat_proto.on_message(ChatMessage)
    async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
        """
        Receives messages from ASI:One or other Fetch.ai network agents,
        acknowledges receipt, routes the request to O.M.N.I.S multi-agent swarm,
        and replies with structured result.
        """
        ctx.logger.info(f"Received ACP message from: {sender} (Message ID: {msg.msg_id})")

        # 1. Mandatory ACP step: Acknowledge message receipt immediately
        await ctx.send(
            sender,
            ChatAcknowledgement(
                timestamp=datetime.now(timezone.utc),
                acknowledged_msg_id=msg.msg_id
            )
        )

        # 2. Process content items
        for item in msg.content:
            if isinstance(item, StartSessionContent):
                ctx.logger.info(f"Session initiated with: {sender}")
                welcome = create_text_chat(
                    "Hello! I am O.M.N.I.S, your autonomous personal AI assistant on the Fetch.ai network. How may I assist you today?",
                    metadata={"Status": "Active", "Swarm": "OMNIS Multi-Agent Hub"}
                )
                await ctx.send(sender, welcome)

            elif isinstance(item, TextContent):
                user_text = item.text.strip()
                ctx.logger.info(f"Processing query from {sender}: '{user_text}'")

                # Dispatch through O.M.N.I.S multi-agent router
                result = process_query(user_text, speak=False)
                assigned_agent = result.get("agent", "OMNIS Hub")
                response_text = f"[{assigned_agent}]\n{result.get('response', '')}"
                meta = {"Agent": assigned_agent, "Status": "Success"}

                # Send back the reply message via ACP
                response_msg = create_text_chat(response_text, metadata=meta)
                await ctx.send(sender, response_msg)
                ctx.logger.info(f"Sent reply back to {sender}")

            elif isinstance(item, EndSessionContent):
                ctx.logger.info(f"Session closed by: {sender}")

    @chat_proto.on_message(ChatAcknowledgement)
    async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
        """Handle acknowledgements cleanly to avoid unhandled message warnings."""
        ctx.logger.debug(f"Received ACK from {sender} for {msg.acknowledged_msg_id}")

    # Include the ACP protocol into the agent
    agent.include(chat_proto, publish_manifest=True)

else:
    agent = None


def run_acp_agent():
    if agent:
        print("Starting O.M.N.I.S ACP Agent for Agentverse / ASI:One...")
        agent.run()
    else:
        print("uagents / ACP protocol is not initialized in this environment.")
        test_q = "What is Bitcoin price?"
        res = process_query(test_q)
        print(f"Fallback Execution:\n[{res['agent']}]\n{res['response']}")


if __name__ == "__main__":
    run_acp_agent()
