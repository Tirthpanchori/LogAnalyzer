import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ingestion'))
from log_parser import parse_python_log, parse_nginx_log, parse_json_log

# --- Embedding model (loaded once, reused across all sessions) ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# --- ChromaDB persistent path ---
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_store")

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

# --- Per-session vectorstore ---
def get_vectorstore(session_id: str) -> Chroma:
    return Chroma(
        collection_name=f"logs_{session_id}",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

# --- Timestamp parser ---
def parse_timestamp(timestamp: str) -> int:
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S,%f",
        "%d/%b/%Y:%H:%M:%S %z",
    ]
    for fmt in formats:
        try:
            return int(datetime.strptime(timestamp, fmt).timestamp())
        except ValueError:
            continue
    return 0

# --- Format context for LLM ---
def format_context(docs):
    formatted = []
    for doc in docs:
        ts = datetime.fromtimestamp(doc.metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S') if doc.metadata.get('timestamp') else ""
        formatted.append(
            f"[{ts}] [{doc.metadata.get('log_level', '')}] [{doc.metadata.get('service_name', '')}] {doc.page_content}"
        )
    return "\n".join(formatted)

# --- Ingest logs into a session collection ---
def ingest_logs(log_entries: list[dict], session_id: str):
    vectorstore = get_vectorstore(session_id)
    documents = []
    for log in log_entries:
        if "message" in log:
            content = log["message"]
        else:
            content = f"{log['method']} {log['path']} {log['status_code']}"

        ts = parse_timestamp(log.get("timestamp", ""))
        documents.append(Document(
            page_content=content,
            metadata={
                "timestamp": ts,
                "service_name": log.get("service_name", ""),
                "log_level": log.get("log_level", "")
            }
        ))
    vectorstore.add_documents(documents)

# --- Query logs in a session collection ---
def query_logs(question: str, session_id: str, service_name: str = None, start_time: int = None, end_time: int = None) -> str:
    vectorstore = get_vectorstore(session_id)
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

    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    chain = (
        {"context": retriever | RunnableLambda(format_context), "question": RunnablePassthrough()}
        | prompt
        | llm
    )
    response = chain.invoke(question)
    return response.content

# --- Get retriever function for RAT loop ---
def get_retriever_fn(session_id: str):
    vectorstore = get_vectorstore(session_id)
    def retrieve_fn(query: str) -> str:
        docs = vectorstore.as_retriever(search_kwargs={"k": 5}).invoke(query)
        return format_context(docs)
    return retrieve_fn

# --- Delete a session collection ---
def delete_session(session_id: str):
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    client.delete_collection(f"logs_{session_id}")