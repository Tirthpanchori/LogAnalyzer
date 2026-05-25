from sentence_transformers import SentenceTransformer
import chromadb
from log_parser import parse_python_log, parse_nginx_log, parse_json_log

# Setup
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.create_collection("logs")

# Parse logs
def load_logs(filepath, parser):
    with open(filepath) as f:
        lines = f.readlines()
    parsed = [parser(line.strip()) for line in lines]
    return [p for p in parsed if p is not None]  # filter failed parses

python_logs = load_logs("sample_logs/python_app.log", parse_python_log)
nginx_logs = load_logs("sample_logs/nginx_access.log", parse_nginx_log)
json_logs = load_logs("sample_logs/json_app.log", parse_json_log)

all_logs = python_logs + nginx_logs + json_logs

# Embed and store
documents = [log["message"] if "message" in log else f"{log['method']} {log['path']} {log['status_code']}" for log in all_logs]
embeddings = model.encode(documents).tolist()
ids = [f"log_{i}" for i in range(len(documents))]

collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=ids
)

# Query
query = "database connection refused"
query_embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=3
)

print("\nTop 3 results for:", query)
for doc in results["documents"][0]:
    print(" -", doc)