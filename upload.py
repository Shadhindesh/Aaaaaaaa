import os
import json
import requests
import subprocess
from telethon import TelegramClient

# Initialize the client with your API ID and API hash
api_id = '25888737'
api_hash = '9c935d3704bbe290f533d6b632572ecf'
phone_number = '+8801842344207'  # Your phone number
FLASK_API_URL = 'https://linkcollector.onrender.com/upload-json'

def load_data():
    data = {}
    with open('data.txt') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            data[key.strip()] = value.strip()
    return data

client = TelegramClient('session_name', api_id, api_hash)

async def upload_and_get_link(chat, video_path):
    await client.start(phone_number)

    # Upload the video file
    message = await client.send_file(chat, video_path)

    # Retrieve the message ID to generate a link
    if message.is_channel:
        # Get the public link for the uploaded video in a channel
        link = f"https://t.me/{chat}/{message.id}"
        print("Public link for video:", link)
        return link
    else:
        print("Uploaded to a private chat, no public link available.")
        return None

def append_to_json(data, all_data):
    all_data.append(data)
    return all_data

# Send the JSON data to the Flask API
def send_json_to_flask_api(data):
    json_data = {
        'file': ('data.json', json.dumps(data), 'application/json')
    }
    response = requests.post(FLASK_API_URL, files=json_data)

    if response.ok:
        print("JSON data uploaded to Flask API successfully!")
    else:
        print("Error uploading JSON to Flask API:", response.text)

def split_video(video_path, segment_length=1800):
    # Create an output directory for the split videos
    output_dir = "split_videos"
    os.makedirs(output_dir, exist_ok=True)

    # Construct the ffmpeg command to split the video
    output_pattern = os.path.join(output_dir, "part_%03d.mp4")
    command = [
        'ffmpeg',
        '-i', video_path,
        '-c', 'copy',  # Copy the video without re-encoding
        '-map', '0',
        '-segment_time', str(segment_length),  # Split every segment_length seconds
        '-f', 'segment',
        output_pattern
    ]

    # Execute the command
    subprocess.run(command)

    # Return the list of split video paths
    return [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.mp4')]

async def main():
    # Load data from data.txt
    data = load_data()

    # Assign data to respective variables
    video_path = data.get('Video Path')
    subject = data.get('Subject')
    chapter = data.get('Chapter')
    class_level = data.get('Class')
    chat = 'alloneina'  # Replace with your channel/chat username

    # Split the video into 30-minute segments
    split_video_paths = split_video(video_path)

    # Create a dictionary to hold video links
    video_links = {}
    for index, segment_path in enumerate(split_video_paths, start=1):
        # Upload each split video and get the public link
        video_link = await upload_and_get_link(chat, segment_path)
        if video_link:
            video_links[str(index)] = video_link  # Use string index for JSON keys

    # Create the JSON data
    json_data = {
        'name': os.path.basename(video_path),
        'class': class_level,
        'chapter': chapter,
        'subject': subject,
        'video_links': video_links,
        'number_of_segments': len(video_links)  # Number of segments created
    }

    # Load existing JSON data from links.json
    existing_json = {"data": []}
    if os.path.exists("links.json"):
        with open("links.json", "r") as f:
            existing_json = json.load(f)

    # Append new data to existing JSON
    updated_json = append_to_json(json_data, existing_json['data'])

    # Save updated JSON to links.json
    with open("links.json", "w") as f:
        json.dump({"data": updated_json}, f, indent=4)
    print("Data saved to links.json")

    # Send the data to the Flask API
    send_json_to_flask_api(updated_json)

# Run the main async function
with client:
    client.loop.run_until_complete(main())
                                               
