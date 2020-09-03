import requests
import subprocess
import sys

def write_file(filename, content):
    with open(filename, "wb") as file:
        file.write(content)

def get_response(url):
    response = requests.get(
        url,
        headers={
            "User-Agent": "Reddit Video Downloader"
        }
    )
    try:
        response.raise_for_status()
    except requests.HTTPError:
        return None
    return response

def get_json(url):
    response = get_response(url)
    if not response:
        return None
    try:
        return response.json()
    except ValueError:
        return None

def get_args():
    if len(sys.argv) != 2:
        sys.exit("Usage: python downloader.py <post_url>")
    return sys.argv[1:]

def get_post_data(post_url):
    return get_json(post_url) or sys.exit("Couldn't get post")

def get_post_id(post_data):
    try:
        return post_data[0]["data"]["children"][0]["data"]["id"]
    except (IndexError, KeyError):
        sys.exit("Couldn't get post id")

def get_video(post_data):
    url = None
    try:
        url = post_data[0]["data"]["children"]\
            [0]["data"]["secure_media"]\
            ["reddit_video"]["fallback_url"]
    except (IndexError, KeyError):
        sys.exit("Couldn't get video URL")
    response = get_response(url)
    if response:
        return response.content
    sys.exit("Couldn't get video")

def get_audio(post_data):
    video_url = post_data[0]["data"]["children"]\
            [0]["data"]["secure_media"]\
            ["reddit_video"]["fallback_url"]
    possible_urls = [
        "/".join(video_url.split("/")[:-1]) + "/DASH_audio.mp4",
        "/".join(video_url.split("/")[:-1]) + "/audio",
    ]
    for url in possible_urls:
        response = get_response(url)
        if response:
            return response.content
    sys.exit("Couldn't get audio")

def merge_video_and_audio(video_filename, audio_filename, output):
    try:
        subprocess.call(f"ffmpeg -i {video_filename} -i {audio_filename} -shortest {output}".split())
    except Exception:
        sys.exit("There was a problem executing ffmpeg")

def download_video(post_url):
    print("Fetching post data...")
    post_data = get_post_data(post_url + ".json")
    post_id = get_post_id(post_data)
    video_filename = f"{post_id}.mp4"
    audio_filename = f"{post_id}.mp3"
    result_filename = f"video_{post_id}.mp4"
    print("Fetching video...")
    video = get_video(post_data)
    print("Fetching audio...")
    audio = get_audio(post_data)
    print("Writing video to file...")
    write_file(video_filename, video)
    print("Writing audio to file...")
    write_file(audio_filename, audio)
    print("Merging video and audio...")
    merge_video_and_audio(video_filename, audio_filename,result_filename)
    print(f"Output written to {result_filename}")

def main():
    args = get_args()
    download_video(args[0])

if __name__ == "__main__":
    main()
