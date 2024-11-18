import boto3
import time
import uuid
import sys

# Initialize AWS Transcribe client
transcribe = boto3.client('transcribe')

# Define the S3 URI of your MP3 file
s3_uri = 's3://holy-apostles/recording.mp3'

# Ensure the job name is unique
job_name = f"transcription_job_{uuid.uuid4()}"

# Start transcription job with speaker diarization enabled
try:
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat='mp3',
        LanguageCode='en-US',  # Change this based on your audio language
        Settings={
            'ShowSpeakerLabels': True,
            'MaxSpeakerLabels': 4  # Set the max number of speakers to identify
        }
    )
except Exception as e:
    print(f"Error starting transcription job: {e}")
    sys.exit(1)

# Check the job status and retrieve the transcript once complete
while True:
    result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    status = result['TranscriptionJob']['TranscriptionJobStatus']
    print(f"Current status: {status}")
    if status in ['COMPLETED', 'FAILED']:
        break
    time.sleep(10)

# If the job was successful, download the transcript
if status == 'COMPLETED':
    transcript_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
    print(f"Transcription completed. Download the transcript here: {,  }")
elif status == 'FAILED':
    failure_reason = result['TranscriptionJob']['FailureReason']
    print(f"Transcription job failed: {failure_reason}")
