import os
from dotenv import load_dotenv
from tweepy import Client

# Load environment variables from .env
load_dotenv()

# Retrieve Bearer Token from the .env file
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def verify_twitter_with_bearer():
    """Verifies Twitter API access using the Bearer Token and explores v2 endpoints."""
    if not TWITTER_BEARER_TOKEN:
        print("❌ Bearer Token is missing. Please add it to your .env file.")
        return

    try:
        # Initialize Tweepy Client with Bearer Token
        client = Client(bearer_token=TWITTER_BEARER_TOKEN)

        # Test basic v2 endpoint: Get your own user details
        try:
            user = client.get_user(username="cruise_death")
            if user.data:
                print("✅ Successfully accessed user details with Bearer Token!")
                print(f"User Name: {user.data['name']}")
                print(f"User Handle: {user.data['username']}")
                print(f"User ID: {user.data['id']}")
            else:
                print("⚠️ Could not retrieve user details.")
        except Exception as e:
            print(f"Error fetching user details: {e}")

        # Test another v2 endpoint: Search recent tweets
        try:
            query = "Akita Inu"
            tweets = client.search_recent_tweets(query=query, max_results=10)  # Adjusted max_results
            print("\n🔍 Recent Tweets:")
            for tweet in tweets.data:
                print(f"- {tweet.text}")
        except Exception as e:
            print(f"Error searching recent tweets: {e}")

    except Exception as e:
        print(f"❌ Error initializing Tweepy Client with Bearer Token: {e}")

if __name__ == "__main__":
    verify_twitter_with_bearer()
