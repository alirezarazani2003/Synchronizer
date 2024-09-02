from fastapi import FastAPI, HTTPException
import datetime
import webvtt
from webvtt import Caption, WebVTT
from pydantic import BaseModel
import os
import uvicorn
import logging
from typing import List

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubtitleSyncRequest(BaseModel):
    primary_subtitle: str
    secondary_subtitle: str
    primary_language: str
    secondary_language: str

class SubtitleSyncResponse(BaseModel):
    primary_subtitle: str
    secondary_subtitle: str
    status: str

@app.post("/get_sync_subs", response_model=SubtitleSyncResponse)
async def get_sync_subs(data: SubtitleSyncRequest):
    try:
        sub_one = await json_to_vtt(data.primary_subtitle, data.primary_language)
        sub_two = await json_to_vtt(data.secondary_subtitle, data.secondary_language)
        synced_subs = synchronize_subtitles(sub_one, sub_two)
        primary_sub_str = convert_vtt_to_str(synced_subs[0])
        secondary_sub_str = convert_vtt_to_str(synced_subs[1])

        return SubtitleSyncResponse(
            primary_subtitle=primary_sub_str,
            secondary_subtitle=secondary_sub_str,
            status="synchronized"
        )
    
    except Exception as e:
        logger.error(f"Error processing subtitles: {e}")
        raise HTTPException(status_code=500, detail="Failed to synchronize subtitles")

async def json_to_vtt(json_value: str, name: str) -> WebVTT:
    """Converts JSON subtitle text to VTT format and saves it to a file."""
    vtt_content = "WEBVTT\n\n" + json_value.replace('\r\n', '\n')
    file_path = f"files/{name}.vtt"

    try:

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(vtt_content)
        
        validate_vtt_format(file_path)
        return webvtt.read(file_path)

    except Exception as e:
        logger.error(f"Error processing VTT file '{file_path}': {e}")
        raise HTTPException(status_code=400, detail=f"Invalid VTT format for file: {name}.vtt")

def validate_vtt_format(file_path: str):
    """Validates the basic format of a VTT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if not lines[0].startswith("WEBVTT"):
            raise ValueError("The VTT file must start with 'WEBVTT' header.")
    except Exception as e:
        raise ValueError(f"Error validating VTT format: {e}")

def inside(time_a, time_b):
    """Checks if time_b is inside time_a."""
    return time_a[0] <= (time_b[0] + time_b[1]) / 2 <= time_a[1]

def sync(texts_a, texts_b, times_a, times_b):
    """Synchronizes the subtitles based on their timings."""
    a = 0
    while a < len(texts_a):
        b = 0
        while b < len(texts_b):
            if times_b[b][0] > times_a[a][1]:
                break
            if inside(times_a[a], times_b[b]):
                if abs(times_a[a][0] - times_a[a][1]) > abs(times_b[b][0] - times_b[b][1]):
                    times_b[b] = times_a[a]
                else:
                    times_a[a] = times_b[b]
            b += 1
        a += 1

def make_time_float(time_str: str) -> float:
    """Converts a timestamp string to float seconds."""
    try:
        hours, minutes, seconds = time_str.split(":")
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    except ValueError as e:
        logger.error(f"Error converting time string '{time_str}': {e}")
        raise ValueError("Invalid time format")

def parse(sub_vtt: WebVTT, texts: List[str], times: List[List[float]]):
    """Parses VTT captions into text and timing lists."""
    for caption in sub_vtt:
        try:
            times.append([make_time_float(caption.start), make_time_float(caption.end)])
            texts.append(caption.raw_text)
        except ValueError as e:
            logger.error(f"Error parsing caption '{caption}': {e}")
            raise ValueError("Error parsing VTT caption")

def make_subtitle(texts: List[str], times: List[List[float]]) -> WebVTT:
    """Creates a WebVTT object from text and timing lists."""
    vtt = WebVTT()
    for i in range(len(times)):
        caption = Caption(
            str(datetime.timedelta(seconds=times[i][0])) + ".000",
            str(datetime.timedelta(seconds=times[i][1])) + ".000",
            texts[i],
        )
        vtt.captions.append(caption)
    return vtt

def synchronize_subtitles(first_sub: WebVTT, second_sub: WebVTT) -> List[WebVTT]:
    """Synchronizes two sets of subtitles."""
    texts_a, texts_b = [], []
    times_a, times_b = [], []
    parse(first_sub, texts_a, times_a)
    parse(second_sub, texts_b, times_b)
    sync(texts_a, texts_b, times_a, times_b)
    sync(texts_b, texts_a, times_b, times_a)
    return [make_subtitle(texts_a, times_a), make_subtitle(texts_b, times_b)]

def convert_vtt_to_str(vtt_sub: WebVTT) -> str:
    """Converts a WebVTT object into a string format."""
    output = ["WEBVTT"]
    counter = 1
    for caption in vtt_sub.captions:
        output.append("")
        output.append(f"{counter}\n{caption.start} --> {caption.end}")
        output.extend(caption.lines)
        counter += 1
    return "\n".join(output)

# For local testing: run 'uvicorn main:app --reload'
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
