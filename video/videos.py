import os
from pytube import extract
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import openai

load_dotenv()

# Load OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

def extract_video_id_from_link(url):
    return extract.video_id(url)

def fetch_transcript(video_url):
    video_id = extract_video_id_from_link(video_url)
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript_list])
        return transcript_text
    except TranscriptsDisabled:
        return None  # Transcript not available

def get_summary(transcript, max_length=3000):
    """
    Generate a summary of the video transcript using OpenAI.
    """
    if len(transcript) > max_length:
        transcript = transcript[:max_length]

    prompt = (
        "You are an AI assistant. Summarize the following YouTube video transcript into a few informative paragraphs:\n\n"
        f"{transcript}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Or "gpt-4o" if available
        messages=[
            {"role": "system", "content": "You are a helpful summarization assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.5,
    )

    summary = response['choices'][0]['message']['content']
    return summary

# Full pipeline example:
def summarize_youtube_video(video_url):
    transcript = fetch_transcript(video_url)
    if transcript is None:
        return "Transcript not available for this video."
    return get_summary(transcript)