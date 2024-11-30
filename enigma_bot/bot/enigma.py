import discord
from discord.ext import commands

from bot import log
from bot.settings import guild_id

class EnigmaClient(commands.Bot):

    def __init__(self):
        self.intents = discord.Intents.default()
        self.intents.members = True
        self.intents.message_content = True
        self.command_prefix='!'

    async def on_ready(self):
        guild = discord.utils.get(self.guilds, id=guild_id)
        log.info(f'{self.user} has connected to {guild.name}')
        print(guild.members)
        print(guild.owner)
        print(guild.roles)
        print(guild.channels)
        print(guild.categories)
        members = '\n - '.join([member.name for member in guild.members])
        log.info(f'Guild Members:\n - {members}')

    # Channels and categories