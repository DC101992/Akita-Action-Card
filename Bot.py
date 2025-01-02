import discord
import os

# Ensure intents are configured properly
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Simplified event when the bot is ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Ensure you keep your Discord Bot Token secure, either via .env or an environment variable
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN')

# Running the bot
client.run(DISCORD_BOT_TOKEN)
