import feedparser
import requests
import os
from urllib.parse import urlparse
from pathlib import Path

def download_podcast(rss_url, output_dir='downloads'):
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)
    
    print(f"Podcast: {feed.feed.title}")
    print(f"Found {len(feed.entries)} episodes")
    
    for entry in feed.entries:
        # Find the audio file URL in the enclosures
        for enclosure in entry.enclosures:
            if 'audio' in enclosure.type:
                audio_url = enclosure.href
                
                # Create filename from the URL
                filename = os.path.join(output_dir, os.path.basename(urlparse(audio_url).path))
                
                # Skip if file already exists
                if os.path.exists(filename):
                    print(f"Skipping {filename} - already exists")
                    continue
                
                print(f"Downloading: {entry.title}")
                
                try:
                    # Download the file
                    response = requests.get(audio_url, stream=True)
                    response.raise_for_status()
                    
                    # Save the file
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"Saved to: {filename}")
                except Exception as e:
                    print(f"Error downloading {entry.title}: {str(e)}")

if __name__ == "__main__":
    rss_url = input("Enter the podcast RSS feed URL: ")
    download_podcast(rss_url) 