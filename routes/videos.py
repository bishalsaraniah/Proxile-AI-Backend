import os
from pytube import extract
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

load_dotenv()

api_server_name = os.getenv("API_SERVICE_NAME")
api_version = os.getenv('API_VERSION')
youtube_api_key = os.getenv('YOUTUBE_API_KEY')

# def start_youtube_service():
#     return build(api_server_name, api_version, developerKey=youtube_api_key)

def extract_video_id_from_link(url):
    return extract.video_id(url)

# Get transcript data from YouTube
def get_transcript_data(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript_list
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        return f"Transcript not available: {str(e)}"

# Format the transcript data (similar to your load_comments_in_format function)
def load_transcript_in_format(transcript_data):
    if isinstance(transcript_data, str):
        # Error message
        return transcript_data

    transcript_text = ""
    for item in transcript_data:
        transcript_text += item['text'] + " "
    return transcript_text

# Main function that combines everything (similar to your fetch_transcript function)
def fetch_transcript(url):
    video_id = extract_video_id_from_link(url)
    transcript_data = get_transcript_data(video_id)
    transcript_text = load_transcript_in_format(transcript_data)
    return transcript_text