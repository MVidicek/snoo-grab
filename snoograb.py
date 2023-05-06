import os
import requests
import subprocess
import praw
import tkinter as tk
from tqdm import tqdm
from praw import Reddit
from tkinter import filedialog

reddit = praw.Reddit()


def browse_output_folder():
    output_directory = filedialog.askdirectory()
    output_directory_var.set(output_directory)


def get_urls_from_textbox():
    urls = url_textbox.get("1.0", tk.END).splitlines()
    return [url for url in urls if url.strip()]


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
    output_directory = output_directory_var.get()

    reddit_urls = get_urls_from_textbox()

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

# Create and add URL entry textbox
url_label = tk.Label(root, text="Enter URLs (one per line):")
url_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 0), sticky="w")

url_textbox = tk.Text(root, wrap=tk.WORD, width=50, height=10)
url_textbox.grid(row=0, column=1, padx=(0, 5), pady=(10, 0), rowspan=2)

url_textbox_scrollbar = tk.Scrollbar(root, command=url_textbox.yview)
url_textbox_scrollbar.grid(row=0, column=2, padx=(
    0, 10), pady=(10, 0), rowspan=2, sticky="ns")
url_textbox.config(yscrollcommand=url_textbox_scrollbar.set)

# Create and add output folder widgets
output_folder_label = tk.Label(root, text="Output Folder:")
output_folder_label.grid(row=2, column=0, padx=(10, 5),
                         pady=(10, 0), sticky="w")

output_directory_var = tk.StringVar()
output_folder_entry = tk.Entry(
    root, textvariable=output_directory_var, width=40)
output_folder_entry.grid(row=2, column=1, padx=(0, 5), pady=(10, 0))

output_folder_button = tk.Button(
    root, text="Browse", command=browse_output_folder)
output_folder_button.grid(row=2, column=2, padx=(0, 10), pady=(10, 0))


# Create and add start download button
start_download_button = tk.Button(
    root, text="Start Download", command=start_download)
start_download_button.grid(
    row=3, column=0, columnspan=3, padx=10, pady=(10, 10))

# Start the application
root.mainloop()
