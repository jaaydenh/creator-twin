from langchain_core.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import TokenTextSplitter
from typing import List

texts=None

def get_transcript(video_id:list[str]):
    ytt_api = YouTubeTranscriptApi()
    content=[]
    for id in video_id:
        content.append(ytt_api.fetch(id))

    script=[]
    for transcript in content:
        curr=""
        for i in transcript:
            curr+=i.text
        script.append(curr)
    return "\n".join(script)





def split_text(script):
    global texts
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(script)
    return texts


@tool
def get_script(index:int):
    """
    Get the script for the given index
    Args:
        index: The index of the script to get
    Returns:
        The script for the given index
    """
    global texts
    print(f"Getting script for index {index}")
    return texts[index]



def video_to_chunks(id: str = "iv-5mZ_9CPY") -> List[str]:
  ytt_api = YouTubeTranscriptApi()
  trans=ytt_api.fetch(id)
  s = ""
  for i in trans:
    s+= i.text
  text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=60)

  texts = text_splitter.split_text(s)
  return texts