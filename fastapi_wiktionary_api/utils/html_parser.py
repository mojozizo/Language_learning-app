"""
HTML parser utilities for Wiktionary API responses.
"""
from html.parser import HTMLParser

class DefinitionHTMLParser(HTMLParser):
    """
    HTML parser for extracting clean text from definition HTML.
    """
    def __init__(self):
        """Initialize the parser with empty sentence and tag stack."""
        super().__init__()
        self.reset()
        self.sentence = []  # List to accumulate text fragments
        self.current_tag = []  # Stack to track current HTML tags
    
    def handle_starttag(self, tag, attrs):
        """
        Process opening HTML tags.
        """
        # Add tag to the current tag stack
        self.current_tag.append(tag)
        # Handle line breaks by adding newline character
        if tag == 'br':
            self.sentence.append('\n')
    
    def handle_endtag(self, tag):
        """
        Process closing HTML tags.
        """
        # Remove tag from the current tag stack
        while tag in self.current_tag:
            self.current_tag.pop()
    
    def handle_data(self, data):
        """
        Process text content within HTML.
        """
        # Skip text in hyperlinks (a tags)
        if 'a' not in self.current_tag:
            self.sentence.append(data.strip())
    
    def get_clean_text(self) -> str:
        """
        Get the accumulated text as a clean string.
        """
        return ''.join(self.sentence).strip()
    
    def reset(self):
        """Reset the parser state."""
        super().reset()
        self.sentence = []
        self.current_tag = []

class PronunciationHTMLParser(HTMLParser):
    """
    HTML parser for extracting IPA pronunciations from HTML.
    """
    def __init__(self):
        """Initialize the parser with empty IPA list."""
        super().__init__()
        self.reset()
        self.ipas = []  # List to accumulate IPA pronunciations
        self.in_ipa = False  # Flag to track if we're inside an IPA span
    
    def handle_starttag(self, tag, attrs):
        """
        Process opening HTML tags, looking for IPA spans.
        """
        # Check if this is an IPA span
        if tag == 'span':
            attrs_dict = dict(attrs)
            if attrs_dict.get('class') == 'IPA':
                self.in_ipa = True
    
    def handle_data(self, data):
        """
        Process text content within HTML.
        """
        # If we're inside an IPA span, add the text to our list
        if self.in_ipa:
            self.ipas.append(data)
            self.in_ipa = False  # Reset flag after capturing IPA
    
    def reset(self):
        """Reset the parser state."""
        super().reset()
        self.ipas = []
        self.in_ipa = False