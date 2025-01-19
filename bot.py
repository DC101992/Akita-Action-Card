import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Bot
from nextcord import Interaction

# Initialize bot and client
intents = nextcord.Intents.default()
intents.messages = True
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents)

# Load environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
FONT_PATH = "path/to/font.ttf"
IMAGE_PATH = "path/to/base_image.png"
OUTPUT_PATH = "output_image.png"
API_ENDPOINT = "https://api.example.com/prices"
TWITTER_ENABLED = False

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

async def fetch_price_data():
    try:
        response = requests.get(API_ENDPOINT, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching price data: {e}")
        return None

def draw_action_card(image_path, output_path, price_data):
    try:
        image = Image.open(image_path)
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
        price_in_algo = price_data[-1]['price']
        opening_price = price_data[0]['price']
        closing_price = price_data[-1]['price']
        change_24hr = round(((closing_price - opening_price) / opening_price) * 100, 2)

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
        image.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error drawing action card: {e}")
        return None

@bot.slash_command(name="action_card", description="Generate and optionally share an Action Card.")
async def action_card(interaction: Interaction, share_to_twitter: bool = False):
    await interaction.response.defer()

    # Load image
    if not os.path.exists(IMAGE_PATH):
        await interaction.followup.send("Image file not found.")
        return

    # Fetch price data
    price_data = await bot.loop.run_in_executor(None, fetch_price_data)
    if not price_data:
        await interaction.followup.send("Failed to fetch price data.")
        return

    # Draw on the image
    output_path = draw_action_card(IMAGE_PATH, OUTPUT_PATH, price_data)
    if not output_path:
        await interaction.followup.send("Error generating the action card.")
        return

    # Send the image
    try:
        if os.path.exists(output_path):
            file = nextcord.File(output_path, filename="action_card.png")
            await interaction.followup.send("Here is your Action Card:", file=file)
        else:
            await interaction.followup.send("Output image not found.")
    except Exception as e:
        print(f"Error sending the image: {e}")
        await interaction.followup.send("Error sending the action card.")

    # Optionally share to Twitter
    if share_to_twitter and TWITTER_ENABLED:
        try:
            # Example placeholder code for posting to Twitter
            print("Posting to Twitter...")
            await interaction.followup.send("Action Card shared on Twitter!")
        except Exception as e:
            print(f"Error posting to Twitter: {e}")
            await interaction.followup.send("Failed to share on Twitter.")

bot.run(DISCORD_BOT_TOKEN)



     


 
 
          
