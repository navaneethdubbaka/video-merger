@app.get("/make-video")
def make_video(image_url: str, audio_url: str):
    output_file = f"{uuid.uuid4()}.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_url,
        "-i", audio_url,
        "-t", "20",
        "-vf", "scale=1280:-2,format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_file
    ]
    subprocess.run(cmd, check=True)

    return FileResponse(output_file, media_type="video/mp4", filename="output.mp4")
