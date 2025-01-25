import os
import requests
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_twitter_credentials():
    try:
        print("DEBUG: Loading Twitter credentials...")  # Debugging statement
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        print(f"DEBUG: API Key: {api_key}")
        print(f"DEBUG: Access Token: {access_token}")
        print(f"DEBUG: Bearer Token: {bearer_token}")

        # Test Bearer Token
        if bearer_token:
            print("DEBUG: Testing Bearer Token...")
            url = "https://api.twitter.com/2/users/me"
            headers = {"Authorization": f"Bearer {bearer_token}"}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print("Bearer Token is valid.")
            else:
                print("Bearer Token is invalid.")
                print(f"DEBUG: Response: {response.status_code} - {response.text}")
        else:
            print("No Bearer Token provided.")

        # Test OAuth 1.0a Credentials
        print("DEBUG: Testing OAuth 1.0a credentials...")
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        twitter_api = tweepy.API(auth)

        # Test if credentials work
        twitter_api.verify_credentials()
        print("OAuth 1.0a credentials are valid.")
    except tweepy.errors.Unauthorized as e:
        print("Invalid or expired Twitter credentials. Please check your tokens.")
        print(f"Error details: {e}")
    except Exception as e:
        print("An unexpected error occurred.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_twitter_credentials()
