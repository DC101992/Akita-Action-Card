import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Bot
from nextcord import Interaction
from nextcord.ui import View, Button
from io import BytesIO
import tweepy  # For Twitter API integration
from requests_oauthlib import OAuth1

# Initialize bot and client
intents = nextcord.Intents.default()
intents.messages = True
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents)

# Load environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
IMAGE_URL = "https://raw.githubusercontent.com/DC101992/Akita-Action-Card/main/akita%20action%20card.jpg"
OUTPUT_PATH = "output_image.png"
API_ENDPOINT = "https://free-api.vestige.fi/asset/523683256/prices/simple/1D"
TWITTER_ENABLED = True
SHARE_LOG_FILE = "share_log.json"

# Font URL
FONT_URL = "https://raw.githubusercontent.com/DC101992/Akita-Action-Card/main/arial.ttf"

# Twitter API keys
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

def fetch_image_from_github(image_url):
    """Fetch the image from GitHub."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        print(f"Error fetching image from GitHub: {e}")
        return None

def upload_media_to_twitter(image_data):
    """Uploads media to Twitter and returns the media_id."""
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
        init_response.raise_for_status()
        media_id = init_response.json()["media_id"]
        print(f"DEBUG: Media INIT successful. Media ID: {media_id}")

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
            append_response.raise_for_status()
            print("DEBUG: Media APPEND successful.")

        # Step 3: FINALIZE - Finalize the media upload
        finalize_data = {
            "command": "FINALIZE",
            "media_id": media_id
        }
        finalize_response = requests.post(url, auth=auth, data=finalize_data)
        finalize_response.raise_for_status()
        print("DEBUG: Media FINALIZE successful.")

        # Cleanup temporary file
        os.remove(temp_image_path)

        return media_id
    except Exception as e:
        print(f"Error during media upload: {e}")
        return None

# Remaining bot implementation...
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

async def fetch_price_data():
    try:
        response = requests.get(API_ENDPOINT, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"DEBUG: API response: {data}")  # Debugging output
        return data
    except Exception as e:
        print(f"Error fetching price data: {e}")
        return None

def calculate_24hr_change(data):
    if not data or len(data) < 2:
        return None
    opening_price = data[0]['price']
    closing_price = data[-1]['price']
    price_change = ((closing_price - opening_price) / opening_price) * 100
    return round(price_change, 2)

def fetch_image_from_url(image_url):
    try:
        response = requests.get(image_url, timeout=5)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error fetching the image: {e}")
        return None

def fetch_font_from_url(font_url, font_size):
    try:
        response = requests.get(font_url, timeout=5)
        response.raise_for_status()
        font_data = BytesIO(response.content)
        return ImageFont.truetype(font_data, font_size)
    except Exception as e:
        print(f"Error fetching font: {e}")
        return ImageFont.load_default()  # Fallback to default font

def draw_action_card(image, output_path, price_data):
    try:
        draw = ImageDraw.Draw(image)

        # Fetch fonts dynamically
        font_large = fetch_font_from_url(FONT_URL, 60)
        font_medium = fetch_font_from_url(FONT_URL, 40)

        x_right_ticker = image.width * 0.85
        x_right_price = image.width * 0.81
        x_right_change = image.width * 0.84

        y_logo_bottom = 150
        y_fields_top = y_logo_bottom + 20
        field_spacing = 40

        # Ticker ($AKTA)
        ticker_text = "$AKTA"
        ticker_bbox = draw.textbbox((0, 0), ticker_text, font=font_large)
        ticker_width = ticker_bbox[2] - ticker_bbox[0]
        ticker_height = ticker_bbox[3] - ticker_bbox[1]
        draw.text((x_right_ticker - ticker_width // 2, y_fields_top), ticker_text, fill="white", font=font_large)

        # ALGO Price and Change
        price_in_algo = price_data[-1]['price']
        opening_price = price_data[0]['price']
        change_24hr = calculate_24hr_change(price_data)

        price_text = f"{price_in_algo:.6f} ALGO"
        price_bbox = draw.textbbox((0, 0), price_text, font=font_large)
        price_width = price_bbox[2] - price_bbox[0]
        y_price_top = y_fields_top + ticker_height + field_spacing
        draw.text((x_right_price - price_width // 2, y_price_top), price_text, fill="white", font=font_large)

        change_color = "green" if change_24hr > 0 else "red"
        price_change_text = f"24hr Change: {change_24hr:.2f}%"
        price_change_bbox = draw.textbbox((0, 0), price_change_text, font=font_medium)
        price_change_width = price_change_bbox[2] - price_change_bbox[0]
        y_change_top = y_price_top + price_bbox[3] - price_bbox[1] + field_spacing
        draw.text((x_right_change - price_change_width // 2, y_change_top), price_change_text, fill=change_color, font=font_medium)

        # Save the updated image
        image.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error drawing action card: {e}")
        return None

@bot.slash_command(name="action_card", description="Generate and optionally share an Action Card.")
async def action_card(interaction: Interaction):
    try:
        # Acknowledge the interaction
        await interaction.response.defer()

        # Fetch the image from the raw URL
        image = fetch_image_from_url(IMAGE_URL)
        if not image:
            await interaction.followup.send("Failed to load the action card image.")
            return

        # Fetch price data
        price_data = await fetch_price_data()  # Properly await the coroutine
        if not price_data:
            await interaction.followup.send("Failed to fetch price data.")
            return

        # Draw on the image
        output_path = draw_action_card(image, OUTPUT_PATH, price_data)
        if not output_path:
            await interaction.followup.send("Error generating the action card.")
            return

        # Send the action card with a Share button
        if os.path.exists(output_path):
            file = nextcord.File(output_path, filename="action_card.png")

            class ShareButton(View):
                def __init__(self):
                    super().__init__(timeout=300)  # Buttons expire after 5 minutes
                    self.add_item(Button(label="Share to Twitter", style=nextcord.ButtonStyle.primary, custom_id="share_button"))

                @staticmethod
                async def share_callback(interaction: Interaction):
                    print("Button callback triggered.")  # Log the interaction
                    try:
                        print(f"Interaction user: {interaction.user.id}")  # Log user ID

                        # Fetch the image from GitHub
                        image_data = fetch_image_from_github(IMAGE_URL)
                        if not image_data:
                            await interaction.response.send_message("Failed to fetch image.", ephemeral=True)
                            return

                        # Upload to Twitter
                        media_id = upload_media_to_twitter(image_data)
                        if media_id:
                            await interaction.response.send_message("Tweet successfully posted!", ephemeral=True)
                        else:
                            await interaction.response.send_message("Failed to post tweet.", ephemeral=True)
                    except Exception as e:
                        print(f"Error in callback: {e}")
                        await interaction.response.send_message("Error occurred while sharing.", ephemeral=True)

            view = ShareButton()  # Attach the share button view
            await interaction.followup.send("Here is your Action Card:", file=file, view=view)
        else:
            await interaction.followup.send("Output image not found.")
    except Exception as e:
        print(f"Error occurred: {e}")
        await interaction.followup.send("An error occurred while processing your request.")

bot.run(DISCORD_BOT_TOKEN)




       
    
        
