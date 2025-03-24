"""
Dictionary API routes.
This module defines the API endpoints for word definitions and pronunciations.
"""
from fastapi import APIRouter, Query, HTTPException
# Using absolute imports to avoid import issues
from fastapi_wiktionary_api.services.wiktionary import WiktionaryService
from fastapi_wiktionary_api.models.schemas import DefinitionResponse, PronunciationResponse

# Create API router
router = APIRouter()

@router.get("/define/{word}", response_model=DefinitionResponse)
async def get_definition(
    word: str,
    lang: str = Query("german", description="Target language for definition")
):
    """
    Get definition for a word in the specified language.
    
    Args:
        word: The word to look up
        lang: Language code or name (default: german)
        
    Returns:
        DefinitionResponse: Object containing word definitions and metadata
        
    Raises:
        HTTPException: If the word is not found or an error occurs
    """
    try:
        return await WiktionaryService.get_definition(word, lang)
    except Exception as e:
        # Return a 500 error with the exception message
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pronounce/{word}", response_model=PronunciationResponse)
async def get_pronunciation(
    word: str,
    lang: str = Query("german", description="Target language for pronunciation"),
    sentence: bool = Query(False, description="Process as sentence")
):
    """
    Get pronunciation for a word or sentence in the specified language.
    
    Args:
        word: The word or sentence to look up
        lang: Language code or name (default: german)
        sentence: Whether to process the input as a sentence (default: False)
        
    Returns:
        PronunciationResponse: Object containing pronunciations and metadata
        
    Raises:
        HTTPException: If the word is not found or an error occurs
    """
    try:
        return await WiktionaryService.get_pronunciation(word, lang, sentence)
    except Exception as e:
        # Return a 500 error with the exception message
        raise HTTPException(status_code=500, detail=str(e))