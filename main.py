from fastapi import FastAPI
from pydantic import BaseModel
from .transcription import transcribe_video
# from httpx import HTTPException

app = FastAPI()

class VideoRequest(BaseModel):
    video_url: str
    video_language: str
    
@app.get("/")
async def root():
    return {"message": "Welcome to loqio!"}

@app.post("/transcribe/")
async def transcribe(request: VideoRequest):
    # if not request.video_url.startswith("http"):
    #     raise HTTPException(status_code=400, detail="Invalid URL")

    transcript = transcribe_video(request.video_url, request.video_language)

    return {
        "status": "success",
        "message": f"Processed {request.video_url} in {request.video_language}",
        "transcription": transcript,
    }
