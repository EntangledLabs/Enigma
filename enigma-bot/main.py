import discord
from dotenv import load_dotenv

from bot.util import EnigmaClient

# Create the discord bot
bot = EnigmaClient()

# Discord bot run method
async def bot_run():
    try:
        await bot.start(discord_api_key)
    except KeyboardInterrupt:
        await bot.close()