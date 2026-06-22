"""
Phase 7: FastAPI backend and static frontend for the regulatory RAG system.

Run:
    uvicorn app:app --reload --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from phase5_6_rag import (
    DEFAULT_LLM_MODEL,
    DEFAULT_OLLAMA_MODEL,
    RetrievedChunk,
    detect_question_language,
    generate_answer,
    generate_ollama_answer,
    load_chunks,
    normalize_language,
    normalize_domain,
    retrieve,
    translate_question_ollama,
    translate_question_openai,
)

LanguageCode = Literal[
    "auto",
    "english",
    "hindi",
    "bengali",
    "gujarati",
    "kannada",
    "malayalam",
    "marathi",
    "odia",
    "punjabi",
    "tamil",
    "telugu",
]

PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PROJECT_ROOT / "static"

app = FastAPI(
    title="Regulatory Intelligence RAG",
    version="1.0.0",
    description="Phase 7 API for SEBI/RBI/Income Tax regulatory Q&A with citations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_cache(request, call_next) -> Response:
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    domain_filter: Literal["all", "SEBI", "RBI", "IncomeTax"] = "all"
    provider: Literal["ollama", "openai", "retrieval_only"] = "ollama"
    answer_language: LanguageCode = "auto"
    top_k: int = Field(3, ge=1, le=8)
    include_hf_experimental: bool = False
    openai_model: str = DEFAULT_LLM_MODEL
    ollama_model: str = DEFAULT_OLLAMA_MODEL
    ollama_timeout: int = Field(600, ge=30, le=1800)


class Source(BaseModel):
    label: str
    domain: str
    circular_number: str
    date: str
    source_url: str
    source_type: str
    trusted_official_source: bool
    score: float
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    provider: str
    domain_filter: str
    answer_language: str
    retrieval_question: str
    sources: list[Source]


def chunk_to_source(chunk: RetrievedChunk, index: int) -> Source:
    metadata = chunk.metadata
    snippet = " ".join(chunk.text.split())[:420]
    return Source(
        label=f"S{index}",
        domain=str(metadata.get("domain") or "Unknown"),
        circular_number=str(metadata.get("circular_number") or metadata.get("title") or chunk.chunk_id),
        date=str(metadata.get("date") or "date not available"),
        source_url=str(metadata.get("source_url") or metadata.get("url") or ""),
        source_type=str(metadata.get("source_type") or "project_corpus"),
        trusted_official_source=bool(metadata.get("trusted_official_source", True)),
        score=round(chunk.final_score, 4),
        snippet=snippet,
    )


def domain_status() -> list[dict]:
    statuses = []
    for key, label in [
        ("all", "All"),
        ("SEBI", "SEBI"),
        ("RBI", "RBI"),
        ("IncomeTax", "Income Tax"),
    ]:
        if key == "all":
            count = len(load_chunks(None))
        else:
            count = len(load_chunks(normalize_domain(key)))
        statuses.append(
            {
                "value": key,
                "label": label,
                "chunk_count": count,
                "available": count > 0,
            }
        )
    return statuses


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "domains": domain_status()}


@app.get("/domains")
def domains() -> list[dict]:
    return domain_status()


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    domain = normalize_domain(request.domain_filter)
    requested_language = normalize_language(request.answer_language)
    answer_language = (
        detect_question_language(request.question)
        if requested_language == "auto"
        else requested_language
    )
    if request.domain_filter == "IncomeTax" and not load_chunks(domain):
        raise HTTPException(
            status_code=422,
            detail="Income Tax is part of the target architecture, but no Income Tax chunks are present in this merged corpus yet.",
        )

    retrieval_question = request.question
    if answer_language != "english":
        try:
            if request.provider == "openai" and os.getenv("OPENAI_API_KEY"):
                retrieval_question = translate_question_openai(
                    request.question,
                    "english",
                    model=request.openai_model,
                )
            else:
                retrieval_question = translate_question_ollama(
                    request.question,
                    "english",
                    model=request.ollama_model,
                    timeout=min(request.ollama_timeout, 180),
                )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Question translation failed: {exc}") from exc

    try:
        chunks = retrieve(
            retrieval_question,
            request.domain_filter,
            request.top_k,
            include_hf_experimental=request.include_hf_experimental,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}") from exc

    if not chunks:
        return QueryResponse(
            answer="No matching regulatory context was found in the indexed database.",
            provider=request.provider,
            domain_filter=request.domain_filter,
            answer_language=answer_language,
            retrieval_question=retrieval_question,
            sources=[],
        )

    try:
        if request.provider == "retrieval_only":
            answer = "Retrieval-only mode: review the source cards below for the matched context."
        elif request.provider == "ollama":
            answer = generate_ollama_answer(
                request.question,
                chunks,
                model=request.ollama_model,
                timeout=request.ollama_timeout,
                answer_language=answer_language,
            )
        else:
            if not os.getenv("OPENAI_API_KEY"):
                raise HTTPException(
                    status_code=400,
                    detail="OPENAI_API_KEY is not set. Choose Ollama for local testing or set an OpenAI API key.",
                )
            answer = generate_answer(
                request.question,
                chunks,
                model=request.openai_model,
                answer_language=answer_language,
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {exc}") from exc

    return QueryResponse(
        answer=answer,
        provider=request.provider,
        domain_filter=request.domain_filter,
        answer_language=answer_language,
        retrieval_question=retrieval_question,
        sources=[chunk_to_source(chunk, index) for index, chunk in enumerate(chunks, 1)],
    )
