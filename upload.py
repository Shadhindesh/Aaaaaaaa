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
    video_path = data.get('Video Path')  # Default to aoi.mp4 if not found
    chat = 'alloneina'  # Replace with your channel/chat username

    # Split the video into 30-minute segments
    split_video_paths = split_video(video_path)

    # Print how many videos were created
    number_of_segments = len(split_video_paths)
    print(f"Number of split videos created: {number_of_segments}")

    # Create a dictionary to hold video links
    video_links = {}
    for index, segment_path in enumerate(split_video_paths, start=1):
        # Define the new video name
        new_video_name = f"{os.path.splitext(os.path.basename(video_path))[0]}_part_{index}.mp4"
        new_segment_path = os.path.join(os.path.dirname(segment_path), new_video_name)

        # Rename the segment file
        os.rename(segment_path, new_segment_path)

        # Upload each split video and get the public link
        video_link = await upload_and_get_link(chat, new_segment_path)
        if video_link:
            video_links[str(index)] = video_link  # Use string index for JSON keys

    # Print the video links
    print("Uploaded video links:", video_links)

# Run the main async function
with client:
    client.loop.run_until_complete(main())