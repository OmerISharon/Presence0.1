import argparse
import os
import random
import sys
import requests

# ───────────────────────────────────────────────────────
# Script Usage (CLI):
#   python get_pexels_media.py <subject> <media_count> <output_dir>
#
# Arguments:
#   <subject>       : Required. Search term for Pexels media.
#   <media_count>   : Required. Number of media to download.
#   <output_dir>    : Required. Folder to save downloaded media.
# ───────────────────────────────────────────────────────

# Load API key from credentials module
CREDENTIALS_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Credentials"
sys.path.insert(0, CREDENTIALS_DIR)
from credential_keys import PEXELS_API_KEY

# Global tracker for downloaded media IDs
downloaded_media_ids = set()

def is_hd(width, height):
    return max(width, height) >= 1280 and min(width, height) >= 720

def download_media(url, output_path):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"✅ Saved to {output_path}")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")


def download_pexels_url_to_local(url: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    # Extract filename from the URL
    filename = url.split("/")[-1].split("?")[0]
    extension = os.path.splitext(filename)[1].lower()

    # Add fallback if no extension is found
    if not extension:
        extension = ".jpg"

    output_path = os.path.join(output_dir, filename)

    try:
        print(f"⬇️ Downloading from URL: {url}")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"✅ Saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return ""


def run_pexels_download(subject, media_count, output_dir, media_type="video", orientation="portrait", select_url=False):
    print(f"\n🔍 Fetching {media_count} {media_type} for subject: '{subject}'")
    print(f"{'🌐 Collecting URLs' if select_url else f'💾 Saving {media_type} to: {output_dir}'}\n")

    if not select_url:
        os.makedirs(output_dir, exist_ok=True)

    results = []   # 👈 list of output paths OR URLs

    url_media_type = "videos" if media_type == "video" else "v1"
    headers = {"Authorization": PEXELS_API_KEY}
    api_url = f"https://api.pexels.com/{url_media_type}/search?query={subject}&orientation={orientation}&per_page=50"

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"API error: {response.status_code} - {response.text}")
        return []

    data = response.json()
    media_list = data.get("videos" if media_type == "video" else "photos", [])
    random.shuffle(media_list)

    print(f"📦 Found {len(media_list)} {media_type}s. Filtering for HD...\n")

    count = 0
    for media in media_list:
        media_id = str(media.get("id"))
        if media_id in downloaded_media_ids:
            continue

        if media_type == "video":
            if media.get("duration", 0) < 10:
                continue

            best_file = None
            max_area = 0
            for file in media.get("video_files", []):
                width = file.get("width", 0)
                height = file.get("height", 0)
                if is_hd(width, height):
                    area = width * height
                    if area > max_area:
                        max_area = area
                        best_file = file
        elif media_type == "image":
            best_file = media

        if best_file:
            if media_type == "video":
                url = best_file["link"]
                output_path = os.path.join(output_dir, f"{media_id}.mp4")
            elif media_type == "image":
                url = best_file["src"]["original"]
                output_path = os.path.join(output_dir, f"{media_id}.jpg")

            print(f"{'🔗 Selected' if select_url else '⬇️  Downloading'} {media_type} {media_id} ({best_file['width']}x{best_file['height']})")

            if select_url:
                results.append(url)
            else:
                download_media(url, output_path)
                downloaded_media_ids.add(media_id)
                results.append(output_path)

            count += 1

        if count >= media_count:
            break

    if count == 0:
        print(f"⚠️ No suitable HD {media_type}s found.")
    else:
        print(f"✅ {('Collected URLs for' if select_url else 'Downloaded')} {count} {media_type}(s) for '{subject}'.")

    return results



def main():
    parser = argparse.ArgumentParser(description="Download media from Pexels based on subject.")
    parser.add_argument("subject", type=str, help="The subject to search for (e.g. 'cats')")
    parser.add_argument("media_count", type=int, help="Number of media items to download")
    parser.add_argument("output_dir", type=str, help="Directory to save downloaded media")
    parser.add_argument("--media_type", type=str, choices=["video", "image"], default="video", help="Type of media to download (default: video)")
    parser.add_argument("--orientation", type=str, choices=["portrait", "landscape", "square"], default="portrait", help="Preferred orientation (default: portrait)")

    args = parser.parse_args()

    downloaded_files = run_pexels_download(
        subject=args.subject,
        media_count=args.media_count,
        output_dir=args.output_dir,
        media_type=args.media_type,
        orientation=args.orientation
    )

    print(fr"LIST OF DOWNLOADED FILES: {downloaded_files}")

if __name__ == "__main__":
    main()
