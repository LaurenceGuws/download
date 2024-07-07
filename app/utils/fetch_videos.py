import requests
from bs4 import BeautifulSoup
from .logging_setup import setup_logging

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
