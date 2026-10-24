"""FastAPI entry point for Clyro's two-source comparison workflow."""

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import Field

from app.comparison import compare_sources
from app.extraction import (
    MAX_SOURCE_CHARACTERS,
    ExtractionProviderError,
    ExtractionResponseError,
    extract_source,
)
from app.schemas import StrictModel


app = FastAPI(
    title="Clyro API",
    description=(
        "Compare two opportunity source texts, preserve their evidence, "
        "and identify matching, conflicting, or missing claims."
    ),
    version="0.1.0",
)


class CompareRequest(StrictModel):
    """Two pasted source descriptions for the same opportunity."""

    source_a: str = Field(min_length=1, max_length=MAX_SOURCE_CHARACTERS)
    source_b: str = Field(min_length=1, max_length=MAX_SOURCE_CHARACTERS)


class CompareResponse(StrictModel):
    """Evidence-preserving comparison result."""

    findings: list[dict[str, Any]]


@app.exception_handler(ExtractionProviderError)
async def handle_provider_error(
    _request: Request, exc: ExtractionProviderError
) -> JSONResponse:
    """Log provider failures locally while keeping the client response generic."""
    print(f"Clyro extraction provider error: {exc}", flush=True)
    return JSONResponse(
        status_code=502,
        content={
            "error": "extraction_provider_error",
            "message": (
                "The extraction service could not process the sources. "
                "Check the backend API key and provider availability, then retry."
            ),
        },
    )


@app.exception_handler(ExtractionResponseError)
async def handle_extraction_error(
    _request: Request, exc: ExtractionResponseError
) -> JSONResponse:
    """Reject malformed model output or evidence without comparing it."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "extraction_validation_error",
            "message": str(exc),
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Lightweight process health check; does not call the model provider."""
    return {"status": "ok"}


@app.post("/api/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    """Extract, validate, and compare two opportunity source texts."""
    source_a = extract_source(request.source_a)
    source_b = extract_source(request.source_b)
    result = compare_sources(source_a, source_b)
    return CompareResponse(**result)

@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    """Serve the Clyro MVP interface."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")
