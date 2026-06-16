import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from retrieval.retriever import query_logs, delete_session

router = APIRouter()

class QueryRequest(BaseModel):
    session_id: str
    question: str
    service_name: str = None
    start_time: int = None
    end_time: int = None

class ResetRequest(BaseModel):
    session_id: str

@router.post("/query")
async def query(request: QueryRequest):
    try:
        response = query_logs(
            question=request.question,
            session_id=request.session_id,
            service_name=request.service_name,
            start_time=request.start_time,
            end_time=request.end_time
        )
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reset")
async def reset(request: ResetRequest):
    try:
        delete_session(request.session_id)
        return {"message": f"Session {request.session_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   