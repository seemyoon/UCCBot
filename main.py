import uuid

from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from rag.rag_pipeline import RAGPipline
from schemas import QueryResponse, QueryRequest, SessionResponse

import uvicorn

app = FastAPI(
    title="UCC API",
    description="Legal assistant for Ukrainian Criminal Code",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_sessions = {}


@app.get("/")
async def root():
    return {
        "message": "UCC API",
        "status": "running",
        "docs": "/docs"
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())

        if session_id not in rag_sessions:
            rag_sessions[session_id] = RAGPipline()

        rag = rag_sessions[session_id]

        answer = rag.run_rag_pipline(request.query)

        return QueryResponse(
            answer=answer,
            session_id=session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session/new", response_model=SessionResponse)
async def create_session():
    session_id = str(uuid.uuid4())

    rag_sessions[session_id] = RAGPipline()

    return SessionResponse(
        session_id=session_id,
        message="New session created",
    )


@app.post("/session/{session_id}", response_model=SessionResponse)
async def delete_session(session_id: str):
    if session_id in rag_sessions:
        del rag_sessions[session_id]

        return SessionResponse(
            session_id=session_id,
            message="Session deleted",
        )
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.post("/session/{session_id}/clear}", response_model=SessionResponse)
async def clear_session(session_id: str):
    if session_id in rag_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    rag_sessions[session_id].clear_history()

    return SessionResponse(
        session_id=session_id,
        message="Session cleared",
    )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_sessions": len(rag_sessions)
    }


if __name__ == "__main__":
    # uvicorn main:app --reload --host 0.0.0.0 --port 8000

    uvicorn.run(app, host="0.0.0.0", port=8000)
