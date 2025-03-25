"""
Pydantic models for API request and response validation.
"""
from pydantic import BaseModel
from typing import List, Optional

class DefinitionResponse(BaseModel):
    """
    Response model for word definitions.
    """
    word: str
    language: str
    definitions: str
    source_url: str
