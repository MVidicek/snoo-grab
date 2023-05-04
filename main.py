import os
import re
import requests
from praw import Reddit

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
USER_AGENT = 'video_downloader:v1.0 (by u/Marcuskac)'  # e.g., 'video_downloader:v1.0 (by u/your_username)'

reddit = Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

def download_video(url, file_name):
    response = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(response.content)

def get_video_url(reddit_url):
    submission = reddit.submission(url=reddit_url)
    try:
        video_url = submission.media['reddit_video']['fallback_url']
        return video_url
    except KeyError:
        print("No video found in the provided link.")
        return None
      
def main():
    reddit_url = ''
    video_url = get_video_url(reddit_url)

    if video_url:
        file_name = "video.mp4"
        download_video(video_url, file_name)
        print(f"Video downloaded as {file_name}")


if __name__ == "__main__":
    main()