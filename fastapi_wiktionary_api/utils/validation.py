"""
Validation utilities for the Wiktionary API.
Provides functions for cleaning words and validating language codes.
"""
import pycountry
from fastapi import HTTPException

def clean_word(word: str) -> str:
    """
    Clean a word for use in a URL.
    Trims whitespace, converts to lowercase, and replaces spaces with underscores.
    
    Args:
        word: The word to clean
        
    Returns:
        Cleaned word string
    """
    return word.strip().lower().replace(' ', '_')

def validate_language(lang_code: str):
    """
    Validate a language code and return the Language object.
    Tries multiple methods to find a matching language.
    
    Args:
        lang_code: Language code or name
        
    Returns:
        pycountry.Language object
        
    Raises:
        HTTPException: If the language code is invalid
    """
    try:
        # Try to get language by name or code
        language = None
        
        # Try alpha_2 code (e.g., 'de' for German)
        try:
            language = pycountry.languages.get(alpha_2=lang_code.lower())
        except (AttributeError, KeyError):
            pass
        
        # If not found, try alpha_3 code (e.g., 'deu' for German)
        if not language:
            try:
                language = pycountry.languages.get(alpha_3=lang_code.lower())
            except (AttributeError, KeyError):
                pass
        
        # If not found, try full name (e.g., 'German')
        if not language:
            try:
                language = pycountry.languages.get(name=lang_code.title())
            except (AttributeError, KeyError):
                pass
        
        # If still not found, try partial name matching
        if not language:
            language = next(
                (lang for lang in pycountry.languages 
                 if lang_code.lower() in lang.name.lower()), 
                None
            )
        
        # If no language is found, raise an exception
        if not language:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid language: {lang_code}"
            )
        
        return language
        
    except Exception as e:
        # Catch and wrap any other errors
        raise HTTPException(
            status_code=400, 
            detail=f"Error validating language: {str(e)}"
        )
