import os
import uuid
import aiohttp
import asyncio
import subprocess
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

app = FastAPI()

@app.get("/make-video")
def make_video(image_url: str, audio_url: str):
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_url,
        "-i", audio_url,
        "-t", "20",  # <-- fixed 20s duration
        "-vf", "scale=1280:-2,format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        "-f", "mp4", "pipe:1"
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return StreamingResponse(process.stdout, media_type="video/mp4")

