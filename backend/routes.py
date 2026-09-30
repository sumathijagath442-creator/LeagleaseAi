from fastapi import APIRouter, HTTPException

from ai_core.gemini_generator import GeminiDocumentGenerator
from backend.schemas import DocumentRequest


router = APIRouter()

generator = GeminiDocumentGenerator()


@router.post("/generate")
def generate_document(request: DocumentRequest):

    try:

        generated_text = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            jurisdiction=request.jurisdiction,
            additional_instructions=request.additional_instructions,
        )

        return {
            "success": True,
            "document_type": request.document_type,
            "content": generated_text,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {exc}",
        ) from exc