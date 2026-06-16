import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from retrieval.retriever import get_retriever_fn
from retrieval.rat import rat_loop

router = APIRouter()

class AnalyzeRequest(BaseModel):
    session_id: str
    question: str = "what caused the incident?"

@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        retrieve_fn = get_retriever_fn(request.session_id)
        result = rat_loop(request.question, retrieve_fn)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))