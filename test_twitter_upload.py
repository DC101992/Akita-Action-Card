import os
import requests
from requests_oauthlib import OAuth1
import sys

# Your Twitter API keys as environment variables
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

def upload_media_to_twitter(image_data):
    url = "https://upload.twitter.com/1.1/media/upload.json"
    auth = OAuth1(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET
    )
    try:
        # Save image data to a temporary file
        temp_image_path = "./temp_image.jpg"
        with open(temp_image_path, "wb") as file:
            file.write(image_data.getbuffer())

        # Step 1: INIT - Initialize media upload
        total_bytes = os.path.getsize(temp_image_path)
        init_data = {
            "command": "INIT",
            "media_type": "image/jpeg",
            "total_bytes": total_bytes
        }
        init_response = requests.post(url, auth=auth, data=init_data)
        print(f"INIT Response: {init_response.status_code}, {init_response.text}")
        init_response.raise_for_status()
        media_id = init_response.json()["media_id"]

        # Step 2: APPEND - Upload the media in chunks
        with open(temp_image_path, "rb") as file:
            media_data = file.read()
            append_data = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": 0
            }
            files = {"media": media_data}
            append_response = requests.post(url, auth=auth, data=append_data, files=files)
            print(f"APPEND Response: {append_response.status_code}, {append_response.text}")
            append_response.raise_for_status()

        # Step 3: FINALIZE - Finalize the media upload
        finalize_data = {
            "command": "FINALIZE",
            "media_id": media_id
        }
        finalize_response = requests.post(url, auth=auth, data=finalize_data)
        print(f"FINALIZE Response: {finalize_response.status_code}, {finalize_response.text}")
        finalize_response.raise_for_status()

        # Cleanup temporary file
        os.remove(temp_image_path)

        return media_id
    except Exception as e:
        print(f"Error during media upload: {e}")
        return None

if __name__ == "__main__":
    # Test with a sample image
    try:
        with open("test_image.jpg", "rb") as image_file:
            image_data = image_file.read()
        media_id = upload_media_to_twitter(BytesIO(image_data))
        print(f"Uploaded Media ID: {media_id}")
    except FileNotFoundError:
        print("Please ensure 'test_image.jpg' exists in the same directory.")
