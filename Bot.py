import os
import nextcord  # Changed from discord to nextcord
from nextcord.ext import commands  # Updated to match nextcord's library
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN')
APPLICATION_ID = "1325141241356095591"  # Your application ID

intents = nextcord.Intents.default()  # Changed to nextcord's Intents
bot = commands.Bot(command_prefix="/", intents=intents, application_id=APPLICATION_ID)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

# Register Slash Command
@bot.slash_command(name="action_card", description="Displays the action card for Akita Dashboard")
async def action_card(ctx):
    await ctx.respond("Here's the Action Card for Akita Dashboard!")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
