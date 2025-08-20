import os
import uuid
import aiohttp
import asyncio
import subprocess
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

async def download_file(url: str, filename: str):
    """Download file asynchronously"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to download {url}")
            with open(filename, "wb") as f:
                f.write(await resp.read())

@app.get("/merge")
async def merge(image_url: str = Query(...), audio_url: str = Query(...)):
    """Merge image + audio into video and return file"""
    uid = str(uuid.uuid4())
    image_path = f"{TEMP_DIR}/{uid}_image.jpg"
    audio_path = f"{TEMP_DIR}/{uid}_audio.mp3"
    output_path = f"{TEMP_DIR}/{uid}_output.mp4"

    try:
        # Download files
        await asyncio.gather(
            download_file(image_url, image_path),
            download_file(audio_url, audio_path),
        )

        # Run ffmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", image_url,  # stream image directly from URL
            "-i", audio_url,  # stream audio directly from URL
            "-ss", "0", "-t", "20",  # limit to 20 sec
            "-vf", "scale=1280:-2,format=yuv420p",
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]

        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode != 0:
            raise Exception(process.stderr.decode())

        # Return video file as response
        return FileResponse(output_path, media_type="video/mp4", filename="output.mp4")

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    finally:
        # Cleanup temporary files after sending response
        for f in [image_path, audio_path, output_path]:
            if os.path.exists(f):
                os.remove(f)
