from flask import Flask, render_template, request, jsonify, Response
import os
import time
import json
import threading
import uuid
from urllib.parse import quote
from .utils.logging_setup import setup_logging
from .utils.fetch_videos import fetch_url, find_video_sources
from .utils.download_videos import download_video, download_progresses

app = Flask(__name__)
logger = setup_logging()

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
    for url in selected_urls:
        download_id = f"download_{uuid.uuid4()}"
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
