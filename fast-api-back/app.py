from fastapi import FastAPI,Body
from fastapi.params import Query
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from config.client import model
from tools.my_details import my_info
from tools.tools import tools
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from tools.get_details import get_personality
from models.api_models import VideoId
from database.pinecone_upsert import upsert_video_chunks_to_pinecone
from database.pinecone_retriever import semantic_search_by_creator
from database.charachter_db import store_video_chunks_in_db,create_video_creator_table,insert_video_creator
import uvicorn
app=FastAPI()



@app.get("/")
def health():
    return {"message": "Hello, I am alive!"}




@app.post("/generate_personality_from_videos",)
def personality(video_id:VideoId=Body(...)):
    return get_personality(list(video_id.video_id))


@app.get("/creator_background_details")
def my_details():
    return my_info()



# @app.post("/create_table")
# def create_table():
  
#     return {"message": "Table created"}


@app.post("/load_data")
def load_data_to_pinecone(creator_id : str, video_id:VideoId=Body(...)):

    try:
        create_video_creator_table()
        store_video_chunks_in_db(video_id=video_id.video_id[0])
        insert_video_creator(creator_id = creator_id, video_id = video_id)
        upsert_video_chunks_to_pinecone(video_id=video_id.video_id[0])
        return {"message": "Data loaded to Pinecone"}
    except Exception as e:
        return {"message": f"Error loading data to Pinecone: {e}"}


@app.get("/retrieve_pinecone_data")
def retrieve_data(creator_id: str, search_query:str):
    try:
        return semantic_search_by_creator(creator_id=creator_id, search_query=search_query)
    except Exception as e:
        return {"message": f"Error retrieving data: {e}"}