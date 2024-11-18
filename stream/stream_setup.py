import datetime
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# Path to your client secret JSON file
CLIENT_SECRET_FILE = "./credentials.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        credentials = flow.run_local_server(port=8080)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return build("youtube", "v3", credentials=credentials)

def get_rtmp_url(youtube, stream_id):
    try:
        response = youtube.liveStreams().list(part="cdn", id=stream_id).execute()
        if "items" in response and len(response["items"]) > 0:
            ingestion_info = response["items"][0]["cdn"]["ingestionInfo"]
            return ingestion_info["ingestionAddress"], ingestion_info["streamName"]
        else:
            print("Stream not found.")
            return None, None
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None, None

def create_scheduled_stream(youtube, title, description, start_time, privacy="private", made_for_kids=False, thumbnail_path=None):
    try:
        # Create the live broadcast
        broadcast = youtube.liveBroadcasts().insert(
            part="snippet,contentDetails,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "scheduledStartTime": start_time.isoformat() + "Z"
                },
                "status": {
                    "privacyStatus": privacy,
                    "selfDeclaredMadeForKids": made_for_kids
                },
                "contentDetails": {"enableAutoStart": True, "enableAutoStop": True}
            }
        ).execute()

        # Create the live stream
        stream = youtube.liveStreams().insert(
            part="snippet,cdn,contentDetails",
            body={
                "snippet": {"title": title + " Stream"},
                "cdn": {"frameRate": "30fps", "resolution": "720p", "ingestionType": "rtmp"},
                "contentDetails": {"isReusable": True}
            }
        ).execute()

        # Bind the stream to the broadcast
        youtube.liveBroadcasts().bind(
            part="id,contentDetails",
            id=broadcast["id"],
            streamId=stream["id"]
        ).execute()

        # Set the thumbnail if provided
        if thumbnail_path:
            set_thumbnail(youtube, broadcast["id"], thumbnail_path)

        # Get RTMP URL and stream key
        rtmp_url, stream_key = get_rtmp_url(youtube, stream["id"])

        return broadcast["id"], stream["id"], rtmp_url, stream_key
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None, None, None, None

def set_thumbnail(youtube, broadcast_id, thumbnail_path):
    try:
        if not os.path.exists(thumbnail_path):
            print(f"Thumbnail file '{thumbnail_path}' not found.")
            return False

        youtube.thumbnails().set(
            videoId=broadcast_id,
            media_body=thumbnail_path
        ).execute()

        print(f"Thumbnail uploaded successfully for broadcast ID: {broadcast_id}")
        return True
    except HttpError as e:
        print(f"An error occurred while setting the thumbnail: {e}")
        return False

def set_thumbnail(youtube, broadcast_id, thumbnail_path):
    try:
        if not os.path.exists(thumbnail_path):
            print(f"Thumbnail file '{thumbnail_path}' not found.")
            return False

        with open(thumbnail_path, "rb") as file:
            youtube.thumbnails().set(
                videoId=broadcast_id,
                media_body=thumbnail_path
            ).execute()

        print(f"Thumbnail uploaded successfully for broadcast ID: {broadcast_id}")
        return True
    except HttpError as e:
        print(f"An error occurred while setting the thumbnail: {e}")
        return False
