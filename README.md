# YouTube Comment Summarizer

## Overview
The **YouTube Comment Summarizer** is a web-based tool built using **Streamlit** that allows users to extract comments from any YouTube video and generate a concise summary using **Google Gemini** and **LangChain** models. It leverages the YouTube API to fetch comments and uses Natural Language Processing (NLP) techniques to summarize the extracted text.

## Features
- **YouTube API Integration**: Fetches comments from any public YouTube video.
- **Summarization**: Uses Google Gemini model paired with LangChain to generate meaningful summaries.
- **Streamlit Interface**: Provides a simple, interactive web app to input a YouTube video URL and view the summary.

## Project Structure
- `comments.py`: Handles fetching comments from YouTube via YouTube Data API.
- `app.py`: Main Streamlit app to interact with the user and display the summarized comments.
- `util.py`: Contains the logic for tokenization and summarization using Google Gemini via LangChain.
## Example Workflow

1. **Input**: Paste the URL of a YouTube video.
    - Example: `https://www.youtube.com/watch?v=xyz123`
  
2. **Processing**: The tool will fetch the comments using the YouTube API, tokenize them, and then generate a summary using Google Gemini and LangChain.

3. **Output**: A summary of the comments will be displayed.

## Dependencies

- `streamlit`: For building the web interface.
- `googleapiclient`: For YouTube API integration.
- `pytube`: To extract the video ID from YouTube URLs.
- `openai`: For GPT-4 based summarization (if needed).
- `langchain`: For advanced text processing and summarization.
- `langchain_google_genai`: To interact with Google Gemini for generating summaries.

Install them via `pip` using the `requirements.txt` file.

## API Keys
This project uses the following APIs:
- **YouTube Data API**: For fetching YouTube comments.
- **Google Gemini**: For generating summaries via LangChain.
- **OpenAI GPT-4**: As a backup for summarization.

## Contributing
Contributions are welcome! Feel free to fork the repository, create a new branch, and submit a pull request.

## Acknowledgments
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [LangChain](https://langchain.com/)
- [Google Gemini](https://developers.google.com/ai/gemini)


## Create and activate a virtual environment:
```python

python -m venv .venv

.venv\Scripts\activate

```