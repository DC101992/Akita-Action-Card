import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN')
APPLICATION_ID = "1325141241356095591"  # Your application ID

# Channel IDs for the allowed channels
TARGET_CHANNEL_IDS = [971568747859046420, 904883897224032256]  # Replace with the actual channel IDs

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents, application_id=APPLICATION_ID)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

# Register Slash Command
@bot.slash_command(name="action_card", description="Displays the action card for Akita Dashboard")
async def action_card(ctx):
    if ctx.channel.id in TARGET_CHANNEL_IDS:
        # This will only respond if the command was triggered in the specified channels
        await ctx.respond("Here's the Action Card for Akita Dashboard!")
    else:
        # If the command was issued outside the target channels, do nothing or send a message
        await ctx.respond("This command can only be used in the designated channels.")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
