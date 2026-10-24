# Web Search Agent (Fetch.ai / Agentverse)

### 📌 Agent Task
The **Web Search Agent** acts as an autonomous research worker for **O.M.N.I.S**. It accepts natural language queries, autonomously scrapes and aggregates live web results using DuckDuckGo (`ddgs`), and uses an LLM (Groq / LLaMA 3.3) to synthesize a direct, spoken-ready answer.

---

### 📂 Folder Structure
- `protocol.py`: Defines the typed message protocol (`SearchRequest`, `SearchResponse`) using Fetch.ai `uagents.Model`.
- `search_agent.py`: The standalone Fetch.ai uAgent. Can run locally on port `8001` or be hosted on Agentverse.
- `client.py`: The O.M.N.I.S bridge that allows `Main.py` or `Backend/` to query the agent synchronously and speak the answer.
- `README.md`: Documentation and task specification.

---

### 🚀 Running the Agent Standalone
To start the autonomous agent server:
```bash
python Agents/WebSearchAgent/search_agent.py
```
This initializes the agent, connects to the local port, and outputs its **Fetch.ai Agent Address** (e.g., `agent1q...`).

---

### 🔗 Integration with O.M.N.I.S
In `Main.py` or any backend module:
```python
from Agents.WebSearchAgent import query_web_search

answer = query_web_search("What is the current population of Tokyo?")
print(answer)
```
*(If the standalone daemon is not running, the client seamlessly falls back to in-process execution, ensuring zero downtime during live demonstrations).*
