import os
import requests
import subprocess
import tkinter as tk
from tqdm import tqdm
from praw import Reddit
from tkinter import filedialog

# To get your own client ID and secret, create a Reddit app here:
# https://www.reddit.com/prefs/apps
# Then, replace the values below with your own.
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
USER_AGENT = 'SnooGrab:v1.0 (by u/Marcuskac)'

reddit = Reddit(client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET, user_agent=USER_AGENT)


def browse_input_file():
    input_file = filedialog.askopenfilename(
        filetypes=[('Text Files', '*.txt')])
    input_file_var.set(input_file)


def browse_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_var.set(output_folder)


def read_input_file(input_file):
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f.readlines()]
    return urls


def download_video(url, output_file):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(output_file, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_file, ncols=100) as progress_bar:
            for data in response.iter_content(1024):
                f.write(data)
                progress_bar.update(len(data))


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
    command = [
        'ffmpeg',
        '-i', video_file,
        '-i', audio_file,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-loglevel', 'error',
        output_file
    ]
    subprocess.run(command, check=True)


def start_download():
    input_file = input_file_var.get()
    output_directory = output_folder_var.get()

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


# Create the main window
root = tk.Tk()
root.title("SnooGrab")

# Create and add input file widgets
input_file_label = tk.Label(root, text="Input File:")
input_file_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 0), sticky="w")

input_file_var = tk.StringVar()
input_file_entry = tk.Entry(root, textvariable=input_file_var, width=40)
input_file_entry.grid(row=0, column=1, padx=(0, 5), pady=(10, 0))

input_file_button = tk.Button(root, text="Browse", command=browse_input_file)
input_file_button.grid(row=0, column=2, padx=(0, 10), pady=(10, 0))

# Create and add output folder widgets
output_folder_label = tk.Label(root, text="Output Folder:")
output_folder_label.grid(row=1, column=0, padx=(10, 5),
                         pady=(10, 0), sticky="w")

output_folder_var = tk.StringVar()
output_folder_entry = tk.Entry(root, textvariable=output_folder_var, width=40)
output_folder_entry.grid(row=1, column=1, padx=(0, 5), pady=(10, 0))

output_folder_button = tk.Button(
    root, text="Browse", command=browse_output_folder)
output_folder_button.grid(row=1, column=2, padx=(0, 10), pady=(10, 0))

# Create and add start download button
start_download_button = tk.Button(
    root, text="Start Download", command=start_download)
start_download_button.grid(
    row=2, column=0, columnspan=3, padx=10, pady=(10, 10))

# Start the application
root.mainloop()
