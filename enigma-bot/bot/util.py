import discord
from discord.ext import commands

from engine.scoring import ScoringEngine
from engine import log

class EnigmaClient(discord.Client):
    
    def __init__(self, se: ScoringEngine):
        self.se = se
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        log.info('Initializing Discord bot')

    async def on_message(self, message):
        pass