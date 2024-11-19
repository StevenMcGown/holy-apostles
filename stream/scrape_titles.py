from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import json

# Function to authenticate and create a YouTube API client
def get_youtube_client():
    """
    Authenticates the user and creates a YouTube API client.
    :return: Authenticated YouTube API client.
    """
    credentials = None
    # Check if token.pickle exists for saved credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials, prompt the user to log in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './credentials.json',  # Path to your credentials.json file
                ['https://www.googleapis.com/auth/youtube.readonly']
            )
            credentials = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    # Build the YouTube API client
    return build('youtube', 'v3', credentials=credentials)

# Replace with the actual channel ID of Holy Apostles Orthodox Church
channel_id = 'UCZEoPDY4U7yaaXlWMORbWYw'  # Correct channel ID

# Function to fetch stream data (titles and publication dates)
def fetch_stream_data(youtube, event_type=None):
    """
    Fetches stream data including title and published date.
    :param youtube: YouTube API client
    :param event_type: Type of event ('live', 'completed', or None)
    :return: List of dictionaries containing title and published date
    """
    data = []
    next_page_token = None

    while True:
        try:
            request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                maxResults=50,
                eventType=event_type,
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                title = item['snippet']['title']
                published_at = item['snippet']['publishedAt']
                data.append({'title': title, 'published_at': published_at})

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return data

# Main script
if __name__ == '__main__':
    # Get authenticated YouTube client
    youtube = get_youtube_client()

    # Fetch live and completed stream data
    live_stream_data = fetch_stream_data(youtube, 'live')
    completed_stream_data = fetch_stream_data(youtube, 'completed')

    # Combine all stream data
    all_stream_data = live_stream_data + completed_stream_data

    # Sort by upload date (published_at)
    sorted_stream_data = sorted(all_stream_data, key=lambda x: x['published_at'])

    # Save the sorted data to a JSON file
    with open('sorted_stream_data.json', 'w') as json_file:
        json.dump(sorted_stream_data, json_file, indent=4)

    print("Data successfully saved to sorted_stream_data.json")
