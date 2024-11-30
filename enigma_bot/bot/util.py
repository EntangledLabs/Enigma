import discord
from discord.ext import commands

class EnigmaClient(discord.Client):
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        pass

    async def on_message(self, message):
        pass