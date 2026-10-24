# Crypto & Finance Agent (Agentverse Marketplace)

### 📌 Agentverse Marketplace Source
- **Agent Name**: Finance Q&A Agent
- **Domain**: `finance-qa.fetch.ai`
- **Agent Address**: [`agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl`](https://agentverse.ai/agents/details/agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl/profile)
- **Supported Protocols**: `Finance-QA` (v0.1.0), `AgentChatProtocol` (v0.3.0)

---

### 📂 Folder Structure
- `protocol.py`: Defines the typed message protocol (`FinanceQA`, `Response`) matching Agentverse specification.
- `finance_agent.py`: Autonomous Fetch.ai uAgent with CoinGecko live market pricing and Groq financial reasoning.
- `client.py`: The O.M.N.I.S bridge that allows `Main.py` or `Backend/` to query finance answers.
- `README.md`: Documentation and task specification.

---

### 🚀 Running the Agent Standalone
```bash
python Agents/FinanceAgent/finance_agent.py
```

---

### 🧪 Testing the Client
```bash
python Agents/FinanceAgent/client.py
```
*(Handles both conceptual economics questions like "What causes inflation?" and live crypto price tickers like "What is Bitcoin price?").*
