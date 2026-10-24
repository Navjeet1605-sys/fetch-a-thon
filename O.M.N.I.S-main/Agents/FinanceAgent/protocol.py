from pydantic import BaseModel, Field

try:
    from uagents import Model  # type: ignore
except Exception:
    # Fetch.ai Model inherits directly from Pydantic BaseModel
    Model = BaseModel

class FinanceQA(Model):
    """Protocol input model for Agentverse Finance Q&A Agent"""
    question: str = Field(description="The finance, economic, or crypto question.")

class Response(Model):
    """Protocol response model returned by Agentverse Finance Q&A Agent"""
    text: str = Field(description="Detailed answer from the agent.")
