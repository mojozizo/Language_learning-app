"""
Dictionary API routes.
"""
from fastapi import APIRouter, Query, HTTPException
# Using absolute imports to avoid import issues
from services.wiktionary import WiktionaryService
from models.schemas import DefinitionResponse

# Create API router
router = APIRouter()

@router.get("/define/{word}", response_model=DefinitionResponse)
async def get_definition(word: str):
    """
    Get definition for a word.
    """
    try:
        return await WiktionaryService.get_definition(word)
    except Exception as e:
        # Return a 500 error with the exception message
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/downloadpdf/{word}")
async def download_pdf(word: str):
    """
    Download the PDF for a word from Wiktionary.
    """
    try:
        return await WiktionaryService.get_pdf(word)
    except Exception as e:
        # Return a 500 error with the exception message
        raise HTTPException(status_code=500, detail=str(e))
        