import os
import re
import requests
import argparse
import subprocess
from praw import Reddit

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
USER_AGENT = 'video_downloader:v1.0 (by u/Marcuskac)'  # e.g., 'video_downloader:v1.0 (by u/your_username)'

reddit = Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Download a video from a Reddit link.')
    parser.add_argument('-u', '--url', type=str, required=True, help='The Reddit URL containing the video.')
    parser.add_argument('-o', '--output', type=str, default='video.mp4', help='The output filename for the downloaded video.')

    return parser.parse_args()

def download_video(url, file_name):
    response = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(response.content)

def get_video_url(reddit_url):
    submission = reddit.submission(url=reddit_url)
    try:
        video_url = submission.media['reddit_video']['fallback_url']
        audio_url = video_url.split("DASH_")[0] + "DASH_audio.mp4"
        return video_url, audio_url
    except KeyError:
        print("No video found in the provided link.")
        return None, None
    
def merge_video_audio(video_file, audio_file, output_file):
    command = f'ffmpeg -y -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}'
    subprocess.call(command, shell=True)    
      
def main():
    args = parse_arguments()
    reddit_url = args.url
    output_filename = args.output

    video_url, audio_url = get_video_url(reddit_url)

    if video_url and audio_url:
        video_file = "temp_video.mp4"
        audio_file = "temp_audio.mp4"

        download_video(video_url, video_file)
        download_video(audio_url, audio_file)

        merge_video_audio(video_file, audio_file, output_filename)

        os.remove(video_file)
        os.remove(audio_file)

        print(f"Video downloaded with audio as {output_filename}")
    else:
        print("Unable to download video and audio.")


if __name__ == "__main__":
    main()