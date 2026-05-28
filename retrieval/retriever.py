import os
import sys
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document
from datetime import datetime


load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
from log_parser import parse_python_log, parse_nginx_log, parse_json_log

# --- Embedding model (loaded once, reused) ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# --- ChromaDB with persistent path ---
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_store")
vectorstore = Chroma(
    collection_name="logs",
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)

# --- LLM ---
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# --- Prompt ---
prompt = ChatPromptTemplate.from_template("""
You are a log analysis assistant. Use the following log entries to answer the question.
Always include the full timestamp and service name for each log entry you mention.
At the end, add a brief summary of what these errors indicate.

Logs:
{context}

Question: {question}
""")

# --- Chain ---
def get_chain(search_kwargs):
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    return (
        {"context": retriever | RunnableLambda(format_context), "question": RunnablePassthrough()}
        | prompt
        | llm
    )

# --- Ingest logs into vectorstore ---
def ingest_logs(log_entries: list[dict]):
    documents = []
    for log in log_entries:
        if "message" in log:
            content = log["message"]
        else:
            content = f"{log['method']} {log['path']} {log['status_code']}"

        documents.append(Document(
            page_content=content,
            metadata={
                "timestamp": parse_timestamp(log.get("timestamp", "")),
                "service_name": log.get("service_name", ""),
                "log_level": log.get("log_level", "")
            }
        ))
    vectorstore.add_documents(documents)

# --- Query ---
def query_logs(question: str, service_name: str = None, start_time: int = None, end_time: int = None) -> str:
    filters = []

    if service_name:
        filters.append({"service_name": service_name})
    if start_time:
        filters.append({"timestamp": {"$gte": start_time}})
    if end_time:
        filters.append({"timestamp": {"$lte": end_time}})

    search_kwargs = {"k": 5}
    if len(filters) == 1:
        search_kwargs["filter"] = filters[0]
    elif len(filters) > 1:
        search_kwargs["filter"] = {"$and": filters}

    chain = get_chain(search_kwargs)
    response = chain.invoke(question)
    return response.content

def parse_timestamp(timestamp: str) -> int:
    formats = [
        "%Y-%m-%dT%H:%M:%S",           # JSON: 2024-01-15T10:23:01
        "%Y-%m-%d %H:%M:%S,%f",         # Python: 2024-01-15 10:23:01,234
        "%d/%b/%Y:%H:%M:%S %z",         # Nginx: 15/Jan/2024:10:23:01 +0000
    ]
    for fmt in formats:
        try:
            return int(datetime.strptime(timestamp, fmt).timestamp())
        except ValueError:
            continue
    return 0 

def format_context(docs):
    formatted = []
    for doc in docs:
        ts = datetime.fromtimestamp(doc.metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S') if doc.metadata.get('timestamp') else ""
        formatted.append(
            f"[{ts}] [{doc.metadata.get('log_level', '')}] [{doc.metadata.get('service_name', '')}] {doc.page_content}"
        )
    return "\n".join(formatted)