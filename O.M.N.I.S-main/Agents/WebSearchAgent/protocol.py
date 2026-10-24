from pydantic import BaseModel, Field
from typing import List, Optional

try:
    from uagents import Model
except ImportError:
    # Fallback to BaseModel if uagents is still finishing installation
    Model = BaseModel

class SearchRequest(Model):
    query: str = Field(description="The web search query to look up on the internet.")
    max_results: int = Field(default=5, description="Maximum number of search results to retrieve.")

class SearchResponse(Model):
    query: str = Field(description="Original search query.")
    summary: str = Field(description="Concise, synthesized answer suitable for speech.")
    sources: List[str] = Field(default_factory=list, description="Titles or URLs of sources found.")
