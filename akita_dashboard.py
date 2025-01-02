import discord
import requests
import tweepy
from PIL import Image, ImageDraw, ImageFont
import io
import os
from discord.ext import commands
import streamlit as st

# Set up your bot with discord.py
bot = commands.Bot(command_prefix="!")

# Twitter API credentials
consumer_key = 'YOUR_TWITTER_API_KEY'
consumer_secret = 'YOUR_TWITTER_API_SECRET_KEY'
access_token = 'YOUR_TWITTER_ACCESS_TOKEN'
access_token_secret = 'YOUR_TWITTER_ACCESS_TOKEN_SECRET'

# Initialize Twitter API with tweepy
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)
api = tweepy.API(auth)

# Function to send a tweet
def send_tweet(tweet_text):
    try:
        api.update_status(tweet_text)
        print(f"Tweeted: {tweet_text}")
    except tweepy.TweepError as e:
        print(f"Error sending tweet: {e}")

# Load image and API data
def load_image(image_path):
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return None
    return Image.open(image_path)

def fetch_price_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def calculate_24hr_change(data):
    if not data or len(data) < 2:
        return None
    opening_price = data[0]['price']
    closing_price = data[-1]['price']
    price_change = ((closing_price - opening_price) / opening_price) * 100
    return round(price_change, 2)

# Set paths
image_path = "path_to_your_image.jpg"  # Add correct image path for your logo/graphic
api_url = "https://free-api.vestige.fi/asset/523683256/prices/simple/1D"  # Replace with actual API URL

# Streamlit: create the action card as an app on your webpage
def create_action_card():
    price_data = fetch_price_data(api_url)
    if price_data:
        price_in_algo = price_data[-1]['price']
        change_24hr = calculate_24hr_change(price_data)
    else:
        st.error("Failed to fetch price data.")
        return

    # Open the image
    image = load_image(image_path)
    if not image:
        st.error("Image file not found.")
        return

    # Drawing text on the image
    draw = ImageDraw.Draw(image)
    font_path = "arial.ttf"  # Update with the correct font file path
    font_large = ImageFont.truetype(font_path, 60)
    font_medium = ImageFont.truetype(font_path, 40)

    x_right_ticker = image.width * 0.85
    x_right_price = image.width * 0.81
    x_right_change = image.width * 0.83

    y_logo_bottom = 150
    y_fields_top = y_logo_bottom + 20
    field_spacing = 40

    # Add the ticker symbol ($AKTA)
    ticker_text = "$AKTA"
    ticker_bbox = draw.textbbox((0, 0), ticker_text, font=font_large)
    ticker_width = ticker_bbox[2] - ticker_bbox[0]
    ticker_height = ticker_bbox[3] - ticker_bbox[1]
    draw.text((x_right_ticker - ticker_width // 2, y_fields_top), ticker_text, fill="white", font=font_large)

    # Add the current price in ALGO
    price_text = f"{price_in_algo:.6f} ALGO"
    price_bbox = draw.textbbox((0, 0), price_text, font=font_large)
    price_width = price_bbox[2] - price_bbox[0]
    y_price_top = y_fields_top + ticker_height + field_spacing
    draw.text((x_right_price - price_width // 2, y_price_top), price_text, fill="white", font=font_large)

    # Add the 24-hour price change percentage
    if change_24hr is not None:
        change_color = "green" if change_24hr > 0 else "red"
        price_change_text = f"24hr Change: {change_24hr:.2f}%"
        price_change_bbox = draw.textbbox((0, 0), price_change_text, font=font_medium)
        price_change_width = price_change_bbox[2] - price_change_bbox[0]
        y_change_top = y_price_top + price_bbox[3] - price_bbox[1] + field_spacing
        draw.text((x_right_change - price_change_width // 2, y_change_top), price_change_text, fill=change_color, font=font_medium)

    # Save image to a byte stream for sending it in Discord
    image_byte_array = io.BytesIO()
    image.save(image_byte_array, format="PNG")
    image_byte_array.seek(0)

    # Streamlit: Display action card on webpage
    st.image(image_byte_array, caption="Updated Action Card", use_container_width=True)

    # Send a tweet to Twitter
    tweet_text = f"$AKTA\nPrice: {price_in_algo:.6f} ALGO\n24hr Change: {change_24hr:.2f}%"
    send_tweet(tweet_text)

# Streamlit interface to run the app
if __name__ == "__main__":
    st.title("Akita Action Card")
    create_action_card()

   

 
