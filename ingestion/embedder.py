import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'retrieval'))
from retriever import ingest_logs

from log_parser import parse_python_log, parse_nginx_log, parse_json_log

def load_logs(filepath, parser):
    with open(filepath) as f:
        lines = f.readlines()
    parsed = [parser(line.strip()) for line in lines]
    return [p for p in parsed if p is not None]

if __name__ == "__main__":
    python_logs = load_logs("sample_logs/python_app.log", parse_python_log)
    nginx_logs = load_logs("sample_logs/nginx_access.log", parse_nginx_log)
    json_logs = load_logs("sample_logs/json_app.log", parse_json_log)

    all_logs = python_logs + nginx_logs + json_logs
    ingest_logs(all_logs)
    print(f"Ingested {len(all_logs)} logs into ChromaDB")