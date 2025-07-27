import sqlite3
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pinecone import Pinecone
import os

load_dotenv()

class Settings(BaseSettings):
    pinecone_namespace: str = "default"
    pinecone_top_k: int = 10
    pinecone_api_key: str

try:
    settings = Settings(pinecone_api_key=os.getenv("PINECONE_API_KEY"))
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Please ensure 'PINECONE_API_KEY' is in .env file.")
    settings = None
