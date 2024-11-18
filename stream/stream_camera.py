import subprocess
from stream_setup import get_authenticated_service, create_scheduled_stream
import datetime

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
    youtube = get_authenticated_service()
    title = "Automated Live Stream"
    description = "Live stream from Python script"
    start_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    broadcast_id, stream_id, rtmp_url, stream_key = create_scheduled_stream(
        youtube, title, description, start_time
    )

    if rtmp_url and stream_key:
        print(f"RTMP URL: {rtmp_url}")
        print(f"Stream Key: {stream_key}")
        print("Starting live stream...")
        stream_from_camera(rtmp_url, stream_key)
