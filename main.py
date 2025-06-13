import os
import uvicorn
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Your internal imports
from comment.utils import get_summary
from comment.comments import fetch_comments
from pdf.pdf_assistant_api import (
    extract_texts_from_files,
    generate_gemini_response,
    generate_tts_audio,
    store_feedback_to_file,
    app_state
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeedbackRequest(BaseModel):
    user_input: str
    bot_response: str

class Params(BaseModel):
    url: str
    max_length: Optional[int] = 1000


@app.post("/upload-pdfs")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 PDFs can be uploaded.")
    text_context = extract_texts_from_files(files)
    app_state["pdf_context"] = text_context
    return {"message": f"{len(files)} PDFs uploaded and text extracted.", "text_length": len(text_context)}


@app.post("/ask-question")
async def ask_question(question: str = Form(...)):
    context = app_state.get("pdf_context", "")
    if not context:
        raise HTTPException(status_code=400, detail="No PDF text context available. Upload PDFs first.")
    response_text = generate_gemini_response(question, context)
    return {"response": response_text}


@app.post("/ask-question-with-audio")
async def ask_question_with_audio(question: str = Form(...)):
    context = app_state.get("pdf_context", "")
    if not context:
        raise HTTPException(status_code=400, detail="No PDF text context available. Upload PDFs first.")
    response_text = generate_gemini_response(question, context)
    audio_path = generate_tts_audio(response_text)
    def iterfile():
        with open(audio_path, "rb") as f:
            yield from f
        os.remove(audio_path)
    return StreamingResponse(iterfile(), media_type="audio/mpeg", headers={"X-Response-Text": response_text})


@app.post("/text-to-speech")
async def text_to_speech(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    audio_path = generate_tts_audio(text)
    def iterfile():
        with open(audio_path, "rb") as f:
            yield from f
        os.remove(audio_path)
    return StreamingResponse(iterfile(), media_type="audio/mpeg")

@app.post("/store-feedback")
async def store_feedback(feedback: FeedbackRequest):
    store_feedback_to_file(feedback.user_input, feedback.bot_response)
    return {"message": "Feedback stored successfully."}

@app.post("/store-feedback-form")
async def store_feedback_form(
    user_input: str = Form(...), 
    bot_response: str = Form(...)
):
    store_feedback_to_file(user_input, bot_response)
    return {"message": "Feedback stored successfully."}

# @app.post("/summarize_comments")
# async def summarize_youtube_comments(params: Params):
#     try:
#         comments = fetch_comments(params.url)
#         summary = get_summary(comments, max_length=1000)
#         return {"summary": summary}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize_comments")
async def summarize_youtube_comments(request: Params):
    try:
        # print(f"Received URL: {request.url}")
        # print(f"Max length: {request.max_length}")

        comments = fetch_comments(request.url)
        # print(f"Fetched {len(comments)} comments")

        summary = get_summary(comments)
        # print("Generated summary")

        return {"summary": summary}
    except Exception as e:
        # print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pdf-context-length")
async def get_context_length():
    length = len(app_state.get("pdf_context", ""))
    return {"context_length": length}


@app.post("/clear-context")
async def clear_context():
    app_state["pdf_context"] = ""
    return {"message": "PDF text context cleared."}

