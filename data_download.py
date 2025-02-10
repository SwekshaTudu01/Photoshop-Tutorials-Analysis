import yt_dlp
import os

# Replace with the URL of the YouTube playlist or single video you want to download
url = "https://www.youtube.com/playlist?list=PLIke35aX3K3kFGnGHN5LDwvZ_ZFP-y6Au"
# Define the folder where videos will be stored
output_folder = "downloaded_videos"

# Create the folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created folder: {output_folder}")

# yt-dlp options
ydl_opts = {
    'format': 'bestvideo[height<=1080]',  # Download only the best video up to 1080p
    'outtmpl': f'{output_folder}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',  
    # Save videos in 'downloaded_videos/playlist_name/' folder
    'postprocessors': [
        {
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Convert to MP4 format if not already
        }
    ],
    'quiet': False,  # Show download progress in the console
    
    'retries': 10,
    'socket_timeout': 60,  # seconds
    'retry_sleep_functions': {'http': lambda n: 5},
}


# Download the video or playlist
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("Download completed!")
