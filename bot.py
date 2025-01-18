import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from dotenv import load_dotenv
from flask import Flask, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session
import threading
import tweepy  # For Twitter API integration

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
APPLICATION_ID = "1325141241356095591"  # Replace with your Application ID

# Twitter API keys
CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:5000/callback"
AUTHORIZATION_BASE_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]

# Paths and API
IMAGE_PATH = "./akita action card.jpg"
FONT_PATH = "./arial.ttf"
API_URL = "https://free-api.vestige.fi/asset/523683256/prices/simple/1D"
SHARE_LOG_FILE = "./share_log.json"
OUTPUT_PATH = "./output_action_card.jpg"

# Flask app for OAuth2 authentication with Twitter
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'a_random_secret_key')

@app.route("/")
def index():
    twitter = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    authorization_url, state = twitter.authorization_url(AUTHORIZATION_BASE_URL)
    session["oauth_state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    twitter = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES, state=session.get("oauth_state"))
    token = twitter.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url)
    session["oauth_token"] = token
    return "Authentication successful! Now you can share tweets through your bot."

def get_twitter_session():
    token = session.get("oauth_token")
    if not token:
        raise Exception("User not authenticated.")
    return OAuth2Session(CLIENT_ID, token=token)

# Initialize Discord bot
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents, application_id=APPLICATION_ID)

# Twitter client setup with Tweepy (using OAuth1)
def post_to_twitter(image_path: str, status: str):
    try:
        auth = tweepy.OAuthHandler(os.getenv("TWITTER_API_KEY"), os.getenv("TWITTER_API_SECRET"))
        auth.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_SECRET"))
        twitter_api = tweepy.API(auth)
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

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(
    name="action_card",
    description="Displays the action card for Akita Dashboard"
)
async def action_card(ctx: nextcord.Interaction, text: str = None):
    await ctx.response.defer(ephemeral=False)

    if not os.path.exists(IMAGE_PATH):
        await ctx.followup.send("Image file not found.")
        return

    try:
        image = Image.open(IMAGE_PATH)
    except Exception as e:
        await ctx.followup.send(f"Error loading image: {e}")
        return

    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        price_data = response.json()
        price_in_algo = price_data[-1]['price']
        opening_price = price_data[0]['price']
        change_24hr = round(((price_in_algo - opening_price) / opening_price) * 100, 2)
    except Exception as e:
        await ctx.followup.send(f"Error fetching price data: {e}")
        return

    try:
        draw = ImageDraw.Draw(image)
        font_large = ImageFont.truetype(FONT_PATH, 60)
        x_right_ticker = image.width * 0.85
        ticker_text = "$AKTA"
        ticker_bbox = draw.textbbox((0, 0), ticker_text, font=font_large)
        draw.text((x_right_ticker - (ticker_bbox[2] - ticker_bbox[0]) // 2, 100), ticker_text, fill="white", font=font_large)
        
        image.save(OUTPUT_PATH)
    except Exception as e:
        await ctx.followup.send(f"Error drawing on the image: {e}")
        return

    try:
        if os.path.exists(OUTPUT_PATH):
            await ctx.followup.send(file=nextcord.File(OUTPUT_PATH))
        else:
            await ctx.followup.send("Output image not found.")
    except Exception as e:
        await ctx.followup.send(f"Error sending the image: {e}")

@bot.slash_command(
    name="share_action_card",
    description="Generate and share your Akita action card"
)
async def share_action_card(ctx: nextcord.Interaction):
    await ctx.response.defer(ephemeral=False)

    async def share_callback(interaction: nextcord.Interaction):
        log_share(ctx.user.id)
        status = "🚀 Check out Akita's performance! #Crypto #Algorand"
        success = post_to_twitter(OUTPUT_PATH, status)
        if success:
            await interaction.response.send_message("Card successfully shared on Twitter!")
        else:
            await interaction.response.send_message("Failed to share the card on Twitter.")

    share_button = Button(label="Share Now", style=nextcord.ButtonStyle.primary, emoji="📤")
    share_button.callback = share_callback

    view = View()
    view.add_item(share_button)
    await ctx.followup.send("Click below to share your action card!", view=view)

# Run the Flask app in a separate thread to handle Twitter OAuth
def run_flask():
    app.run(port=5000, threaded=True)

# Run Flask server and the Discord bot
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

bot.run(DISCORD_BOT_TOKEN)
