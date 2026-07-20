# 🤖 NeuralSQL - Agentic Text-to-SQL Engine

An enterprise-grade Natural Language to SQL generation platform powered by Agentic AI (Llama 3 via Groq), FastAPI, and Docker.

**Author:** Yash
**Live App:** https://neuralsql-agent.streamlit.app/
---

## ✨ Key Features

- 💬 **Natural Language Querying:** Translates complex human questions into optimized SQL queries.
- 🤖 **Agentic AI Architecture:**
  - **Generator Agent:** Converts plain text into draft SQL syntax.
  - **Critic Agent:** Audits SQL queries against schema limits, syntax, and logic.
  - **Autonomous Self-Correction:** Automatic retry loop with error feedback back to Generator if syntax fails.
- 🐳 **Dockerized Setup:** Fully containerized backend and frontend for seamless single-command deployment.
- ⚡ **Asynchronous REST API:** High-throughput FastAPI infrastructure.
- 📊 **Real-Time Telemetry:** Monitors query execution counts, success rates, and live system metrics.

---

## 🔁 Agentic Architecture Workflow

```
[ User Question ]
       │
       ▼
[ Ambiguity Evaluator ] ──(Ambiguous?)──► [ Request User Clarification ]
       │ (Clear)
       ▼
┌─────────────────────────────────────────────────────────┐
│                 AGENTIC SELF-HEALING LOOP                │
│                                                            │
│    [ Generator Agent ] ──────► Drafts SQL                 │
│           ▲                        │                       │
│           │ (Feedback)             ▼                       │
│    [ Critic Agent ] ◄────── Checks Syntax/Schema           │
└─────────────────────────────────────────────────────────┘
       │ (Passed)
       ▼
[ SQLite Database ] ────────► Executes & Returns DataFrame
       │
       ▼
[ Streamlit UI & Telemetry ]
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Agentic AI Framework** | Groq API (Llama-3) |
| **Backend Infrastructure** | FastAPI, Uvicorn, Pydantic |
| **Frontend & Visualization** | Streamlit, Pandas |
| **Database Engine** | SQLite3 |
| **Containerization** | Docker, Docker Compose |

---

## 📂 Repository Structure

```
neuralsql-agent/
│
├── backend/
│   ├── api.py               # FastAPI REST API endpoints
│   ├── sql_agent.py         # LLM Multi-Agent pipeline (Generator + Critic)
│   ├── db_setup.py          # SQLite database initialization
│   ├── analytics.py         # Telemetry & query performance metrics
│   ├── Dockerfile           # Backend container configuration
│   └── requirements.txt     # Backend dependencies
│
├── frontend/
│   ├── app.py                # Streamlit dashboard interface
│   ├── Dockerfile            # Frontend container configuration
│   └── requirements.txt      # Frontend dependencies
│
├── docker-compose.yml         # Multi-container orchestration
├── .gitignore                 # Git exclusion rules
└── README.md                  # Project documentation
```

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/check-ambiguity` | Evaluates if input query needs user clarification |
| `POST` | `/ask` | Executes Multi-Agent pipeline to generate & run SQL |
| `GET` | `/analytics` | Fetches query metrics, total count, and success rate |

---

## 🚀 Quick Start Guide

### Option A: Using Docker (Recommended)

```bash
# 1. Clone repo
git clone https://github.com/your-username/neuralsql-agent.git
cd neuralsql-agent

# 2. Set environment variable (PowerShell)
$env:GROQ_API_KEY="your_groq_api_key_here"

# 3. Spin up Docker Containers
docker-compose up --build
```

**Frontend UI:** http://localhost:8501 | **FastAPI Docs:** http://localhost:8000/docs

### Option B: Local Terminal Setup

**1. Backend Server:**

```bash
cd backend
pip install -r requirements.txt
$env:GROQ_API_KEY="your_groq_api_key_here"
python -m uvicorn api:app --reload --port 8000
```

**2. Frontend UI:**

```bash
cd frontend
pip install -r requirements.txt
python -m streamlit run app.py
```

---

## 🗄️ Database Schema Reference

- **customers**: `cust_id` (PK), `name`, `city`
- **products**: `product_id` (PK), `item_name`, `category`, `price`
- **orders**: `order_id` (PK), `cust_id` (FK), `product_id` (FK), `amount`
