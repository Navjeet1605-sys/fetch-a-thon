# 🌌 O.M.N.I.S: Autonomous Multi-Agent Personal AI

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
[![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents-blue)](https://fetch.ai/)
[![Agentverse](https://img.shields.io/badge/Agentverse-Marketplace-purple)](https://agentverse.ai/)
[![ASI:One](https://img.shields.io/badge/ASI%3AOne-Ready-orange)](https://asi1.ai/)

> **Fetch-A-Thon 3.0 Submission:** *ASI:One Agent Challenge – From Intent to Action*  
> **Target Tracks:** *Best Multi-Agent Workflow* | *Best Personal AI* | *Best Agentverse Deployment*

---

## 📌 Executive Summary

**O.M.N.I.S (Omni-Modal Networked Intelligence System)** transforms a traditional voice/desktop assistant into an **autonomous multi-agent command center** powered by the **Fetch.ai Ecosystem**.

Rather than acting as a simple conversational chatbot, O.M.N.I.S turns human intent into real-world autonomous action. When a user asks any question or delegates a complex task (via voice locally or through **ASI:One** over the decentralized network), O.M.N.I.S analyzes the intent and orchestrates specialized Fetch.ai agents to plan, query live market APIs, scrape real-time web sources, and execute actions.

---

## 🏗️ System Architecture

```
                 [ User Voice / Terminal ]       [ ASI:One Cloud User ]
                            │                              │
                            │                      (Agent Chat Protocol - ACP)
                            │                              │
                            ▼                              ▼
                 ┌────────────────────────────────────────────────────────┐
                 │       O.M.N.I.S Supervisor & Intent Router             │
                 │          (Cohere Decision-Making Model)                │
                 └──────────────────────────┬─────────────────────────────┘
                                            │
        ┌───────────────────────────────────┼──────────────────────────────────┐
        ▼                                   ▼                                  ▼
┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐
│ Crypto & Finance Agent│       │   Web Search Agent    │       │ Conversational Agent  │
│  (Agentverse Address  │       │  (DuckDuckGo + Groq   │       │   (Groq LLaMA Engine  │
│      + CoinGecko)     │       │     Synthesizer)      │       │     + Knowledge)      │
└───────────────────────┘       └───────────────────────┘       └───────────────────────┘
        │                                   │                                  │
        └───────────────────────────────────┼──────────────────────────────────┘
                                            │
                                            ▼
                           [ Synthesis & Spoken Output ]
                             (Text-to-Speech Engine)
```

---

## ⚡ The Three Pillars of Fetch.ai in O.M.N.I.S

### 1. 🤖 `uAgents` Framework (Multi-Agent Swarm)
- Each agent runs with its own identity, protocol, and message models.
- **Crypto & Finance Agent** ([`Agents/FinanceAgent`](file:///c:/Users/navje/Downloads/O.M.N.I.S-main/O.M.N.I.S-main/Agents/FinanceAgent/)): Tracks real-time token metrics (BTC, ETH, FET/ASI) and answers macroeconomic questions.
- **Web Search Agent** ([`Agents/WebSearchAgent`](file:///c:/Users/navje/Downloads/O.M.N.I.S-main/O.M.N.I.S-main/Agents/WebSearchAgent/)): Performs live scraping and voice-friendly fact extraction.

### 2. 🌐 `Agentverse` Integration
- Integrates directly with existing Agentverse marketplace agents, including the official **Finance Q&A Agent** (`agent1qdv2qgxucvqatam6nv28qp202f3pw8xqpfm8man6zyegztuzd2t6yem9evl`).
- Dedicated drop-in script for [Agentverse Launchpad](https://agentverse.ai/agents/launch): [`FetchAI_Ecosystem/agentverse_omnis_cloud.py`](file:///c:/Users/navje/Downloads/O.M.N.I.S-main/O.M.N.I.S-main/FetchAI_Ecosystem/agentverse_omnis_cloud.py).
- Supports both **Cloud Hosting** (runs 24/7 on Agentverse) and **Mailbox Connection** (connects local agent to Agentverse).

### 3. 💬 `ASI:One` & Agent Chat Protocol (ACP)
- Implements the official **Agent Chat Protocol (ACP)** with `chat_protocol_spec`, `ChatMessage`, `ChatAcknowledgement`, and `TextContent`.
- Users on **[ASI:One](https://asi1.ai/)** can interact directly with O.M.N.I.S inside the chat interface without needing any custom front-end.

---

## 🌐 How to Launch on Agentverse (ASI:One)

To deploy O.M.N.I.S to **[Agentverse Launchpad](https://agentverse.ai/agents/launch)**:
1. Log in to [https://agentverse.ai/agents/launch](https://agentverse.ai/agents/launch)
2. Click **+ New Agent** ➔ Select **Blank Agent**
3. In the code editor (`agent.py`), copy and paste the entire code from:
   [`FetchAI_Ecosystem/agentverse_omnis_cloud.py`](file:///c:/Users/navje/Downloads/O.M.N.I.S-main/O.M.N.I.S-main/FetchAI_Ecosystem/agentverse_omnis_cloud.py)
4. In the left navigation, click **Secrets**:
   - Add Secret Name: `GROQ_API_KEY`
   - Value: `your_groq_api_key_here` (from https://console.groq.com)
5. Click **Start** (top right).
6. Your agent address (`agent1q...`) will appear in the console logs and register with the Almanac contract and **ASI:One** via ACP!

---

## 🚀 Quickstart & Demo Guide

### 1. Interactive Command Center (Ask Anything)
Launch the unified multi-agent dispatcher:
```bash
python omnis_agent.py
```
*Try asking:*
- `"What is the live price of Bitcoin and Fetch.ai today?"` ➔ Handled by **Crypto & Finance Agent**
- `"Who won the latest Nobel Prize in Physics?"` ➔ Handled by **Web Search Agent**
- `"What is the difference between stocks and bonds?"` ➔ Handled by **Economics Reasoning Agent**

### 2. Voice-Activated Desktop Assistant
Run the full voice pipeline (listening ➔ routing ➔ execution ➔ text-to-speech):
```bash
python Main.py
```

### 3. Standalone Agent Tests
- **Web Search Agent**:
  ```bash
  python Agents/WebSearchAgent/client.py
  ```
- **Finance & Crypto Agent**:
  ```bash
  python Agents/FinanceAgent/client.py
  ```
- **ASI:One ACP Handshake Simulation**:
  ```bash
  python FetchAI_Ecosystem/test_asione_interaction.py
  ```

---

## 📁 Repository Structure

```
O.M.N.I.S-main/
├── README.md                      # Hackathon Documentation & Badges
├── omnis_agent.py                 # Universal Interactive Multi-Agent Runner
├── Main.py                        # Voice & Desktop Assistant Loop
├── .env                           # API Keys (Groq, Cohere)
├── Agents/
│   ├── agent_hub.py               # Dynamic Intent Router & Orchestrator
│   ├── FinanceAgent/              # Crypto & Finance Agent (Agentverse Protocol)
│   │   ├── protocol.py            # Typed FinanceQA & Response models
│   │   ├── finance_agent.py       # Standalone uAgent & CoinGecko engine
│   │   └── client.py              # Synchronous OMNIS bridge
│   └── WebSearchAgent/            # Realtime Web Search & Scraping Agent
│       ├── protocol.py            # Typed SearchRequest & SearchResponse
│       ├── search_agent.py        # Standalone DuckDuckGo + Groq uAgent
│       └── client.py              # Fail-safe search connector
├── FetchAI_Ecosystem/
│   ├── omnis_acp_agent.py         # Official Agent Chat Protocol (ACP) Agent for ASI:One
│   └── test_asione_interaction.py # Simulated ASI:One ACP interaction test
└── Backend/                       # Voice STT, TTS, Chatbot, and Automation
```

---

## 🏆 Fetch-A-Thon 3.0 Deliverables
- **GitHub Repository:** Public repo with all agents, protocols, and instructions.
- **ASI:One Compatibility:** Implements `uagents_core.contrib.protocols.chat` (ACP).
- **Target Category:** *Best Multi-Agent Workflow* & *Best Personal AI*.
