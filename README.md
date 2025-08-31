# TwitchClipDL

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub Repo Size](https://img.shields.io/github/repo-size/yourusername/TwitchClipDL)

**TwitchClipDL** is a Python tool to fetch and download clips from Twitch channels using the Twitch API and Selenium. It allows you to retrieve clip metadata in bulk and save clips locally with sanitized filenames.

---

## Features

- Retrieve Twitch clips from a broadcaster by username.
- Export clip data as a Pandas DataFrame.
- Download clips automatically in MP4 format.
- Handles filename sanitization to avoid invalid characters.
- Headless browser support via Selenium.

---

## Requirements

- Python 3.8+
- Twitch Developer account with **Client ID** and **Client Secret**.
- Chrome WebDriver installed and available in PATH.
- Python packages:
  ```bash
  pip install requests pandas python-dotenv selenium
  ```

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/TwitchClipDL.git
cd TwitchClipDL
```

2. Create a .env file in the project root:
```bash
CLIENT_ID=your_twitch_client_id
CLIENT_SECRET=your_twitch_client_secret
```

## Usage
```bash
from twitch_clip_dl import TwitchClipDL

# Initialize the downloader with the broadcaster's username
downloader = TwitchClipDL("twitch_username")

# Fetch clip metadata as a Pandas DataFrame
clips_df = downloader.get_data_from_twitch(pandas_df=True)

# Download all clips locally
downloader.get_clips(clips_df)
```
