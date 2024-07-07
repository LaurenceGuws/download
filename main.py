import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, Response
import os
import time
import json
import threading
import uuid
from urllib.parse import quote
from logger import setup_logging

app = Flask(__name__)
logger = setup_logging()

download_progresses = {}

def fetch_url(web_url):
    logger.debug(f"Fetching URL: {web_url}")
    response = requests.get(web_url)
    if response.status_code != 200:
        logger.error(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None
    logger.info(f"HTTP request to {web_url} completed with status code {response.status_code}")
    return BeautifulSoup(response.content, 'html.parser')

def find_video_sources(soup):
    video_tags = soup.findAll('video')
    logger.info(f"Total {len(video_tags)} videos found")

    video_urls = []
    for video_tag in video_tags:
        video_url = extract_video_url(video_tag)
        if video_url:
            video_urls.append(video_url)
            logger.debug(f"Found video source URL: {video_url}")
        else:
            logger.warning("Video source not found in the video tag")

    return video_urls

def extract_video_url(video_tag):
    video_source = video_tag.find('source')
    if video_source and 'src' in video_source.attrs:
        return video_source['src']
    elif 'src' in video_tag.attrs:
        return video_tag['src']
    return video_tag.get('data-mp4')

def sanitize_filename(url):
    # Sanitize the URL to create a valid file name
    sanitized_url = quote(url, safe='')
    return sanitized_url

def download_video(url, referer, save_path, download_id, file_name=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': referer
    }
    
    # Use the provided file name or generate a unique one
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_videos', methods=['POST'])
def fetch_videos():
    web_url = request.form['url']
    
    soup = fetch_url(web_url)
    if not soup:
        return jsonify({'status': 'error', 'message': 'Failed to fetch the webpage'})

    video_urls = find_video_sources(soup)

    if not video_urls:
        return jsonify({'status': 'error', 'message': 'No videos found on the page'})

    return jsonify({'status': 'success', 'videos': video_urls})

@app.route('/download_videos', methods=['POST'])
def download_videos():
    data = request.json
    selected_urls = data['urls']
    save_path = data['save_path']
    web_url = data['web_url']
    file_name = data.get('file_name')

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    download_threads = []
    for i, url in enumerate(selected_urls):
        download_id = f"download_{i}"
        download_progresses[download_id] = 0
        thread = threading.Thread(target=download_video, args=(url, web_url, save_path, download_id, file_name))
        thread.start()
        download_threads.append(thread)

    return jsonify({'status': 'success', 'message': 'Downloads started', 'download_ids': list(download_progresses.keys())})

@app.route('/download_progress')
def download_progress():
    def generate():
        while True:
            yield f"data: {json.dumps(download_progresses)}\n\n"
            time.sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True)
