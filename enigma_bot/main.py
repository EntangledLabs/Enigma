from os import getenv

import discord

from bot import log
from bot.enigma import EnigmaClient

# Create the discord bot
bot = EnigmaClient()

if __name__ == '__main__':
    bot.run(getenv("DISCORD_API_KEY"), log_handler=None)