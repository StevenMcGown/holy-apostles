import subprocess
from stream_setup import get_authenticated_service, create_scheduled_stream
import datetime
import time
import os

def stream_from_camera(rtmp_url, stream_key):
    rtmp_address = f"{rtmp_url}/{stream_key}"
    command = [
        "ffmpeg",
        "-f", "v4l2",  # Linux webcam input
        "-i", "/dev/video0",  # Webcam device
        "-f", "alsa",  # Audio input
        "-i", "default",  # Default audio device
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", "2500k",
        "-maxrate", "2500k",
        "-bufsize", "5000k",
        "-pix_fmt", "yuv420p",
        "-g", "50",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-f", "flv",
        rtmp_address
    ]
    subprocess.run(command)

if __name__ == "__main__":
    # Authenticate and get the YouTube service
    youtube = get_authenticated_service()

    # Set stream details
    stream_title = "Sunday Service"
    stream_description = "Join us for the Sunday service live stream."
    start_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Scheduled 2 hours from now
    thumbnail_path = "icon.jpg"  # Path to the thumbnail image

    # Check if the thumbnail file exists
    if not os.path.exists(thumbnail_path):
        print(f"Thumbnail file '{thumbnail_path}' not found. Please ensure it exists.")
    else:
        # Schedule the stream and upload the thumbnail
        broadcast_id, stream_id, rtmp_url, stream_key = create_scheduled_stream(
            youtube,
            title=stream_title,
            description=stream_description,
            start_time=start_time,
            privacy="private",
            thumbnail_path=thumbnail_path
        )

        print(f"RTMP URL: {rtmp_url}")
        print(f"Stream Key: {stream_key}")
