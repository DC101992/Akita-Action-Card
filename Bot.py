import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
APPLICATION_ID = '1325141241356095591'  # Your Bot Application ID
PUBLIC_KEY = '316f8e8fc9a48ed82f4b2f9992f6ebebec6760cd42d2dd960451e873ea53c3d9'  # Your Bot Public Key

# Set up bot with commands
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(name="action_card", description="Display the Action Card")
async def action_card(interaction: discord.Interaction):
    await interaction.response.send_message("Here is the action card!", ephemeral=False)

# Run bot
if DISCORD_BOT_TOKEN:
    bot.run(DISCORD_BOT_TOKEN)
else:
    print("Error: Bot token not found!")
