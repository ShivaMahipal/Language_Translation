import streamlit as st
from utils import (
    translate_docx,
    translate_pptx,
    translate_pdf,
    log_activity,
    translate_text_chunk,
    detect_and_report_language, # Added new import
)
import os
import pandas as pd

# Set page config
st.set_page_config(page_title="Translate-Pro", page_icon="ðŸŒ ")

# Function to load local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load custom CSS
local_css("style.css")

# Custom title with symbol
st.markdown(
    '<h1 style="text-align: left;">ðŸŒ Translate-Pro</h1>',
    unsafe_allow_html=True
)

# Initialize session state variables
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""
if 'source_language_name' not in st.session_state:
    st.session_state.source_language_name = ""
if 'download_path' not in st.session_state:
    st.session_state.download_path = None

# Language selection dictionary
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'zh-cn': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'ru': 'Russian',
    'pt': 'Portuguese',
    # Add more languages as needed by langdetect
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan', 'ceb': 'Cebuano', 'ny': 'Chichewa', 'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'eo': 'Esperanto', 'et': 'Estonian', 'fi': 'Finnish', 'gl': 'Galician', 'ka': 'Georgian', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'iw': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer', 'rw': 'Kinyarwanda', 'ku': 'Kurdish (Kurmanji)', 'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian', 'or': 'Odia (Oriya)', 'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pa': 'Punjabi', 'ro': 'Romanian', 'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish', 'tg': 'Tajik', 'ta': 'Tamil', 'tt': 'Tatar', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'tk': 'Turkmen', 'uk': 'Ukrainian', 'ur': 'Urdu', 'ug': 'Uyghur', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu',
}
NAMES_TO_CODES = {v: k for k, v in LANGUAGE_NAMES.items()}

# Create directories
if not os.path.exists("uploads"):
    os.makedirs("uploads")
if not os.path.exists("translated_files"):
    os.makedirs("translated_files")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Text Translation", "File Translation", "Activity Logs"])

# --- Tab 1: Text Translation ---
with tab1:
    st.header("Translate Text Instantly")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Enter text to translate")
        text_to_translate = st.text_area("", height=250, key="text_to_translate_input")

    with col2:
        st.subheader("Translated Text")
        st.text_area("", st.session_state.translated_text, height=250, key="translated_text_area")

    if st.session_state.source_language_name:
        st.info(f"Detected source language: {st.session_state.source_language_name}")

    target_language_text = st.selectbox(
        "Select target language",
        list(LANGUAGE_NAMES.values()),
        key="text_translation_language"
    )

    if st.button("Translate Text"):
        if text_to_translate and target_language_text:
            # Detect language for reporting
            detected_code = detect_and_report_language(text_to_translate)
            if detected_code == "multi":
                st.session_state.source_language_name = "Multi-Language detected"
            else:
                st.session_state.source_language_name = LANGUAGE_NAMES.get(detected_code, "Unknown")

            with st.spinner("Translating text..."):
                target_language_code = NAMES_TO_CODES[target_language_text]
                st.session_state.translated_text = translate_text_chunk(text_to_translate, target_language_code)
            st.rerun()
        else:
            st.warning("Please enter text and select a target language.")

# --- Tab 2: File Translation ---
with tab2:
    st.header("Translate Your Documents")
    st.write("Upload your file, select a language, and get a fully formatted translated version back.")

    uploaded_file = st.file_uploader(
        "Upload a document (.docx, .pptx, .pdf)", type=["docx", "pptx", "pdf"]
    )
    target_language_file = st.selectbox(
        "Select target language",
        list(LANGUAGE_NAMES.values()),
        key="file_translation_language"
    )

    if st.button("Translate File"):
        if uploaded_file is not None and target_language_file:
            file_path = os.path.join("uploads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            file_extension = os.path.splitext(file_path)[1].lower()
            target_code = NAMES_TO_CODES[target_language_file]
            
            new_path = None
            with st.spinner(f"Translating {uploaded_file.name}... This may take a moment."):
                try:
                    if file_extension == ".docx":
                        new_path = translate_docx(file_path, target_code)
                    elif file_extension == ".pptx":
                        new_path = translate_pptx(file_path, target_code)
                    elif file_extension == ".pdf":
                        new_path = translate_pdf(file_path, target_code)
                    
                    st.session_state.download_path = new_path
                    log_activity(
                        "file_translation",
                        uploaded_file.name,
                        "auto",
                        target_language_file,
                    )
                except Exception as e:
                    st.error(f"An error occurred during translation: {e}")
                    st.session_state.download_path = None
            st.rerun()
        else:
            st.warning("Please upload a file and select a target language.")

    if st.session_state.download_path:
        st.success(f"Your file has been successfully translated!")
        with open(st.session_state.download_path, "rb") as f:
            st.download_button(
                label="Download Translated File",
                data=f,
                file_name=os.path.basename(st.session_state.download_path),
            )

# --- Tab 3: Activity Logs ---
with tab3:
    st.header("Your Translation History")
    if os.path.exists("user_log.csv"):
        log_df = pd.read_csv("user_log.csv")
        if "Username" in log_df.columns:
            log_df = log_df.drop(columns=["Username"])
        st.dataframe(log_df)
    else:
        st.info("No activity logs found.")
