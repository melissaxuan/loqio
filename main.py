from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .transcription import transcribe_video
from .translation import translate_video
from .subtitles import video_subtitles
# from httpx import HTTPException

app = FastAPI()

origins = [
    "http://localhost:3000", # frontend port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscribeRequest(BaseModel):
    video_url: str
    video_language: str
    
class TranslateRequest(BaseModel):
    video_url: str
    video_language: str
    target_language: str | None = "en"

@app.get("/")
async def root():
    return {"message": "Welcome to loqio!"}

@app.post("/transcribe")
async def transcribe(request: TranscribeRequest):
    # if not request.video_url.startswith("http"):
    #     raise HTTPException(status_code=400, detail="Invalid URL")

    transcript = transcribe_video(request.video_url, request.video_language)

    return {
        "status": "success",
        "message": f"Processed {request.video_url} in {request.video_language}",
        "transcription": transcript,
    }

@app.post("/translate")
async def translate(request: TranslateRequest):
    # if not request.video_url.startswith("http"):
    #     raise HTTPException(status_code=400, detail="Invalid URL")

    translation = translate_video(request.video_url, request.video_language, request.target_language)

    return {
        "status": "success",
        "message": f"Processed {request.video_url} from {request.video_language} to {request.target_language}",
        "translation": translation,
    }

@app.post("/subtitles")
async def subtitles(request: TranslateRequest):
    matched_subtitles = video_subtitles(request.video_url, request.video_language, request.target_language)

    return {
        "status": "success",
        "message": f"Processed {request.video_url} from {request.video_language} to {request.target_language}",
        "subtitles": matched_subtitles,
    }