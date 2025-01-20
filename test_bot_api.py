import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = "https://free-api.vestige.fi/asset/523683256/prices/simple/1D"

# Test Discord Bot Token
if not DISCORD_BOT_TOKEN:
    raise ValueError("Bot token not found. Ensure your .env file contains the correct token.")
else:
    print("Discord Bot Token loaded successfully.")

# Test API Connection
try:
    response = requests.get(API_URL, timeout=10)  # Set timeout for safety
    response.raise_for_status()  # Raise error for bad HTTP responses
    price_data = response.json()
    print(f"API Connection Successful. Data Received:\n{price_data[:5]}")  # Display the first 5 records for brevity
except Exception as e:
    print(f"Error connecting to API: {e}")
