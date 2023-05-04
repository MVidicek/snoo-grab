# SnooGrab

SnooGrab is a simple command-line tool that allows you to download videos from Reddit, including those hosted on v.redd.it.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
  - [Cloning the Repository](#cloning-the-repository)
  - [Setting Up Reddit API Credentials](#setting-up-reddit-api-credentials)
  - [Installing FFmpeg](#installing-ffmpeg)
  - [Installing Python Dependencies](#installing-python-dependencies)
- [Usage](#usage)
- [License](#license)

## Requirements

- Python 3.6 or higher
- Reddit API credentials (client ID and client secret)
- FFmpeg

## Installation

### Cloning the Repository

Clone the repository to your local machine by running the following command:

```bash
git clone https://github.com/yourusername/redvid-dl.git
```
Alternatively, you can download the repository as a ZIP file and extract it.

### Setting Up Reddit API Credentials

1. Log in to your Reddit account and go to https://www.reddit.com/prefs/apps.
2. Click on "Create App" or "Create Another App".
3. Fill in the required fields:
   - Name: Choose a name for your app (e.g., SnooGrab).
   - App type: Select "script".
   - Description: Add a short description (optional).
   - About URL: Leave it blank or add your GitHub repository URL.
   - Redirect URI: Enter `http://localhost:8080` (required for script type).
4. Click on "Create app" at the bottom of the form.
5. Note down the client ID (found under the app name) and the client secret.

Update the `CLIENT_ID`, `CLIENT_SECRET`, and `USER_AGENT` variables in the script with the corresponding values from the Reddit app you created:

```python
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
USER_AGENT = 'your_user_agent'  # e.g., 'SnooGrab:v1.0 (by u/your_username)'
```

### Installing FFmpeg

Here's a step-by-step guide on installing FFmpeg and adding it to your PATH variables on different operating systems:

**Windows:**

1. Download the Windows build of FFmpeg from the official website: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z (This is a trusted third-party website that hosts FFmpeg builds for Windows, as recommended on the official FFmpeg website)

2. Extract the downloaded .7z archive using a tool like 7-Zip (https://www.7-zip.org/).

3. Move the extracted "ffmpeg-*-full_build" folder to a permanent location, such as "C:\Program Files\ffmpeg" or "C:\ffmpeg".

4. Add the "bin" folder inside the "ffmpeg-*-full_build" folder to your system's PATH variable:

   a. Right-click on "This PC" or "My Computer" and click on "Properties".

   b. Click on "Advanced system settings" on the left side.

   c. Click on the "Environment Variables" button near the bottom of the "System Properties" window.

   d. In the "System variables" section, find the variable named "Path" and click on "Edit".

   e. Click on "New" and add the full path to the "bin" folder, such as "C:\Program Files\ffmpeg\bin" or "C:\ffmpeg\bin".

   f. Click on "OK" to close the "Edit environment variable" window, then click on "OK" again to close the "Environment Variables" window, and finally click on "OK" to close the "System Properties" window.

5. Restart any open command prompt or terminal windows to apply the changes.

**macOS:**

1. Install Homebrew if you don't have it installed already. Homebrew is a package manager for macOS. You can install it by following the instructions on the official website: https://brew.sh/

2. Open Terminal and run the following command to install FFmpeg:

```bash
brew install ffmpeg
```

Homebrew will automatically install FFmpeg and add it to your PATH variable.

**Linux (Debian-based distributions like Ubuntu):**

1. Open Terminal and run the following commands to install FFmpeg:

```bash
sudo apt update
sudo apt install ffmpeg
```

The package manager will install FFmpeg and add it to your PATH variable.

After installing FFmpeg, you can verify that it has been added to your PATH by running the following command in your command prompt, terminal, or shell:

```bash
ffmpeg -version
```

This command should display the FFmpeg version information if the installation and PATH configuration were successful.

### Installing Python Dependencies
Navigate to the cloned or extracted repository folder in your terminal or command prompt, and run the following command to install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage
After completing the installation, you can use SnooGrab as follows:

```bash
python redvid-dl.py --url https://www.reddit.com/r/subreddit/post/ --output downloaded_video.mp4
```
Replace the example Reddit URL with the URL of the video you want to download, and change the output filename if desired.

## License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.
