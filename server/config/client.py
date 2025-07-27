from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(
    api_key=api_key,
    model="gpt-4",
    temperature=0.5
)
