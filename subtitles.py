from .transcription import transcribe_video
from .translation import translate_video
from datetime import datetime, timedelta

# 6. matching timestamps for transcript and translation subtitles:
def convert_time(time):
    h, m, s_ms = time.split(':')
    s, ms = s_ms.split('.')
    td = timedelta(hours = int(h), minutes = int(m), seconds = int(s), milliseconds = int(ms))
    return int(td.total_seconds() * 1000)

def match_timestamps(transcript, translation):
    #transcript = transcribe_video(yt_url, transcription_language)
    #translation = translate_video(yt_url, transcription_language, translation_language)

    # merge the transcript and translation text according to transcript timestamps
    transcript_index = 0
    for translation_index in range(len(translation)):
        starttime = convert_time(translation[translation_index]['start_time'])
        endtime = convert_time(translation[translation_index]['end_time'])
        mid_translation = starttime + (endtime - starttime) / 2

        transcript_endtime = convert_time(transcript[transcript_index]['end_time'])
        
        while (mid_translation > transcript_endtime): 
            transcript_index += 1
            if (len(transcript) > transcript_index): 
                transcript_endtime = convert_time(transcript[transcript_index]['end_time'])
            else: 
                transcript_endtime = mid_translation
                transcript_index = len(transcript) - 1
        
        if ('translation' not in transcript[transcript_index]):
            transcript[transcript_index]['translation'] = translation[translation_index]['text']
        else:
            transcript[transcript_index]['translation'] += translation[translation_index]['text']
        
        print(transcript_index, transcript[transcript_index]['text'], translation_index, transcript[transcript_index]['translation'])

    return transcript

# used for subtitles api
def video_subtitles(yt_url, transcription_language, translation_language): 
    transcript = transcribe_video(yt_url, transcription_language)
    translation = translate_video(yt_url, transcription_language, translation_language)
    return match_timestamps(transcript, translation)