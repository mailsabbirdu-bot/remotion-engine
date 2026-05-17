import os
import subprocess

from moviepy.editor import VideoFileClip


def render_scene(video_path, scene, output_path):

    if not os.path.exists(video_path):
        print("❌ Missing video")
        return None

    duration = scene.get("duration", 5)

    audio_path = scene.get("audio_path")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    temp = "/content/temp_render.mp4"

    clip = VideoFileClip(video_path)

    if clip.duration < duration:
        clip = clip.loop(duration=duration)
    else:
        clip = clip.subclip(0, duration)

    clip = clip.resize(height=1080)

    clip.write_videofile(
        temp,
        fps=20,

codec="libx264",
preset="ultrafast",
threads=2,

        audio=False,
        logger=None
    )

    clip.close()

    cmd = [
        "ffmpeg",
        "-y",
        "-i", temp,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    subprocess.run(cmd)

    print("✅ Rendered:", output_path)
