import asyncio
import os
from PIL import Image
from bot import fetch_price_data, draw_action_card
from tweepy import OAuthHandler, API

# Correct raw GitHub image URL
IMAGE_URL = "https://raw.githubusercontent.com/DC101992/Akita-Action-Card/main/akita%20action%20card.jpg"
OUTPUT_IMAGE_PATH = "output_image.png"

# Test fetching price data
async def test_fetch_price_data():
    """Test fetching price data from the API."""
    data = await fetch_price_data()
    if data:
        print(f"Price data fetched successfully: {data}")
    else:
        print("Failed to fetch price data.")

# Test fetching the image from GitHub
def test_fetch_image_from_url():
    """Test fetching the action card base image from GitHub."""
    from bot import fetch_image_from_url

    print(f"Fetching image from {IMAGE_URL}")
    image = fetch_image_from_url(IMAGE_URL)
    if image:
        print("Image fetched successfully.")
        return image
    else:
        print("Failed to fetch the image.")
        return None

# Test drawing the action card
def test_draw_action_card():
    """Test generating and saving the action card."""
    image = test_fetch_image_from_url()
    if not image:
        print("Image fetching failed. Cannot test action card generation.")
        return

    price_data = [{"price": 0.005}, {"price": 0.006}]  # Example price data for testing
    output_path = draw_action_card(image, OUTPUT_IMAGE_PATH, price_data)
    if output_path and os.path.exists(output_path):
        print(f"Action card generated successfully and saved to {output_path}")
    else:
        print("Failed to generate or save the action card.")

# Test posting to Twitter
def test_post_to_twitter():
    """Test posting the generated action card to Twitter."""
    from bot import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

    # Ensure the image exists before posting
    if not os.path.exists(OUTPUT_IMAGE_PATH):
        print(f"Error: File not found - {OUTPUT_IMAGE_PATH}")
        return

    # Twitter API authentication
    try:
        auth = OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        twitter_api = API(auth)

        # Upload the media (image) to Twitter
        media = twitter_api.media_upload(OUTPUT_IMAGE_PATH)
        print(f"Media uploaded successfully with media_id: {media.media_id_string}")

        # Post the tweet with the uploaded media
        status = "🚀 Check out Akita's performance!"
        twitter_api.update_status(status=status, media_ids=[media.media_id_string])
        print("Tweet posted successfully!")
    except Exception as e:
        print(f"Error posting to Twitter: {e}")

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_fetch_price_data())
    test_draw_action_card()
    test_post_to_twitter()
