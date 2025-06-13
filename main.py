import os
import uvicorn
from pydantic import BaseModel
from typing import Optional, List

from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, HTTPException

from services.utils import get_summary
from routes.comments import fetch_comments
from routes.videos import fetch_transcript

from routes.pdf_assistant_api import extract_texts_from_files, generate_gemini_response, app_state



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



#PDF Routes
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
    # response_text = generate_gemini_response(question, context)
    response_text = get_summary(context)
    return {"response": response_text}


# YouTube Comment Routes
@app.post("/summarize_comments")
async def summarize_youtube_comments(request: Params):
    try:
        comments = fetch_comments(request.url)
        summary = get_summary(comments)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# YouTube Video Routes
@app.post("/summarize_videos")
async def summarize_youtube_videos(request: Params):
    try:
        video_summary = fetch_transcript(request.url)
        summary = get_summary(video_summary)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))