"""Admin/dev endpoints for enriching charger + EV data via the Jina Reader API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.jina_reader import fetch_url_as_markdown, extract_rows_from_markdown, JinaReaderError

router = APIRouter(prefix="/tools", tags=["tools"])


class ScrapeRequest(BaseModel):
    url: str = Field(..., description="Public URL to read (charger locator, spec sheet, etc.)")
    target_selector: Optional[str] = Field(None, description="Optional CSS selector to scope the page")


class ScrapeResponse(BaseModel):
    url: str
    chars: int
    preview: str
    table_rows: list[dict] = []


@router.post("/jina-read", response_model=ScrapeResponse)
def jina_read(req: ScrapeRequest):
    """Fetch a URL via Jina Reader and return clean markdown (plus any parsed table)."""
    try:
        markdown = fetch_url_as_markdown(req.url, target_selector=req.target_selector)
    except JinaReaderError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    rows = extract_rows_from_markdown(markdown)

    return ScrapeResponse(
        url=req.url,
        chars=len(markdown),
        preview=markdown[:600],
        table_rows=rows[:50],  # cap the response
    )
