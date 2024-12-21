import requests
import re
import time
import random
import os
from bs4 import BeautifulSoup
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed

NICKNAME = input("Nickname: ")
BASE_URL = "https://web.archive.org"
PLAYS_URL = "/web/20191210091719/https://plays.tv"
USER_URL = f"/u/{NICKNAME}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}

def log_error(message, video_url=None):
    if video_url:
        print(f"ERROR: {message} - {video_url}")
    else:
        print(f"ERROR: {message}")

def convert_date_format(input_date: str, input_format: str, output_format: str) -> str:
    try:
        parsed_date = datetime.strptime(input_date, input_format)
        return parsed_date.strftime(output_format)
    except ValueError:
        return input_date

def random_sleep(min_seconds=10, max_seconds=20):
    sleep_time = random.uniform(min_seconds, max_seconds)
    print(f"Waiting {sleep_time:.2f} seconds before the next request...")
    time.sleep(sleep_time)

def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filename):
        filename = f"{base} ({counter}){ext}"
        counter += 1
    return filename

def sanitize(name):
    return re.sub(r'[^\w\s.-]', '_', name).strip()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        log_error(f"Request failed: {e}", url)
        return None

def scrape(url):
    try:
        webarchive = fetch_url(url)
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to load page: {e}", url)
        return

    if webarchive is None:
        log_error("No content for URL. Skipping...", url)
        return

    profile = BeautifulSoup(webarchive.text, 'html.parser')
    profileVids = profile.find('div', id='B', class_='content-1')
    if not profileVids:
        log_error("Profile videos section not found. Skipping...", url)
        return

    for videos in profileVids.find_all('li', class_='video-item'):
        video_link = videos.find('a', class_='thumb-link', href=True)
        if not video_link:
            log_error("Video link not found in video-item.", url)
            continue

        random_sleep()
        video_url = re.sub(r'\?.*', '', video_link['href'])
        video_url = f"{BASE_URL}{video_url}"

        print(f"Fetching: {video_url}")
        webvideo = fetch_url(video_url)

        if webvideo is None:
            log_error("404 Not Archived", video_url)
            continue
        else:
            download_video(webvideo)

def download_video(page):
    if page is None:
        log_error("No page content to download. Skipping...")
        return

    current_format = "%b %d %Y"
    desired_format = "%Y-%m-%d"
    video = BeautifulSoup(page.text, 'html.parser')

    source_tag = video.find('source', attrs={'res': '720'})
    if not source_tag:
        print("No source with res='720' found. Falling back to any available <source> tag.")
        source_tag = video.find('source')
    
    if not source_tag:
        log_error("No valid <source> tag found. Skipping...")
        return

    title_tag = video.find('div', class_="video-title")
    date_tag = video.find('a', class_="created-time")

    if not date_tag or not title_tag:
        log_error("Missing required video details. Skipping...")
        return

    date = convert_date_format(date_tag.text.strip(), current_format, desired_format)
    title = title_tag.text.strip()
    safe_title = sanitize(title)
    safe_title = safe_title.encode('utf-8', 'ignore').decode('utf-8')
    filename = get_unique_filename(f"{date} - {safe_title}.mp4")

    src_link = source_tag['src']
    vidurl = f"https:{src_link}"

    print(f"Downloading video from: {vidurl}")

    try:
        response = requests.get(vidurl, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File saved as {filename}")
        else:
            log_error(f"Failed to fetch video. Status code: {response.status_code}", vidurl)
    except requests.exceptions.RequestException as e:
        log_error(f"Error downloading video: {e}", vidurl)


user_url = f"{BASE_URL}{PLAYS_URL}{USER_URL}"

scrape(user_url)