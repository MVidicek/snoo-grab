import os
import requests
import subprocess
import praw
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QProgressBar, QFileDialog, QWidget
from PyQt6.QtCore import Qt, QThread, pyqtSignal

reddit = praw.Reddit()


def read_input_file(input_file):
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f.readlines()]
    return urls


def download_video(url, output_file, progress_callback=None):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    downloaded_size = 0
    with open(output_file, 'wb') as f:
        for data in response.iter_content(1024):
            f.write(data)
            downloaded_size += len(data)
            progress = (downloaded_size / total_size) * 100
            if progress_callback:
                progress_callback(
                    progress, f"Downloading {output_file}: {progress:.2f}%")


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


class DownloadThread(QThread):
    progress = pyqtSignal(int, str)

    def __init__(self, reddit_urls, output_directory, parent=None):
        QThread.__init__(self, parent)
        self.reddit_urls = reddit_urls
        self.output_directory = output_directory

    def run(self):
        def update_progress(progress, text):
            self.progress.emit(progress, text)

        for reddit_url in self.reddit_urls:
            update_progress(0, f"Processing {reddit_url}")
            video_url, audio_url = get_video_url(reddit_url)

            if video_url and audio_url:
                video_file = os.path.join(
                    self.output_directory, "temp_video.mp4")
                audio_file = os.path.join(
                    self.output_directory, "temp_audio.mp4")

                download_video(video_url, video_file, lambda p,
                               t: update_progress(p, t))
                download_video(audio_url, audio_file, lambda p,
                               t: update_progress(p, t))

                post_id = reddit_url.strip('/').split('/')[-1]
                output_filename = os.path.join(
                    self.output_directory, f"{post_id}.mp4")
                merge_video_audio(video_file, audio_file, output_filename)

                os.remove(video_file)
                os.remove(audio_file)

                update_progress(
                    100, f"Video downloaded with audio as {output_filename}")
            else:
                update_progress(
                    0, f"Unable to download video and audio for {reddit_url}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the layout and widgets
        layout = QVBoxLayout()

        url_label = QLabel("Enter URLs (one per line):")
        layout.addWidget(url_label)

        self.url_textbox = QTextEdit()
        layout.addWidget(self.url_textbox)

        output_folder_label = QLabel("Output Folder:")
        layout.addWidget(output_folder_label)

        hbox = QHBoxLayout()
        self.output_folder_entry = QLineEdit()
        hbox.addWidget(self.output_folder_entry)

        output_folder_button = QPushButton("Browse")
        output_folder_button.clicked.connect(self.browse_output_folder)
        hbox.addWidget(output_folder_button)

        layout.addLayout(hbox)

        self.start_download_button = QPushButton("Start Download")
        self.start_download_button.clicked.connect(self.start_download)
        layout.addWidget(self.start_download_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("SnooGrab")
        self.setGeometry(100, 100, 720, 480)

    def browse_output_folder(self):
        output_directory = QFileDialog.getExistingDirectory()
        self.output_folder_entry.setText(output_directory)

    def start_download(self):
        output_directory = self.output_folder_entry.text()
        reddit_urls = self.url_textbox.toPlainText().splitlines()

        self.download_thread = DownloadThread(reddit_urls, output_directory)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.start()

    def update_progress(self, progress, text):
        self.progress_bar.setValue(progress)
        self.progress_bar.setFormat(f"{text}")


if __name__ == "__main__":
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    app.exec()
