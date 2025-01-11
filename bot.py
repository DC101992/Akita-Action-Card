import os
import requests
from PIL import Image, ImageDraw, ImageFont
import nextcord  # For Discord bot functionality
from nextcord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
APPLICATION_ID = "1325141241356095591"  # Replace with your actual Application ID

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

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(name="action_card", description="Displays the action card for Akita Dashboard")
async def action_card(ctx: nextcord.Interaction):
    await ctx.response.defer()  # Defer to give time for processing
    
    # Load image
    if not os.path.exists(IMAGE_PATH):
        await ctx.send("Image file not found.")
        return
    image = Image.open(IMAGE_PATH)

    # Fetch price data
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        price_data = response.json()
        price_in_algo = price_data[-1]['price']
        opening_price = price_data[0]['price']
        closing_price = price_data[-1]['price']
        change_24hr = round(((closing_price - opening_price) / opening_price) * 100, 2)
    except Exception as e:
        await ctx.send(f"Error fetching price data: {e}")
        return

    # Draw on the image
    draw = ImageDraw.Draw(image)
    font_large = ImageFont.truetype(FONT_PATH, 60)
    font_medium = ImageFont.truetype(FONT_PATH, 40)

    # Field Positions to match Streamlit layout
    x_right_ticker = image.width * 0.85  # Move ticker field slightly right
    x_right_price = image.width * 0.81   # Align price field
    x_right_change = image.width * 0.83  # Align change field

    y_logo_bottom = 150  # Matches Streamlit logo position
    y_fields_top = y_logo_bottom + 20  # Fields just below logo
    field_spacing = 40  # Matches vertical spacing in Streamlit

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
    if change_24hr is not None:
        change_color = "green" if change_24hr > 0 else "red"
        price_change_text = f"24hr Change: {change_24hr:.2f}%"
        price_change_bbox = draw.textbbox((0, 0), price_change_text, font=font_medium)
        price_change_width = price_change_bbox[2] - price_change_bbox[0]
        y_change_top = y_price_top + price_bbox[3] - price_bbox[1] + field_spacing
        draw.text((x_right_change - price_change_width // 2, y_change_top), price_change_text, fill=change_color, font=font_medium)

    # Save the image
    output_path = "./output_action_card.jpg"
    image.save(output_path)

    # Send the image in Discord
    await ctx.send(file=nextcord.File(output_path))

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
