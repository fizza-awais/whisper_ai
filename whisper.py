import requests
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("API_TOKEN")

def read_file(filename, chunk_size=5242880):
    # Open the file in binary mode for reading
    with open(filename, 'rb') as _file:
        while True:
            # Read a chunk of data from the file
            data = _file.read(chunk_size)
            # If there's no more data, stop reading
            if not data:
                break
            # Yield the data as a generator
            yield data

def upload_file(api_token, path):
    """
    Upload a file to the AssemblyAI API.

    Args:
        api_token (str): Your API token for AssemblyAI.
        path (str): Path to the local file.

    Returns:
        str: The upload URL.
    """
    print(f"Uploading file: {path}")

    # Set the headers for the request, including the API token
    headers = {'authorization': api_token}
    
    # Send a POST request to the API to upload the file, passing in the headers
    # and the file data
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             data=read_file(path))

    # If the response is successful, return the upload URL
    if response.status_code == 200:
        return response.json()["upload_url"]
    # If the response is not successful, print the error message and return
    # None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def create_transcript(api_token, audio_url):
    """
    Create a transcript using AssemblyAI API.

    Args:
        api_token (str): Your API token for AssemblyAI.
        audio_url (str): URL of the audio file to be transcribed.

    Returns:
        dict: Completed transcript object.
    """
    print("Transcribing audio... This might take a moment.")

    # Set the API endpoint for creating a new transcript
    url = "https://api.assemblyai.com/v2/transcript"

    # Set the headers for the request, including the API token and content type
    headers = {
        "authorization": api_token,
        "content-type": "application/json"
    }

    # Set the data for the request, including the URL of the audio file to be
    # transcribed
    data = {
        "audio_url": audio_url
    }

    # Send a POST request to the API to create a new transcript, passing in the
    # headers and data
    response = requests.post(url, json=data, headers=headers)

    # Get the transcript ID from the response JSON data
    transcript_id = response.json()['id']
    detected_language = response.json()['language_code']
    print("Detected Language",detected_language)


    # Set the polling endpoint URL by appending the transcript ID to the API endpoint
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

    # Keep polling the API until the transcription is complete
    while True:
        # Send a GET request to the polling endpoint, passing in the headers
        transcription_result = requests.get(polling_endpoint, headers=headers).json()

        # If the status of the transcription is 'completed', exit the loop
        if transcription_result['status'] == 'completed':
            break

        # If the status of the transcription is 'error', raise a runtime error with
        # the error message
        elif transcription_result['status'] == 'error':
            raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

        # If the status of the transcription is not 'completed' or 'error', wait for
        # 3 seconds and poll again
        else:
            time.sleep(3)

    return transcription_result

# Your API token is already set in this variable
# your_api_token = "11664d773881407bbe3bc05c7a3ae35e"

# -----------------------------------------------------------------------------
# Update the file path here, pointing to a local audio or video file.
# If you don't have one, download a sample file: https://storage.googleapis.com/aai-web-samples/espn-bears.m4a
# You may also remove the upload step and update the 'audio_url' parameter in the
# 'create_transcript' function to point to a remote audio or video file.
# -----------------------------------------------------------------------------
filename = "lisan_zuban.mp3"

# Upload the file to AssemblyAI and get the upload URL
upload_url = upload_file(api_key, filename)

# Transcribe the audio file using the upload URL
transcript = create_transcript(api_key, upload_url)

# Print the completed transcript object
print(transcript['text'])
print(transcript)
with open(f"{filename}.txt", "w", encoding="utf-8") as file:
    # Write the data to the file
    file.write(transcript['text'])