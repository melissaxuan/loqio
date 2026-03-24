import whisper
from whisper.utils import get_writer
import yt_dlp
import ffmpeg
from datetime import datetime
import tqdm
import sys
import re
import torch
import os

#####

### 1. grab audio file from youtube video:

# grabbing audio file from youtube video and saving as m4a
def get_yt_audio(yt_url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([yt_url])

    print(error_code)

# grabbing subtitles only if youtube video has them and saving as srt
def get_yt_subtitles(yt_url):
    ydl_opts = {
        'writesubtitles': True,
        # 'writeautomaticsub': True,
        'subtitlesformat': 'srt',
        'skip_download': True,
        'outtmpl': '%(id)s.%(ext)s',
        'no_cache': True,
        # 'subtitleslangs': ['en','zh-Hans'],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([yt_url])
    
    print(error_code)

#####

### 2. transcribe audio file using whisper:

# Define a custom tqdm class
class _CustomProgressBar(tqdm.tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current = self.n

    def update(self, n):
        super().update(n)
        self._current += n
        # Add your custom progress handling here (e.g., updating a GUI)
        # print(f"Progress: {self._current}/{self.total}") # Optional: for console output

def extract_yt_video_id(yt_url):
    # Extract the video ID from the YouTube URL
    if "v=" in yt_url:
        return yt_url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in yt_url:
        return yt_url.split("youtu.be/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL")
    
def translate_audio(file, language, target_language):
    translate_module = sys.modules['whisper.transcribe']
    translate_module.tqdm.tqdm = _CustomProgressBar

    model = whisper.load_model("large-v2")
    decode_options = {
    "language": language,
    "verbose": False, # verbose=False is often required for the progress bar to appear/callback to work
    }
    model_opt = dict(task="translate", **decode_options)
    result = model.transcribe(file, **model_opt)
    writer = get_writer("srt", ".")
    yt_video_id = file.split(".")[0]  # Assuming the file is named as "{video_id}.m4a"
    writer(result, f"{yt_video_id}-{target_language}.srt")
    for segment in result['segments']:
        print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")

    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def process_translation(transcription):
    blocks = transcription.split('\n\n')
    processed_lines = []
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_range = lines[1]
            text = lines[2]
            start_time = time_range.split(' --> ')[0]
            end_time = time_range.split(' --> ')[1]
            # Convert the time format from "00:00:00,000" to "0:00:00"
            formatted_start_time = format_time(start_time)
            formatted_end_time = format_time(end_time)
            processed_line = f"[{formatted_start_time} - {formatted_end_time}]{text}"
            processed_lines.append(processed_line)
    return '\n'.join(processed_lines)

def format_time(time):
    return datetime.strptime(time, "%H:%M:%S,%f").strftime("%H:%M:%S")

#####

### 3. turn transcription into dict:

def parse_translation_srt(srt):
    with open(srt, "r", encoding="utf-8") as f:
        srt_content = f.read()

    content = srt_content.replace('\r\n', '\n').strip()
    blocks = re.split(r'\n\n+', content)
    transcript = []

    for block in blocks:
        lines = block.split('\n')
        if (len(lines) >= 3):
            index = lines[0].strip()

            times = lines[1].split(' --> ')

            if (len(times) == 2):
                text = " ".join(lines[2:]).strip()
                transcript.append({
                    "index": index,
                    "start_time": times[0].strip().replace(',', '.'),
                    "end_time": times[1].strip().replace(',', '.'),
                    "text": text
                })

    return transcript

#####

### 4. put all together for api:

def translate_video(yt_url, language, target_language):
    video_id = extract_yt_video_id(yt_url)
    
    if not os.path.exists(f"{video_id}.m4a"):
        get_yt_audio(yt_url)
        
    audio_file = f"{video_id}.m4a"

    translate_audio(audio_file, language, target_language)
    srt_file = f"{video_id}-{target_language}.srt"
    transcript = parse_translation_srt(srt_file)
    return transcript

#####