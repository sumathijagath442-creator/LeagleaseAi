from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ai_core.gemini_generator import GeminiGenerator

router = APIRouter()


class GenerateRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: str


class GenerateResponse(BaseModel):
    document: str


@router.get("/health")
def route_health():
    return {"status": "healthy"}


@router.post("/generate", response_model=GenerateResponse)
def generate_document(request: GenerateRequest):
    try:
        generator = GeminiGenerator()

        document = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
        )

        return GenerateResponse(document=document)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc