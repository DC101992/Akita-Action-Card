import sys
import os
from io import BytesIO
from dotenv import load_dotenv

# Add the directory containing bot.py to the Python path
sys.path.append("C:\\Users\\taggm\\OneDrive\\Desktop\\akita action card")

# Import functions from bot.py
from bot import upload_media_to_twitter, fetch_image_from_github

# Load environment variables
load_dotenv()

# Mock Discord interaction for testing
class MockInteraction:
    def __init__(self):
        self.user = MockUser()

    async def send_message(self, content, ephemeral=False):
        print(f"[MOCK Interaction] Message Sent: {content}")

class MockUser:
    def __init__(self):
        self.id = "123456789"

async def share_callback(interaction):
    print("Button callback triggered.")
    try:
        print(f"Interaction user: {interaction.user.id}")

        # Fetch the image from GitHub
        IMAGE_URL = "https://raw.githubusercontent.com/DC101992/Akita-Action-Card/main/akita%20action%20card.jpg"
        image_data = fetch_image_from_github(IMAGE_URL)
        if not image_data:
            await interaction.send_message("Failed to fetch image.", ephemeral=True)
            return

        # Upload to Twitter
        media_id = upload_media_to_twitter(image_data)
        if media_id:
            await interaction.send_message("Tweet successfully posted!", ephemeral=True)
        else:
            await interaction.send_message("Failed to post tweet.", ephemeral=True)
    except Exception as e:
        print(f"Error in callback: {e}")
        await interaction.send_message("Error occurred while sharing.", ephemeral=True)

if __name__ == "__main__":
    # Run the share_callback function with a mock interaction
    import asyncio
    interaction = MockInteraction()
    asyncio.run(share_callback(interaction))
