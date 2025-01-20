import os
import requests
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# Load image and API data
def load_image(image_path):
    if not os.path.exists(image_path):
        st.error(f"Image file not found: {image_path}")
        return None
    return Image.open(image_path)

def fetch_price_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return None

def calculate_24hr_change(data):
    if not data or len(data) < 2:
        return None
    opening_price = data[0]['price']
    closing_price = data[-1]['price']
    price_change = ((closing_price - opening_price) / opening_price) * 100
    return round(price_change, 2)

# Define paths and URLs
image_path = "akita_action_card.jpg"  # Use a consistent relative path
api_url = "https://free-api.vestige.fi/asset/523683256/prices/simple/1D"

# Streamlit layout
st.title("Akita Dashboard")
st.header("Action Card Preview")

image = load_image(image_path)
price_data = fetch_price_data(api_url)
if price_data:
    price_in_algo = price_data[-1]['price']
    change_24hr = calculate_24hr_change(price_data)

if image:
    # Prepare drawing
    draw = ImageDraw.Draw(image)
    font_path = "./arial.ttf"  # Ensure this points to a valid .ttf file
    font_large = ImageFont.truetype(font_path, 60)
    font_medium = ImageFont.truetype(font_path, 40)

    # Field Positions
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
    if change_24hr is not None:
        change_color = "green" if change_24hr > 0 else "red"
        price_change_text = f"24hr Change: {change_24hr:.2f}%"
        price_change_bbox = draw.textbbox((0, 0), price_change_text, font=font_medium)
        price_change_width = price_change_bbox[2] - price_change_bbox[0]
        y_change_top = y_price_top + price_bbox[3] - price_bbox[1] + field_spacing
        draw.text((x_right_change - price_change_width // 2, y_change_top), price_change_text, fill=change_color, font=font_medium)

    # Display updated image in Streamlit app
    st.image(image, caption="Updated Action Card", use_container_width=True)
