"""
Wiktionary service.
This module provides services for interacting with the Wiktionary API
to get word definitions and pronunciations.
"""
import json
import requests
import pycountry
from html.parser import HTMLParser
from fastapi import HTTPException
from typing import List, Optional

# Using absolute imports to avoid import issues
from fastapi_wiktionary_api.utils.html_parser import DefinitionHTMLParser, PronunciationHTMLParser
from fastapi_wiktionary_api.utils.validation import clean_word, validate_language

def parse_pronunciation_response(response: dict, language: pycountry.Language) -> List[str]:
    """
    Extract IPA pronunciations from Wiktionary API response.
    
    Args:
        response: JSON response from Wiktionary API
        language: Language object from pycountry
        
    Returns:
        List of IPA pronunciation strings
    """
    parser = PronunciationHTMLParser()
    lang_name = language.name.lower()
    
    # Extract HTML sections from response
    sections = response.get('lead', {}).get('sections', [])
    sections.extend(response.get('remaining', {}).get('sections', []))
    
    # Look for pronunciation sections
    for section in sections:
        # Check if this is a language section (level 2 heading)
        if section.get('toclevel') == 2 and lang_name in section.get('line', '').lower():
            # Found the language section, now find pronunciation subsection
            for subsection in section.get('subsections', []):
                if 'pronunciation' in subsection.get('line', '').lower():
                    # Parse the HTML content to extract IPA notations
                    parser.feed(subsection.get('text', ''))
                    if parser.ipas:
                        return parser.ipas
    
    # Return empty list if no pronunciations found
    return []

class WiktionaryService:
    """
    Service for interacting with the Wiktionary API.
    Provides methods for getting word definitions and pronunciations.
    """
    
    @staticmethod
    async def get_definition(word: str, lang: str) -> dict:
        """
        Get definitions for a word in the specified language.
        
        Args:
            word: The word to look up
            lang: Language code or name
            
        Returns:
            Dictionary containing word definitions and metadata
            
        Raises:
            HTTPException: If the word is not found or an error occurs
        """
        # Validate the language code/name
        language = validate_language(lang)
        
        # Make request to Wiktionary API definition endpoint
        response = requests.get(
            f"https://en.wiktionary.org/api/rest_v1/page/definition/{clean_word(word)}"
        )
        
        # Check if the request was successful
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Word not found")
        
        # Parse the response to extract definitions
        definitions = WiktionaryService.parse_definition_response(response.json(), language)
        
        # Return formatted response
        return {
            "word": word,
            "language": lang,
            "definitions": definitions,
            "source_url": f"https://en.wiktionary.org/wiki/{word}#{lang.title()}"
        }

    @staticmethod
    async def get_pronunciation(word: str, lang: str, sentence: bool) -> dict:
        """
        Get pronunciations for a word or sentence in the specified language.
        
        Args:
            word: The word or sentence to look up
            lang: Language code or name
            sentence: Whether to process the input as a sentence
            
        Returns:
            Dictionary containing pronunciations and metadata
            
        Raises:
            HTTPException: If the word is not found or an error occurs
        """
        # Validate the language code/name
        language = validate_language(lang)
        
        # Make request to Wiktionary API mobile sections endpoint
        # This endpoint contains more detailed HTML sections
        response = requests.get(
            f"https://en.wiktionary.org/api/rest_v1/page/mobile-sections/{clean_word(word)}"
        )
        
        # Check if the request was successful
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Word not found")
        
        # Parse the response to extract IPA pronunciations
        ipas = parse_pronunciation_response(response.json(), language)
        
        # Process differently if input is a sentence
        if sentence:
            return WiktionaryService.process_sentence_pronunciation(word, ipas, lang)
        
        # Return formatted response for a single word
        return {
            "word": word,
            "language": lang,
            "pronunciations": ipas,
            "source_url": f"https://en.wiktionary.org/wiki/{word}"
        }
    
    @staticmethod
    def parse_definition_response(response: dict, language: pycountry.Language) -> str:
        """
        Parse definition response from Wiktionary API.
        
        Args:
            response: JSON response from Wiktionary API
            language: Language object from pycountry
            
        Returns:
            Formatted string containing definitions
        """
        parser = DefinitionHTMLParser()
        definitions = []
        
        # Get the appropriate language code
        lang_code = language.alpha_2 if hasattr(language, 'alpha_2') else language.alpha_3
        lang_data = response.get(lang_code, [])
        
        # Process each entry by part of speech
        for entry in lang_data:
            pos = entry.get('partOfSpeech', '')
            definitions.append(f"{pos}:\n")
            
            # Process each definition
            for idx, definition in enumerate(entry.get('definitions', []), 1):
                # Parse and clean the HTML definition
                parser.feed(definition.get('definition', ''))
                definitions.append(f"  {idx}. {parser.get_clean_text()}\n")
                parser.reset()
                
                # Process examples for this definition
                for example in definition.get('examples', []):
                    parser.feed(example.get('text', ''))
                    definitions.append(f"    Example: {parser.get_clean_text()}\n")
                    parser.reset()
        
        # Return all definitions as a single string
        return ''.join(definitions) if definitions else "No definitions found"

    @staticmethod
    def process_sentence_pronunciation(sentence: str, ipas: List[str], lang: str) -> dict:
        """
        Process pronunciations for a sentence.
        Maps IPA pronunciations to individual words in the sentence.
        
        Args:
            sentence: The sentence to process
            ipas: List of IPA pronunciations
            lang: Language code or name
            
        Returns:
            Dictionary containing sentence pronunciation data
        """
        # Split the sentence into words
        words = sentence.split()
        clean_words = [clean_word(w) for w in words]
        
        # Create a pronunciation map for each word
        # Use [!!!] if no pronunciation is available
        pronunciation_map = {
            word: ipas[i] if i < len(ipas) else '[!!!]'
            for i, word in enumerate(clean_words)
        }
        
        # Format output as aligned columns of words and pronunciations
        word_line = ' '.join(word.ljust(len(pron)) for word, pron in pronunciation_map.items())
        ipa_line = ' '.join(pron.ljust(len(word)) for word, pron in pronunciation_map.items())
        
        # Return formatted response
        return {
            "word": sentence,
            "language": lang,
            "pronunciations": list(pronunciation_map.values()),
            "formatted_output": f"{word_line}\n{ipa_line}",
            "source_url": f"https://en.wiktionary.org/wiki/{clean_word(sentence)}"
        }