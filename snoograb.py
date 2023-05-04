import os
import re
import requests
import argparse
import subprocess
from praw import Reddit

# To get your own client ID and secret, create a Reddit app here:
# https://www.reddit.com/prefs/apps
# Then, replace the values below with your own.
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
USER_AGENT = 'SnooGrab:v1.0 (by u/Marcuskac)'

reddit = Reddit(client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET, user_agent=USER_AGENT)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Download videos from Reddit links.')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='The input file containing Reddit URLs, one per line.')
    parser.add_argument('-o', '--output', type=str, default='downloads',
                        help='The output directory for the downloaded videos.')

    return parser.parse_args()


def read_input_file(input_file):
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f.readlines()]
    return urls


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
    input_file = args.input
    output_directory = args.output

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    reddit_urls = read_input_file(input_file)

    for reddit_url in reddit_urls:
        print(f"Processing {reddit_url}")
        video_url, audio_url = get_video_url(reddit_url)

        if video_url and audio_url:
            video_file = os.path.join(output_directory, "temp_video.mp4")
            audio_file = os.path.join(output_directory, "temp_audio.mp4")

            download_video(video_url, video_file)
            download_video(audio_url, audio_file)

            post_id = reddit_url.strip('/').split('/')[-1]
            output_filename = os.path.join(output_directory, f"{post_id}.mp4")
            merge_video_audio(video_file, audio_file, output_filename)

            os.remove(video_file)
            os.remove(audio_file)

            print(f"Video downloaded with audio as {output_filename}")
        else:
            print(f"Unable to download video and audio for {reddit_url}")


if __name__ == "__main__":
    main()
