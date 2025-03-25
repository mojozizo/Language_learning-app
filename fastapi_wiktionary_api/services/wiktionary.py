"""
Wiktionary service.
This module provides services for interacting with the Wiktionary API
"""
import json
import requests
import pycountry
from html.parser import HTMLParser
from fastapi import HTTPException
from typing import List, Optional

# Using absolute imports to avoid import issues
from utils.html_parser import DefinitionHTMLParser, PronunciationHTMLParser
from utils.validation import clean_word, validate_language

class WiktionaryService:
    """
    Service for interacting with the Wiktionary API.
    """
    
    @staticmethod
    async def get_definition(word: str) -> dict:
        """
        Get definitions for a word.
        """
        # Make request to Wiktionary API definition endpoint
        response = requests.get(
            f"https://en.wiktionary.org/api/rest_v1/page/definition/{clean_word(word)}"
        )
        
        # Check if the request was successful
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Word not found")
        
        # Parse the response to extract definitions
        definitions = WiktionaryService.parse_definition_response(response.json())
        
        # Extract the primary language from the first definition if possible
        primary_language = "unknown"
        if isinstance(response.json(), dict):
            # Take the first available language code that's not 'other'
            for lang_code in response.json().keys():
                if lang_code != 'other' and response.json()[lang_code]:
                    entries = response.json()[lang_code]
                    if entries and 'language' in entries[0]:
                        primary_language = entries[0]['language'].lower()
                        break
        
        # Return formatted response with language field
        return {
            "word": word,
            "definitions": definitions,
            "language": primary_language,
            "source_url": f"https://en.wiktionary.org/wiki/{clean_word(word)}"
        }
    
    @staticmethod
    def parse_definition_response(response: dict) -> str:
        """
        Parse definition response from Wiktionary API.
        """
        parser = DefinitionHTMLParser()
        definitions = []
        
        # Check each language section in the response
        for lang_code, lang_data in response.items():
            # Skip the 'other' section which contains etymologies/related languages
            if lang_code == 'other':
                continue
                
            # Process each entry by part of speech
            for entry in lang_data:
                pos = entry.get('partOfSpeech', '')
                language = entry.get('language', '')
                definitions.append(f"{language} - {pos}:\n")
                
                # Process each definition
                for idx, definition in enumerate(entry.get('definitions', []), 1):
                    # Parse and clean the HTML definition
                    parser.feed(definition.get('definition', ''))
                    definitions.append(f"  {idx}. {parser.get_clean_text()}\n")
                    parser.reset()
                    
                    # Process examples for this definition
                    for example in definition.get('examples', []):
                        parser.feed(example)
                        definitions.append(f"    Example: {parser.get_clean_text()}\n")
                        parser.reset()
        
        # Return all definitions as a single string
        return ''.join(definitions) if definitions else "No definitions found"
