
import streamlit as st
from utils import (
    extract_text,
    detect_language,
    translate_text,
    create_pdf,
    log_activity,
)
import os

st.title("Document Translator")

# Create a directory for uploads if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Create a directory for translated files if it doesn't exist
if not os.path.exists("translated_files"):
    os.makedirs("translated_files")

uploaded_file = st.file_uploader(
    "Upload a document (.docx, .pptx, .pdf)", type=["docx", "pptx", "pdf"]
)
username = st.text_input("Enter your username")
target_language = st.selectbox(
    "Select target language",
    [
        "English",
        "Spanish",
        "French",
        "German",
        "Chinese (Simplified)",
        "Japanese",
        "Korean",
        "Arabic",
        "Russian",
        "Portuguese",
    ],
)

if st.button("Translate"):
    if uploaded_file is not None and username and target_language:
        file_path = os.path.join("uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract text from the document
        original_text = extract_text(file_path)

        if original_text:
            # Detect the language of the original text
            source_language = detect_language(original_text)
            st.write(f"Detected source language: {source_language}")

            # Translate the text
            translated_text = translate_text(
                original_text, source_language, target_language
            )

            if translated_text:
                st.subheader("Original Text")
                st.text_area("Original Text", original_text, height=200)

                st.subheader("Translated Text")
                st.text_area("Translated Text", translated_text, height=200)

                # Generate and provide a download link for the translated PDF
                pdf_path = os.path.join(
                    "translated_files", f"{os.path.splitext(uploaded_file.name)[0]}_translated.pdf"
                )
                create_pdf(translated_text, pdf_path)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "Download Translated PDF",
                        f,
                        file_name=os.path.basename(pdf_path),
                    )

                # Log the activity
                log_activity(
                    username,
                    uploaded_file.name,
                    source_language,
                    target_language,
                )
            else:
                st.error("Translation failed.")
        else:
            st.error("Could not extract text from the document.")
    else:
        st.warning("Please upload a file, enter your username, and select a target language.")
