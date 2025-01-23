import sys
import os
import json
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Bot
from nextcord import Interaction
from nextcord.ui import View, Button
import tweepy  # For Twitter API integration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the directory containing bot.py to the Python path (if needed for imports)
sys.path.append("C:\\Users\\taggm\\OneDrive\\Desktop\\akita action card")

# Discord bot and API setup
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
IMAGE_URL = "https://raw.githubusercontent.com/DC101992/Akita-Action-Card/main/akita%20action%20card.jpg"
OUTPUT_PATH = "output_image.png"
API_ENDPOINT = "https://free-api.vestige.fi/asset/523683256/prices/simple/1D"
FONT_URL = "https://raw.githubusercontent.com/DC101992/Akita-Action-Card/main/arial.ttf"
SHARE_LOG_FILE = "share_log.json"

# Initialize the bot
intents = nextcord.Intents.default()
intents.messages = True
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents)


def post_to_twitter(image_path: str, status: str):
    """Posts an image with a status to Twitter."""
    try:
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        twitter_api = tweepy.API(auth)

        # Post the image and text
        twitter_api.update_with_media(filename=image_path, status=status)
        return True
    except Exception as e:
        print(f"Error posting to Twitter: {e}")
        return False


def log_share(user_id: int):
    """Logs the share action for a user."""
    if not os.path.exists(SHARE_LOG_FILE):
        with open(SHARE_LOG_FILE, 'w') as file:
            json.dump({}, file)

    with open(SHARE_LOG_FILE, 'r') as file:
        logs = json.load(file)

    logs[str(user_id)] = logs.get(str(user_id), 0) + 1

    with open(SHARE_LOG_FILE, 'w') as file:
        json.dump(logs, file)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


async def fetch_price_data():
    """Fetches price data from the API."""
    try:
        response = requests.get(API_ENDPOINT, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching price data: {e}")
        return None


def calculate_24hr_change(data):
    """Calculates the 24-hour price change."""
    if not data or len(data) < 2:
        return None
    opening_price = data[0]['price']
    closing_price = data[-1]['price']
    price_change = ((closing_price - opening_price) / opening_price) * 100
    return round(price_change, 2)


def fetch_image_from_url(image_url):
    """Fetches an image from a URL."""
    try:
        response = requests.get(image_url, timeout=5)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error fetching the image: {e}")
        return None


def fetch_font_from_url(font_url, font_size):
    """Fetches a font from a URL."""
    try:
        response = requests.get(font_url, timeout=5)
        response.raise_for_status()
        return ImageFont.truetype(BytesIO(response.content), font_size)
    except Exception as e:
        print(f"Error fetching font: {e}")
        return ImageFont.load_default()


def draw_action_card(image, output_path, price_data):
    """Draws the action card image."""
    try:
        draw = ImageDraw.Draw(image)
        font_large = fetch_font_from_url(FONT_URL, 60)
        font_medium = fetch_font_from_url(FONT_URL, 40)

        # Layout
        x_right = image.width * 0.85
        y_fields_top = 170
        field_spacing = 40

        # Ticker
        ticker_text = "$AKTA"
        draw.text((x_right, y_fields_top), ticker_text, fill="white", font=font_large)

        # Price and Change
        price_in_algo = price_data[-1]['price']
        change_24hr = calculate_24hr_change(price_data)
        draw.text((x_right, y_fields_top + field_spacing), f"{price_in_algo:.6f} ALGO", fill="white", font=font_large)
        draw.text(
            (x_right, y_fields_top + 2 * field_spacing),
            f"24hr Change: {change_24hr:.2f}%",
            fill="green" if change_24hr > 0 else "red",
            font=font_medium,
        )

        image.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error drawing action card: {e}")
        return None


@bot.slash_command(name="action_card", description="Generate and share an Action Card.")
async def action_card(interaction: Interaction):
    try:
        await interaction.response.defer()
        image = fetch_image_from_url(IMAGE_URL)
        price_data = await fetch_price_data()
        output_path = draw_action_card(image, OUTPUT_PATH, price_data)
        if not output_path:
            await interaction.followup.send("Error generating the action card.")
            return

        file = nextcord.File(output_path, filename="action_card.png")

        class ShareButton(View):
            def __init__(self):
                super().__init__(timeout=300)
                self.add_item(Button(label="Share to Twitter", style=nextcord.ButtonStyle.primary))

            @staticmethod
            async def share_callback(interaction):
                if post_to_twitter(OUTPUT_PATH, "🚀 Check out Akita's performance!"):
                    await interaction.response.send_message("Tweet successfully posted!", ephemeral=True)
                else:
                    await interaction.response.send_message("Failed to post tweet.", ephemeral=True)

        await interaction.followup.send("Here is your Action Card:", file=file, view=ShareButton())
    except Exception as e:
        print(f"Error occurred: {e}")
        await interaction.followup.send("An error occurred while processing your request.")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)


       
    
   
 
      
 
                 
                     
