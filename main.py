import os
import uuid
import subprocess
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse

app = FastAPI()

# folder where videos will be saved
VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)


@app.get("/make-video")
def make_video(image_url: str, audio_url: str):
    # unique filename
    file_id = str(uuid.uuid4())
    output_path = os.path.join(VIDEO_DIR, f"{file_id}.mp4")

    # ffmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_url,
        "-i", audio_url,
        "-t", "20",  # fixed 20s
        "-vf", "scale=1280:-2,format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    subprocess.run(cmd, check=True)

    # instead of streaming, return the file link
    file_url = f"/videos/{file_id}.mp4"
    return JSONResponse({"video_url": file_url})


# route to serve video files
@app.get("/videos/{file_name}")
def get_video(file_name: str):
    file_path = os.path.join(VIDEO_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4")
    return JSONResponse({"error": "File not found"}, status_code=404)
