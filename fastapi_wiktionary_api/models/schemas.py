"""
Pydantic models for API request and response validation.
These models define the structure of the API responses.
"""
from pydantic import BaseModel
from typing import List, Optional

class DefinitionResponse(BaseModel):
    """
    Response model for word definitions.
    
    Attributes:
        word: The word that was looked up
        language: The language of the definition
        definitions: Formatted string containing definitions
        source_url: URL to the Wiktionary page for the word
    """
    word: str
    language: str
    definitions: str
    source_url: str

class PronunciationResponse(BaseModel):
    """
    Response model for word pronunciations.
    
    Attributes:
        word: The word that was looked up
        language: The language of the pronunciation
        pronunciations: List of IPA pronunciations
        formatted_output: Optional formatted output for sentence pronunciation
        source_url: URL to the Wiktionary page for the word
    """
    word: str
    language: str
    pronunciations: List[str]
    formatted_output: Optional[str] = None
    source_url: str