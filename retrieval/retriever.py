import os
import sys
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

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

Logs:
{context}

Question: {question}
""")

# --- Chain ---
def get_chain():
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    return (
        {"context": retriever, "question": RunnablePassthrough()}
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
                "timestamp": log.get("timestamp", ""),
                "service_name": log.get("service_name", ""),
                "log_level": log.get("log_level", "")
            }
        ))
    vectorstore.add_documents(documents)

# --- Query ---
def query_logs(question: str) -> str:
    chain = get_chain()
    response = chain.invoke(question)
    return response.content