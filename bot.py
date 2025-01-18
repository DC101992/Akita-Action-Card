import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from dotenv import load_dotenv
import tweepy  # For Twitter API integration

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
APPLICATION_ID = "1325141241356095591"  # Replace with your Application ID

# Twitter API keys
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Verify token retrieval
if not DISCORD_BOT_TOKEN:
    raise ValueError("Bot token not found. Ensure your .env file contains the correct token.")

# Setup bot with intents
intents = nextcord.Intents.default()
intents.message_content = True  # Enable Message Content Intent
bot = commands.Bot(command_prefix="/", intents=intents, application_id=APPLICATION_ID)

# Paths and API
IMAGE_PATH = "./akita action card.jpg"
FONT_PATH = "./arial.ttf"
API_URL = "https://free-api.vestige.fi/asset/523683256/prices/simple/1D"
SHARE_LOG_FILE = "./share_log.json"
OUTPUT_PATH = "./output_action_card.jpg"

# Twitter client setup
def post_to_twitter(image_path: str, status: str):
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

# Logging shares
def log_share(user_id: int):
    if not os.path.exists(SHARE_LOG_FILE):
        with open(SHARE_LOG_FILE, 'w') as file:
            json.dump({}, file)

    with open(SHARE_LOG_FILE, 'r') as file:
        logs = json.load(file)

    logs[str(user_id)] = logs.get(str(user_id), 0) + 1

    with open(SHARE_LOG_FILE, 'w') as file:
        json.dump(logs, file)

# Bot events
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

# Main command for action card
@bot.slash_command(
    name="action_card",
    description="Displays the action card for Akita Dashboard"
)
async def action_card(ctx: nextcord.Interaction, text: str = None):
    # Defer the interaction
    await ctx.response.defer(ephemeral=False)

    # Load image
    if not os.path.exists(IMAGE_PATH):
        await ctx.followup.send("Image file not found.")
        return
    try:
        image = Image.open(IMAGE_PATH)
    except Exception as e:
        await ctx.followup.send(f"Error loading image: {e}")
        return

    # Fetch price data
    try:
        response = requests.get(API_URL, timeout=5)  # Set a shorter timeout
        response.raise_for_status()  # Ensure exceptions are raised for HTTP errors
        price_data = response.json()
        price_in_algo = price_data[-1]['price']
        opening_price = price_data[0]['price']
        closing_price = price_data[-1]['price']
        change_24hr = round(((closing_price - opening_price) / opening_price) * 100, 2)
    except Exception as e:
        await ctx.followup.send(f"Error fetching price data: {e}")
        return

    # Draw on the image
    try:
        draw = ImageDraw.Draw(image)
        font_large = ImageFont.truetype(FONT_PATH, 60)
        font_medium = ImageFont.truetype(FONT_PATH, 40)

        x_right_ticker = image.width * 0.85
        x_right_price = image.width * 0.81
        x_right_change = image.width * 0.83

        y_logo_bottom = 150
        y_fields_top = y_logo_bottom + 20
        field_spacing = 40

        # Ticker ($AKTA)
        ticker_text = "$AKTA"
        ticker_bbox = draw.textbbox((0, 0), ticker_text, font=font_large)
        ticker_width = ticker_bbox[2] - ticker_bbox[0]
        ticker_height = ticker_bbox[3] - ticker_bbox[1]
        draw.text((x_right_ticker - ticker_width // 2, y_fields_top), ticker_text, fill="white", font=font_large)

        # ALGO Price
        price_text = f"{price_in_algo:.6f} ALGO"
        price_bbox = draw.textbbox((0, 0), price_text, font=font_large)
        price_width = price_bbox[2] - price_bbox[0]
        y_price_top = y_fields_top + ticker_height + field_spacing
        draw.text((x_right_price - price_width // 2, y_price_top), price_text, fill="white", font=font_large)

        # 24-Hour Change
        change_color = "green" if change_24hr > 0 else "red"
        price_change_text = f"24hr Change: {change_24hr:.2f}%"
        price_change_bbox = draw.textbbox((0, 0), price_change_text, font=font_medium)
        price_change_width = price_change_bbox[2] - price_change_bbox[0]
        y_change_top = y_price_top + price_bbox[3] - price_bbox[1] + field_spacing
        draw.text((x_right_change - price_change_width // 2, y_change_top), price_change_text, fill=change_color, font=font_medium)

        # Save the updated image
        image.save(OUTPUT_PATH)
    except Exception as e:
        await ctx.followup.send(f"Error drawing on the image: {e}")
        return

    # Send the image
    try:
        if os.path.exists(OUTPUT_PATH):
            await ctx.followup.send(file=nextcord.File(OUTPUT_PATH))
        else:
            await ctx.followup.send("Output image not found.")
    except Exception as e:
        await ctx.followup.send(f"Error sending the image: {e}")

# Share button command
@bot.slash_command(
    name="share_action_card",
    description="Generate and share your Akita action card"
)
async def share_action_card(ctx: nextcord.Interaction):
    await ctx.response.defer(ephemeral=False)

    # Define the button callback
    async def share_callback(interaction: nextcord.Interaction):
        log_share(ctx.user.id)  # Log the share action
        status = "🚀 Check out Akita's performance! #Crypto #Algorand"
        success = post_to_twitter(OUTPUT_PATH, status)
        if success:
            await interaction.response.send_message("Card successfully shared on Twitter!")
        else:
            await interaction.response.send_message("Failed to share the card on Twitter.")

    # Create share button
    share_button = Button(label="Share Now", style=nextcord.ButtonStyle.primary, emoji="📤")
    share_button.callback = share_callback

    # Send the button
    view = View()
    view.add_item(share_button)
    await ctx.followup.send("Click below to share your action card!", view=view)

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
