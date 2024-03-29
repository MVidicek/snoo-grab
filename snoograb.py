import configparser
import os
import requests
import subprocess
import praw
from styles import light, dark
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QProgressBar, QFileDialog, QWidget, QMessageBox, QDialog, QDialogButtonBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QGuiApplication


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


def get_video_url(reddit, reddit_url):
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
        '-y',
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

    def __init__(self, reddit, reddit_urls, output_directory, parent=None):
        QThread.__init__(self, parent)
        self.reddit = reddit
        self.reddit_urls = reddit_urls
        self.output_directory = output_directory

    def run(self):
        def update_progress(progress, text):
            self.progress.emit(progress, text)

        # Each video has a video file and an audio file
        total_files = len(self.reddit_urls) * 2
        completed_files = 0

        for reddit_url in self.reddit_urls:
            update_progress(0, f"Processing {reddit_url}")
            video_url, audio_url = get_video_url(self.reddit, reddit_url)

            if video_url and audio_url:
                video_file = os.path.join(
                    self.output_directory, "temp_video.mp4")
                audio_file = os.path.join(
                    self.output_directory, "temp_audio.mp4")

                download_video(video_url, video_file, lambda p,
                               t: update_progress((completed_files + p/100) / total_files * 100, t))
                completed_files += 1

                download_video(audio_url, audio_file, lambda p,
                               t: update_progress((completed_files + p/100) / total_files * 100, t))
                completed_files += 1

                post_id = reddit_url.strip('/').split('/')[-1]
                output_filename = os.path.join(
                    self.output_directory, f"{post_id}.mp4")
                merge_video_audio(video_file, audio_file, output_filename)

                os.remove(video_file)
                os.remove(audio_file)

            else:
                update_progress(
                    0, f"Unable to download video and audio for {reddit_url}")

        update_progress(
            100, f"All videos downloaded successfully.")


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.setGeometry(0, 0, 320, 200)

        self.setWindowTitle("Settings")

        # Create input fields
        self.client_id_input = QLineEdit()
        self.client_secret_input = QLineEdit()
        self.password_input = QLineEdit()
        self.username_input = QLineEdit()

        layout.addWidget(QLabel("Client ID"))
        layout.addWidget(self.client_id_input)

        layout.addWidget(QLabel("Client Secret"))
        layout.addWidget(self.client_secret_input)

        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password_input)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)

        # Create OK and Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.confirm)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.center()

        self.load_settings_from_praw_ini()

    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def get_values(self):
        return {
            'client_id': self.client_id_input.text(),
            'client_secret': self.client_secret_input.text(),
            'password': self.password_input.text(),
            'username': self.username_input.text()
        }

    def confirm(self):
        self.praw_settings = {
            'client_id': self.client_id_input.text(),
            'client_secret': self.client_secret_input.text(),
            'password': self.password_input.text(),
            'username': self.username_input.text(),
            'user_agent': f'Windows:SnooGrab:v0.0.2 (by /u/{self.username_input.text()})'
        }
        self.save_settings_to_praw_ini()
        self.accept()

    def save_settings_to_praw_ini(self):
        config = configparser.ConfigParser()
        config['DEFAULT'] = self.praw_settings

        with open('praw.ini', 'w') as configfile:
            config.write(configfile)

    def load_settings_from_praw_ini(self):
        config = configparser.ConfigParser()
        config.read('praw.ini')

        if 'DEFAULT' in config:
            self.praw_settings = dict(config['DEFAULT'])
        else:
            self.praw_settings = {
                'client_id': '',
                'client_secret': '',
                'password': '',
                'username': '',
                'user_agent': 'Windows:SnooGrab:v0.0.1 (by /u/Marcuskac)'
            }

        self.client_id_input.setText(self.praw_settings['client_id'])
        self.client_secret_input.setText(self.praw_settings['client_secret'])
        self.password_input.setText(self.praw_settings['password'])
        self.username_input.setText(self.praw_settings['username'])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

       # Create the layout and widgets
        layout = QVBoxLayout()
        # Set margins (left, top, right, bottom)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)  # Set spacing between widgets

        # Add a button to switch themes
        self.theme_button = QPushButton("Switch theme")
        self.theme_button.clicked.connect(self.switch_theme)
        layout.addWidget(self.theme_button)

        # Initialize to the light theme
        self.theme = "light"
        self.setStyleSheet(light.stylesheet)

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

        progress_layout = QVBoxLayout()  # Create a new layout for the progress bar and text
        self.progress_bar = QProgressBar()
        # The text will now be displayed in a separate QLabel
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.progress_text = QLabel()  # This QLabel will display the progress text
        progress_layout.addWidget(self.progress_text)

        # Add the progress layout to the main layout
        layout.addLayout(progress_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("SnooGrab")
        self.setGeometry(0, 0, 720, 480)
        self.center()

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        layout.addWidget(self.settings_button)

        self.praw_settings = {
            'user_agent': 'Windows:SnooGrab:v0.0.2 (by /u/)'
        }

    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def open_settings(self):
        dialog = SettingsDialog(self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self.praw_settings = dialog.get_values()

    def switch_theme(self):
        if self.theme == "light":
            self.setStyleSheet(dark.stylesheet)
            self.theme = "dark"
        else:
            self.setStyleSheet(light.stylesheet)
            self.theme = "light"

    def update_progress(self, progress, text):
        self.progress_bar.setValue(progress)
        self.progress_text.setText(f"{text}")

    def download_finished(self):
        QMessageBox.information(self, "Download Complete",
                                "All videos have been downloaded.")

    def browse_output_folder(self):
        output_directory = QFileDialog.getExistingDirectory()
        self.output_folder_entry.setText(output_directory)

    def enable_download_button(self):
        self.start_download_button.setDisabled(False)

    def start_download(self):

        reddit = praw.Reddit(
            client_id=self.praw_settings.get('client_id', ''),
            client_secret=self.praw_settings.get('client_secret', ''),
            password=self.praw_settings.get('password', ''),
            username=self.praw_settings.get('username', ''),
            user_agent=self.praw_settings.get(
                'user_agent', '') + self.praw_settings.get('username', '')
        )

        output_directory = self.output_folder_entry.text()
        reddit_urls = self.url_textbox.toPlainText().splitlines()

        # Check if any file already exists
        for reddit_url in reddit_urls:
            post_id = reddit_url.strip('/').split('/')[-1]
            output_filename = os.path.join(output_directory, f"{post_id}.mp4")
            if os.path.exists(output_filename):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)  # Corrected this line
                msg.setText("File already exists")
                msg.setInformativeText(
                    f"Do you want to overwrite {output_filename}?")
                msg.setWindowTitle("File Overwrite Confirmation")
                # Corrected this line
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

                returnValue = msg.exec()
                if returnValue == QMessageBox.StandardButton.Cancel:  # Corrected this line
                    return

        self.start_download_button.setDisabled(True)
        self.download_thread = DownloadThread(
            reddit, reddit_urls, output_directory)
        self.download_thread.finished.connect(self.enable_download_button)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.start()


if __name__ == "__main__":
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    app.exec()
