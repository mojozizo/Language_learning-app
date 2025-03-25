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
