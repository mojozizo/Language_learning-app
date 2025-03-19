import streamlit as st
import fitz  # PyMuPDF
import requests
import tempfile
import os
from PIL import Image
import io
import base64

# Function to call Ollama API for translation
def get_translation(text, source_lang="auto", target_lang="english"):
    # Construct prompt for translation with grammar and examples
    prompt = f"""
    Translate the following text from {source_lang} to {target_lang}:
    
    "{text}"
    
    Please provide:
    1. Translation
    2. Grammar analysis (part of speech, tense, etc.)
    3. 2-3 example sentences using similar phrases or words in the given language
    """
    
    # Call Ollama API
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "stablelm2",  # Change to your preferred Ollama model
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

# Extract all words with their positions from a PDF page
def extract_words_with_positions(doc, page_num):
    page = doc[page_num]
    words = page.get_text("words")
    
    # Format: [x0, y0, x1, y1, word, block_no, line_no, word_no]
    word_list = []
    for word in words:
        word_list.append({
            "text": word[4],
            "rect": [word[0], word[1], word[2], word[3]],
            "block": word[5],
            "line": word[6],
            "word_num": word[7]
        })
    
    return word_list

# Convert PDF page to image
def get_page_as_image(doc, page_num, scale=2):
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))

# Main app
def main():
    st.set_page_config(page_title="PDF Translation Viewer", layout="wide")
    
    # App title
    st.title("PDF Translation Viewer")
    st.markdown("Upload a PDF, select text, and get translations with grammar analysis.")
    
    # Initialize session state
    if 'pdf_doc' not in st.session_state:
        st.session_state.pdf_doc = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'words' not in st.session_state:
        st.session_state.words = []
    if 'selected_text' not in st.session_state:
        st.session_state.selected_text = ""
    if 'translation' not in st.session_state:
        st.session_state.translation = ""
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Save uploaded file to temp location
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "uploaded_pdf.pdf")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Open PDF
        if st.session_state.pdf_doc is None or st.session_state.pdf_doc.name != temp_path:
            st.session_state.pdf_doc = fitz.open(temp_path)
            st.session_state.current_page = 0
        
        # PDF navigation
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("← Previous Page", key="prev_btn"):
                if st.session_state.current_page > 0:
                    st.session_state.current_page -= 1
                    st.session_state.selected_text = ""
                    st.session_state.translation = ""
        
        with col2:
            st.markdown(f"Page: {st.session_state.current_page + 1} / {len(st.session_state.pdf_doc)}")
        
        with col3:
            if st.button("Next Page →", key="next_btn"):
                if st.session_state.current_page < len(st.session_state.pdf_doc) - 1:
                    st.session_state.current_page += 1
                    st.session_state.selected_text = ""
                    st.session_state.translation = ""
        
        # Main content
        pdf_col, translation_col = st.columns([3, 2])
        
        with pdf_col:
            # Extract words with positions
            st.session_state.words = extract_words_with_positions(
                st.session_state.pdf_doc, 
                st.session_state.current_page
            )
            
            # Display PDF page as image
            page_img = get_page_as_image(st.session_state.pdf_doc, st.session_state.current_page)
            st.image(page_img, use_column_width=True)
            
            # Text selection methods
            st.markdown("### Select Text to Translate")
            st.markdown("Choose one of the text selection methods below:")
            
            # Method 1: Select a single word from clickable list
            with st.expander("Method 1: Click on a word", expanded=False):
                st.markdown("#### Words on this page:")
                
                # Display word buttons in a grid
                word_cols = 5
                for i in range(0, len(st.session_state.words), word_cols):
                    cols = st.columns(word_cols)
                    for j in range(word_cols):
                        if i + j < len(st.session_state.words):
                            word = st.session_state.words[i + j]["text"]
                            if word.strip():  # Only display non-empty words
                                with cols[j]:
                                    if st.button(word, key=f"word_{i}_{j}"):
                                        st.session_state.selected_text = word
            
            # Method 2: Enter line and word numbers
            with st.expander("Method 2: Extract by line", expanded=False):
                # Group words by lines
                lines = {}
                for word in st.session_state.words:
                    line_num = word["line"]
                    if line_num not in lines:
                        lines[line_num] = []
                    lines[line_num].append(word["text"])
                
                # Sort lines by line number
                sorted_lines = sorted(lines.items(), key=lambda x: x[0])
                
                # Display lines with buttons
                for i, (line_num, words) in enumerate(sorted_lines):
                    line_text = " ".join(words)
                    if line_text.strip():  # Skip empty lines
                        if st.button(f"Line {i+1}: {line_text[:50]}{'...' if len(line_text) > 50 else ''}", key=f"line_{i}"):
                            st.session_state.selected_text = line_text
            
            # Method 3: Manual text input
            with st.expander("Method 3: Manual text entry", expanded=True):
                # Extract all page text
                page = st.session_state.pdf_doc[st.session_state.current_page]
                page_text = page.get_text()
                
                st.text_area("Full page text (copy what you need):", value=page_text, height=200)
        
        with translation_col:
            # Manual text entry
            st.markdown("### Text to Translate")
            manual_text = st.text_area(
                "Edit or paste text for translation:", 
                value=st.session_state.selected_text,
                height=150,
                key="translation_input"
            )
            
            if manual_text != st.session_state.selected_text:
                st.session_state.selected_text = manual_text
            
            # Language options
            source_lang = st.selectbox(
                "Source Language:", 
                ["auto", "German", ],
                index=0
            )
            
            # Translate button
            if st.button("Translate", type="primary") and st.session_state.selected_text:
                with st.spinner("Translating..."):
                    try:
                        st.session_state.translation = get_translation(
                            st.session_state.selected_text, 
                            source_lang=source_lang
                        )
                    except Exception as e:
                        st.error(f"Translation failed: {str(e)}")
                        st.session_state.translation = ""
            
            # Display translation
            st.markdown("### Translation Result")
            if st.session_state.translation:
                st.markdown(st.session_state.translation)
            else:
                st.info("Select text and click 'Translate' to see results")
    else:
        st.info("Please upload a PDF file to begin")

if __name__ == "__main__":
    main()