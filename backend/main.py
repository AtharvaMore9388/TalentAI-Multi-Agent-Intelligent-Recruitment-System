"""
TalentAI — FastAPI Backend
Provides REST endpoints and Server-Sent Events (SSE) for real-time
agent message streaming to the frontend.
"""
from __future__ import annotations
import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from lib.models import (
    RecruitmentRequest, RecruitmentState, AgentMessage, Candidate
)
from lib.chroma_store import get_store
import data_loader


# ─── App Lifecycle ───────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up the ChromaDB store on startup."""
    store = get_store()
    print(f"[TalentAI] ChromaDB ready. {store.count()} resumes indexed.")
    yield
    print("[TalentAI] Shutting down.")


app = FastAPI(
    title="TalentAI API",
    description="Multi-Agent Intelligent Recruitment and Talent Matching System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active pipeline results (keyed by session_id)
_active_results: dict[str, RecruitmentState] = {}


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    count = 0
    try:
        store = get_store()
        count = store.count()
    except Exception:
        count = 0
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "indexed_resumes": count,
        "version": "1.0.0",
    }


# ─── Sample Data ─────────────────────────────────────────────────────────────

@app.get("/api/samples", tags=["Data"])
async def get_sample_data():
    """Return sample JDs and resumes for demo use."""
    return data_loader.get_samples()


# ─── Recruitment Pipeline (SSE Streaming) ────────────────────────────────────

@app.post("/api/recruit/stream", tags=["Recruitment"])
async def recruit_stream(request: RecruitmentRequest):
    """
    Start the recruitment pipeline and stream agent messages via SSE.
    Each message is a JSON-encoded AgentMessage.
    If GROQ_API_KEY is not configured or in sandbox mode, streams the
    concrete worked example demonstrating all 6 agents with real-time delays.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        from agents.dynamic_pipeline import run_dynamic_recruitment_pipeline

        last_dossier = None
        try:
            async for msg, dossier in run_dynamic_recruitment_pipeline(
                job_description=request.job_description,
                resumes=request.resumes,
                top_n=request.top_n,
            ):
                if dossier is not None:
                    last_dossier = dossier
                yield f"data: {msg.model_dump_json()}\n\n"

            final_event = {
                "type": "complete",
                "status": "completed",
                "dossier": last_dossier,
            }
            yield f"data: {json.dumps(final_event)}\n\n"

        except Exception as exc:
            err_str = str(exc)
            error_msg = AgentMessage(
                agent="System",
                role="decision",
                content=f"❌ Pipeline error: {err_str}",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            yield f"data: {error_msg.model_dump_json()}\n\n"
            yield f"data: {json.dumps({'type': 'error', 'message': err_str})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ─── Recruitment Pipeline (Non-streaming) ────────────────────────────────────

@app.post("/api/recruit", tags=["Recruitment"])
async def recruit(request: RecruitmentRequest):
    """
    Start the recruitment pipeline (non-streaming version).
    Waits for full completion and returns results.
    """
    from agents.orchestrator import run_recruitment_pipeline

    state = RecruitmentState()
    messages: list[AgentMessage] = []

    try:
        async for msg in run_recruitment_pipeline(
            job_description=request.job_description,
            resumes=request.resumes,
            top_n=request.top_n,
        ):
            messages.append(msg)
            state.messages.append(msg)

        state.status = "completed"
        return {"state": state.model_dump(), "execution_trace": [m.model_dump() for m in messages]}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ─── Execution Trace ─────────────────────────────────────────────────────────

@app.get("/api/trace/demo", tags=["Demo"])
async def get_demo_trace():
    """Returns a pre-built execution trace for demo/documentation purposes."""
    return data_loader.get_demo_trace()


@app.get("/api/trace/worked-example", tags=["Demo"])
async def get_worked_example():
    """Returns the structured concrete worked example dossier addressing reviewer feedback."""
    return data_loader.get_worked_example_dossier()


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
