import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from ingestion.log_parser import parse_python_log, parse_nginx_log, parse_json_log
from retrieval.retriever import ingest_logs

router = APIRouter()

def detect_and_parse(content: str) -> list[dict]:
    lines = content.strip().split('\n')
    parsed = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Try JSON first
        result = parse_json_log(line)
        if result:
            parsed.append(result)
            continue
        # Try Python logging
        result = parse_python_log(line)
        if result:
            parsed.append(result)
            continue
        # Try Nginx
        result = parse_nginx_log(line)
        if result:
            parsed.append(result)
            continue
    return parsed

@router.post("/ingest")
async def ingest_files(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    total_logs = []

    for file in files:
        try:
            content = await file.read()
            text = content.decode("utf-8")
            parsed = detect_and_parse(text)
            total_logs.extend(parsed)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing {file.filename}: {str(e)}")

    if not total_logs:
        raise HTTPException(status_code=400, detail="No valid log lines found in uploaded files")

    ingest_logs(total_logs, session_id)

    return {
        "session_id": session_id,
        "total_logs_ingested": len(total_logs)
    }