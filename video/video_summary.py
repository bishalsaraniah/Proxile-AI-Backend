# Filename: video_summary.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import re
import requests
from bs4 import BeautifulSoup
# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.CouldNotRetrieveTranscript import CouldNotRetrieveTranscript
from openai import OpenAI

app = FastAPI()

class VideoSummaryRequest(BaseModel):
    url: str
    language: str = "English"  # Default language
    max_length: Optional[int] = 1000

def extract_video_id(url: str) -> str:
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    else:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

def get_transcript(video_id: str) -> str:
    try:
        transcript_raw = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'es', 'ko'])
        transcript_full = ' '.join([i['text'] for i in transcript_raw])
        return transcript_full
    except CouldNotRetrieveTranscript as e:
        raise HTTPException(status_code=400, detail=f"Could not retrieve transcript: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transcript: {e}")

def summarize_text(text: str, lang: str = 'en') -> str:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set as environment variable")

    client = OpenAI(api_key=openai_api_key)

    prompt = f"""
    The following text is in its original language. Provide the output in this language: {lang}.
    Format the output as follows:

    Summary:
    short summary of the video

    Key Takeaways:
    succinct bullet point list of key takeaways

    input text: {text}
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
        )
        summary_text = response.to_dict()['choices'][0]['message']['content']
        return summary_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during summarization: {e}")

@app.post("/summarize_video")
async def summarize_youtube_video(request: VideoSummaryRequest):
    try:
        video_id = extract_video_id(request.url)
        transcript = get_transcript(video_id)
        summary = summarize_text(transcript, request.language)
        return {"summary": summary}
    except HTTPException as http_ex:
        raise http_ex # Re-raise HTTPExceptions to be handled by FastAPI
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
