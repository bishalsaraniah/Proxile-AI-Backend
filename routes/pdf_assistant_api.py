import os
import PyPDF2
import tempfile
from typing import List
from dotenv import load_dotenv
from fastapi import HTTPException
import google.generativeai as genai
from gtts import gTTS  # Google Text-to-Speech

# Load environment variables
load_dotenv()

# Configure the Gemini Pro model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Application state dictionary to hold shared context
app_state = {
    "pdf_context": ""
}

def extract_text_from_pdf_fileobj(fileobj) -> str:
    """Extract text from a PDF file-like object using PyPDF2."""
    try:
        reader = PyPDF2.PdfReader(fileobj)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from PDF: {e}")

def extract_texts_from_files(files: List) -> str:
    """Extract and concatenate text from a list of UploadFile."""
    combined_text = ""
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename} is not a PDF")
        file_content = file.file.read()
        from io import BytesIO
        combined_text += extract_text_from_pdf_fileobj(BytesIO(file_content))
        file.file.close()
    return combined_text

def generate_gemini_response(question: str, context: str) -> str:
    """Send question + context to Gemini AI and get the response text."""
    chat = model.start_chat(history=[])
    full_message = context + "\n\n" + question
    response = chat.send_message(full_message, stream=True)
    response_text = ''.join([chunk.text for chunk in response])
    return response_text

def generate_tts_audio(text: str) -> str:
    """Generate speech audio (mp3) for given text and return the path."""
    tts = gTTS(text=text, lang='en')
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file_path = temp_file.name
    temp_file.close()
    tts.save(temp_file_path)
    return temp_file_path

def store_feedback_to_file(user_input: str, bot_response: str) -> None:
    """Append user input and bot response to a feedback log file."""
    try:
        with open("feedback_log.txt", "a", encoding="utf-8") as f:
            f.write(f"User: {user_input}\nBot: {bot_response}\n\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store feedback: {e}")

