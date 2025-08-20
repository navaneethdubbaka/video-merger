import os
import uuid
import subprocess
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from supabase import create_client, Client

app = FastAPI()

# --- Direct Supabase Credentials (replace with yours) ---
SUPABASE_URL = "https://xrigzgfmdqhbpkvxkbhs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhyaWd6Z2ZtZHFoYnBrdnhrYmhzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQyMDIxNSwiZXhwIjoyMDY2OTk2MjE1fQ.xhJjshMPsNpg1X86mn04t34ZPU-KxmVdE5xF7_wH1e8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/make-video")
def make_video(image_url: str, audio_url: str):
    # Unique video file name
    output_filename = f"{uuid.uuid4()}.mp4"

    # FFmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_url,
        "-i", audio_url,
        "-t", "20",
        "-vf", "scale=1280:-2,format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        output_filename
    ]

    # Run ffmpeg
    subprocess.run(cmd, check=True)

    # Upload to Supabase Storage
    with open(output_filename, "rb") as f:
        supabase.storage.from_("videos").upload(output_filename, f)

    # Make public URL
    public_url = supabase.storage.from_("videos").get_public_url(output_filename)

    # Delete local file after upload
    os.remove(output_filename)

    return JSONResponse({"url": public_url})
