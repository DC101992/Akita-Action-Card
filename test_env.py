import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Print the values to verify they're loaded correctly
print("DISCORD_BOT_TOKEN:", os.getenv("DISCORD_BOT_TOKEN"))
print("TWITTER_API_KEY:", os.getenv("TWITTER_API_KEY"))
print("TWITTER_ACCESS_TOKEN:", os.getenv("TWITTER_ACCESS_TOKEN"))
print("FLASK_SECRET_KEY:", os.getenv("FLASK_SECRET_KEY"))
