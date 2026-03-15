import whisper
from whisper.utils import get_writer
import yt_dlp
import ffmpeg
from datetime import datetime
# import ffprobe

def get_yt_audio(yt_url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([yt_url])

    print(error_code)

# to list available subs, use `list_subs` in the options to see available translations
# to download specific language subtitles, set `subtitleslangs` to a list, e.g., `['en', 'es']`
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

def transcribe_audio(file):
    model = whisper.load_model("base")
    result = model.transcribe(file)
    writer = get_writer("srt", ".")
    writer(result, "audio.srt")
    for segment in result['segments']:
        print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")
    # return process_transcription(result)
    # print(result["text"])
    # with open(file, "rb") as audio_file:
        # transcription = whisper.audio.transcriptions.create(
            # model="whisper-1", 
            # file=audio_file, 
            # response_format="srt"
        # )
        # Pass the transcription directly for processing
        # return process_transcription(transcription)
        #return response  # Directly return the response, assuming it's the transcription text

# Function to process the raw transcription into the desired format
def process_transcription(transcription):
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
# get_yt_audio("https://www.youtube.com/watch?v=Taw2tAMGIVM")
# get_yt_audio("https://www.youtube.com/watch?v=oLHfnK9IVZs")
# get_yt_subtitles("https://www.youtube.com/watch?v=oLHfnK9IVZs")
transcribe_audio("Taw2tAMGIVM.m4a")