import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), 'ingestion'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'retrieval'))

from log_parser import parse_python_log, parse_nginx_log, parse_json_log
from retriever import ingest_logs, vectorstore, format_context
from rat import rat_loop

# --- Load and ingest sample logs ---
def load_logs(filepath, parser):
    with open(filepath) as f:
        lines = f.readlines()
    parsed = [parser(line.strip()) for line in lines]
    return [p for p in parsed if p is not None]

python_logs = load_logs("ingestion/sample_logs/python_app.log", parse_python_log)
nginx_logs = load_logs("ingestion/sample_logs/nginx_access.log", parse_nginx_log)
json_logs = load_logs("ingestion/sample_logs/json_app.log", parse_json_log)

all_logs = python_logs + nginx_logs + json_logs
ingest_logs(all_logs)
print(f"Ingested {len(all_logs)} sample logs")

# --- Ingest synthetic incident logs ---
base_time = datetime(2024, 1, 15, 10, 0, 0)
synthetic_logs = [
    {"timestamp": (base_time + timedelta(minutes=2)).isoformat(), "service_name": "service-a", "log_level": "WARNING", "message": "DB connection pool reaching capacity 18/20"},
    {"timestamp": (base_time + timedelta(minutes=3)).isoformat(), "service_name": "service-a", "log_level": "ERROR", "message": "DB connection pool exhausted max=20"},
    {"timestamp": (base_time + timedelta(minutes=4)).isoformat(), "service_name": "service-a", "log_level": "ERROR", "message": "Cannot acquire DB connection all slots taken"},
    {"timestamp": (base_time + timedelta(minutes=3)).isoformat(), "service_name": "service-b", "log_level": "WARNING", "message": "Upstream service-a response slow 2000ms"},
    {"timestamp": (base_time + timedelta(minutes=4)).isoformat(), "service_name": "service-b", "log_level": "ERROR", "message": "Timeout waiting for service-a response after 30s"},
    {"timestamp": (base_time + timedelta(minutes=5)).isoformat(), "service_name": "service-b", "log_level": "ERROR", "message": "Returning 503 to downstream clients"},
    {"timestamp": (base_time + timedelta(minutes=5)).isoformat(), "service_name": "service-c", "log_level": "WARNING", "message": "service-b returning errors intermittently"},
    {"timestamp": (base_time + timedelta(minutes=6)).isoformat(), "service_name": "service-c", "log_level": "ERROR", "message": "500 error received from service-b"},
    {"timestamp": (base_time + timedelta(minutes=7)).isoformat(), "service_name": "service-c", "log_level": "ERROR", "message": "Cascading failure detected alerting on-call"},
]
ingest_logs(synthetic_logs)
print(f"Ingested {len(synthetic_logs)} synthetic logs")

# --- Retrieve function for RAT ---
def retrieve_fn(query: str) -> str:
    docs = vectorstore.as_retriever(search_kwargs={"k": 5}).invoke(query)
    return format_context(docs)

# --- Run RAT loop ---
result = rat_loop("what caused the cascading failure across services?", retrieve_fn)