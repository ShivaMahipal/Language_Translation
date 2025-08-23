import os
import pandas as pd
from docx import Document
from pptx import Presentation
import PyPDF2
from deep_translator import GoogleTranslator
from langdetect import detect
from fpdf import FPDF
from datetime import datetime

def extract_text(file_path):
    """Extracts text from a .docx, .pptx, or .pdf file."""
    extension = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if extension == ".docx":
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif extension == ".pptx":
            prs = Presentation(file_path)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
        elif extension == ".pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
    return text


def detect_language(text):
    """Detects the language of a given text."""
    try:
        return detect(text)
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "Unknown"


def translate_text(text, src_lang, dest_lang):
    """Translates text from a source language to a destination language."""
    try:
        # Map language names to language codes for deep-translator
        dest_lang_code = {
            'english': 'en',
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'chinese (simplified)': 'zh-CN',
            'japanese': 'ja',
            'korean': 'ko',
            'arabic': 'ar',
            'russian': 'ru',
            'portuguese': 'pt'
        }.get(dest_lang.lower())

        if not dest_lang_code:
            return "Invalid target language"

        translated = GoogleTranslator(source=src_lang, target=dest_lang_code).translate(text)
        return translated
    except Exception as e:
        print(f"Error translating text: {e}")
        return None



def create_pdf(text, file_path):
    """Creates a PDF file with the given text."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Add the text to the PDF, handling multi-byte characters
        pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.output(file_path)
    except Exception as e:
        print(f"Error creating PDF: {e}")


def log_activity(username, file_name, source_language, target_language):
    """Logs user activity to a CSV file."""
    log_file = "user_log.csv"
    log_entry = {
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "username": [username],
        "file_name": [file_name],
        "source_language": [source_language],
        "target_language": [target_language],
    }
    df = pd.DataFrame(log_entry)
    if os.path.exists(log_file):
        df.to_csv(log_file, mode="a", header=False, index=False)
    else:
        df.to_csv(log_file, index=False)
