import requests
import os
import uuid
from urllib.parse import quote
from .logging_setup import setup_logging

logger = setup_logging()
download_progresses = {}

def sanitize_filename(url):
    sanitized_url = quote(url, safe='')
    return sanitized_url

def download_video(url, referer, save_path, download_id, file_name=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': referer
    }
    
    if not file_name:
        sanitized_url = sanitize_filename(url)
        unique_id = uuid.uuid4()
        file_name = f"{sanitized_url}_{unique_id}.mp4"
    
    local_filename = os.path.join(save_path, file_name)

    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0

        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                    download_progresses[download_id] = progress

    logger.info(f"Downloaded {url} to {local_filename}")
    return local_filename
