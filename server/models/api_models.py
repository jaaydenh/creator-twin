from pydantic import BaseModel

class VideoId(BaseModel):
    video_id:list[str]
