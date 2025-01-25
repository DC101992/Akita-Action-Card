import requests
from requests_oauthlib import OAuth1
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Test Media Upload API URL
def test_media_upload_url():
    url = "https://upload.twitter.com/1.1/media/upload.json"
    auth = OAuth1(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET
    )

    # Simulate a POST request for media upload
    try:
        response = requests.post(url, auth=auth, data={"command": "INIT", "media_type": "image/jpeg", "total_bytes": 1})
        print(f"DEBUG: Status Code: {response.status_code}")
        print(f"DEBUG: Response Text: {response.text}")

        if response.status_code == 200:
            print("Media Upload API URL is accessible and correct.")
        elif response.status_code == 401:
            print("Unauthorized. Please check your authentication credentials.")
        elif response.status_code == 403:
            print("Access to this API URL is forbidden. Check app permissions.")
        elif response.status_code == 400:
            print("Bad request. Ensure your parameters and data are correct.")
        else:
            print(f"Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to Media Upload API URL: {e}")

if __name__ == "__main__":
    test_media_upload_url()
