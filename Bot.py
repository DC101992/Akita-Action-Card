import os
import nextcord  # Changed from discord to nextcord
from nextcord.ext import commands  # Updated to match nextcord's library
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve the bot token
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
APPLICATION_ID = "1325141241356095591"  # Your application ID

# Verify token retrieval
if not DISCORD_BOT_TOKEN or DISCORD_BOT_TOKEN == 'YOUR_BOT_TOKEN':
    raise ValueError("Bot token not found. Ensure your .env file contains the correct token.")

# Set up intents and the bot instance
intents = nextcord.Intents.default()  # Updated to nextcord's Intents
bot = commands.Bot(command_prefix="/", intents=intents, application_id=APPLICATION_ID)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

# Register a slash command
@bot.slash_command(name="action_card", description="Displays the action card for Akita Dashboard")
async def action_card(ctx):
    await ctx.respond("Here's the Action Card for Akita Dashboard!")

# Debugging token loading (optional)
print(f"Debug: Token loaded successfully with length {len(DISCORD_BOT_TOKEN)} characters.")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
