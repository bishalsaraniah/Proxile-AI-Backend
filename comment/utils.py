import os
import openai
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain_text_splitters import TokenTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')


def get_summary(text):
    #Tokenization
    text_splitter = TokenTextSplitter(
    chunk_size=1000, 
    chunk_overlap=10
    )
    
    chunks = text_splitter.create_documents([text])

    #Summarization
    llm = ChatGoogleGenerativeAI(
        # model="gemini-pro",
        model="gemini-1.5-flash",
        # model="gemini-2.5-flash",
        # model="gemini-1.5-pro",
        # model="gemini-1.5-flash-8b-001",
        google_api_key=gemini_api_key
    )
                                                                
    chain = load_summarize_chain(
        llm, 
        chain_type="map_reduce"
    )

    #Invoke Chain
    response=chain.run(chunks)

    return response