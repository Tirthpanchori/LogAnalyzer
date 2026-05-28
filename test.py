from ingestion.embedder import load_logs
from ingestion.log_parser import parse_python_log, parse_nginx_log, parse_json_log
from retrieval.retriever import ingest_logs, query_logs

# Ingest
python_logs = load_logs("ingestion/sample_logs/python_app.log", parse_python_log)
nginx_logs = load_logs("ingestion/sample_logs/nginx_access.log", parse_nginx_log)
json_logs = load_logs("ingestion/sample_logs/json_app.log", parse_json_log)

all_logs = python_logs + nginx_logs + json_logs
ingest_logs(all_logs)
print(f"Ingested {len(all_logs)} logs")

# Query
# Filtered query
response = query_logs(
    "what errors occurred?",
    service_name="auth-service"
)
print("\nFiltered answer:", response)