from os import getenv

import discord
from dotenv import load_dotenv

from bot.util import EnigmaClient

load_dotenv(override=True)

# Create the discord bot
bot = EnigmaClient()

if __name__ == '__main__':
    try:
        bot.run(getenv("DISCORD_API_KEY"))
    except KeyboardInterrupt:
        bot.close()