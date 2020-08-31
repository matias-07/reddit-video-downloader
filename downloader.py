import os
import subprocess
import requests
import sys

def get_or_raise(url):
    response = requests.get(
        url,
        headers={
            "User-Agent": "Reddit Video Downloader"
        }
    )
    response.raise_for_status()
    return response

def get_post_id(data):
    return data[0]["data"]["children"][0]["data"]["id"]

def get_video_url(data):
    return data[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]

def get_audio_urls(video_url):
    return [
        "/".join(video_url.split("/")[:-1]) + "/DASH_audio.mp4",
        "/".join(video_url.split("/")[:-1]) + "/audio"
    ]

def write_file(filename, content):
    with open(filename, "wb") as f:
        f.write(content)

def download_video_from_post(post_url):
    post = None
    print("Fetching post...")
    try:
        response = get_or_raise(post_url + ".json")
        post = response.json()
    except Exception as e:
        sys.exit("There was a problem fetching the post")
    post_id = get_post_id(post)
    video_url = None
    print("Obtaining video URL")
    try:
        video_url = get_video_url(post)
    except Exception as e:
        sys.exit("Couldn't get video URL from post")
    print("Obtaining audio URL...")
    audio_urls = get_audio_urls(video_url)
    video = None
    audio = None
    print("Obtaining audio...")
    try:
        for url in audio_urls:
            audio = get_or_raise(url)
            if audio:
                break
    except Exception as e:
        sys.exit("Couldn't get audio")
    print("Obtaining video...")
    try:
        video = get_or_raise(video_url)
    except Exception as e:
        sys.exit("Couldn't get video")
    print("Writing video to file...")
    try:
        write_file(f"{post_id}.mp4", video.content)
    except Exception as e:
        print(e)
        sys.exit("Couldn't write video file.")
    print("Writing audio to file...")
    try:
        write_file(f"{post_id}.mp3", audio.content)
    except Exception as e:
        sys.exit("Couldn't write audio file")
    print("Merging video and audio files...")
    try:
        subprocess.call(f"ffmpeg -i {post_id}.mp4 -i {post_id}.mp3 -shortest video_{post_id}.mp4".split())
    except Exception as e:
        sys.exit("There was a problem executing ffmpeg")
    print(f"Finished: output written to video_{post_id}.mp4")
    sys.exit(0)

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python downloader.py <post_url>")
    post_url = sys.argv[1]
    download_video_from_post(post_url)

if __name__ == "__main__":
    main()
