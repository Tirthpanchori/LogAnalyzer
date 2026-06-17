# LogAnalyzer

**RAT-Powered Multi-Service Incident Reasoning Engine**

LogAnalyzer ingests log files from multiple microservices and uses a RAT (Retrieval-Augmented Thinking) reasoning loop to reconstruct what went wrong, identify the root cause, and suggest a fix — without manually correlating logs across services.

## What is RAT?

Unlike a basic RAG system that retrieves relevant chunks and answers in one shot, RAT iterates:

- **Pass 1** — Retrieves the most anomalous log chunks and forms an initial hypothesis
- **Pass 2** — Retrieves logs that temporally preceded the anomaly and refines the hypothesis
- **Pass 3** — Retrieves cross-service correlated logs and produces a final root cause analysis with confidence level and fix

## Features

- Parses three log formats — Python logging, Nginx access logs, JSON structured logs
- Per-session ChromaDB collections — multiple users don't mix logs
- Metadata-aware retrieval — filter by service name and time range
- 3-pass RAT reasoning loop with iterative hypothesis refinement
- Structured output — root cause, confidence level, actionable fix
- Follow-up question interface for deeper investigation

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq API + Llama 3.1 8B |
| Orchestration | LangChain (LCEL) |
| Embeddings | HF Inference API (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB (persistent) |
| Backend | FastAPI |
| Frontend | React + Vite |
| Deployment | Render |

## Project Structure
LogAnalyzer/

├── ingestion/

│   ├── log_parser.py       # Parses Python, Nginx, JSON log formats

│   └── embedder.py         # Ingestion pipeline

├── retrieval/

│   ├── retriever.py        # ChromaDB + LangChain retrieval layer

│   └── rat.py              # 3-pass RAT reasoning loop

├── api/

│   ├── main.py             # FastAPI app

│   └── routes/

│       ├── ingest.py       # POST /api/ingest

│       ├── analyze.py      # POST /api/analyze

│       └── query.py        # POST /api/query, DELETE /api/reset

├── frontend/               # React + Vite frontend

└── requirements.txt

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Groq API key (free at console.groq.com)

### Backend Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Add your GROQ_API_KEY to .env

uvicorn api.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ingest` | Upload log files, returns session_id |
| POST | `/api/analyze` | Run RAT loop, returns 3-pass analysis |
| POST | `/api/query` | Follow-up questions against ingested logs |
| DELETE | `/api/reset` | Clear session collection |

## Environment Variables
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
CHROMA_PATH=./chroma_store        # Local

CHROMA_PATH=/data/chroma_store  # Render deployment
## Demo Scenarios

Three pre-built incident scenarios for demos:

1. **DB connection pool exhaustion** — Auth service runs out of DB connections, cascading to API gateway timeouts and payment service 503s
2. **Memory leak** — Gradual OOM kills causing intermittent 502s upstream
3. **Bad deployment** — Misconfigured environment variable causing specific endpoint 500s

## Deployment

Deployed on Render with a persistent disk volume for ChromaDB. Set `CHROMA_PATH=/data/chroma_store` and `GROQ_API_KEY` in Render environment variables.