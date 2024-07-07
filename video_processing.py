import requests
from bs4 import BeautifulSoup
import ffmpeg
import os
from logger import setup_logging

logger = setup_logging()

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

def scale_video(input_path, output_path, resolution="1280x720"):
    logger.info(f"Scaling video {input_path} to resolution {resolution}")
    ffmpeg.input(input_path).output(output_path, vf=f"scale={resolution}").overwrite_output().run()
    logger.info(f"Scaled video saved to {output_path}")

def concatenate_videos(video_paths, output_path):
    logger.info(f"Concatenating videos: {video_paths}")

    scaled_videos = []
    for i, video in enumerate(video_paths):
        scaled_video = video.replace(".mp4", f"_scaled_{i}.mp4")
        scale_video(video, scaled_video)
        scaled_videos.append(scaled_video)

    inputs = [ffmpeg.input(video) for video in scaled_videos]
    concat_filter = ffmpeg.concat(*inputs, v=1, a=1, unsafe=1).node
    v1 = concat_filter[0]
    a1 = concat_filter[1]
    ffmpeg.output(v1, a1, output_path).overwrite_output().run()
    logger.info(f"Videos concatenated into {output_path}")

    # Clean up scaled intermediate files
    for video in scaled_videos:
        os.remove(video)
