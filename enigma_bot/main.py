from os import getenv
from io import TextIOWrapper, BytesIO
import asyncio
import csv, re

import discord
from discord.ext import commands

from enigma_requests import Settings, Team, Box, ParableUser

from bot import log
from bot.settings import guild_id
from bot.util import create_pw

###############
# TODO: Add "discord event" creation
# TODO: Add team creds






# Create the discord bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!enigma ', intents=intents)

###################################
# Bot client events
@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, id=guild_id)
    log.info(f'{bot.user} has connected to {guild.name}')
    members = '\n - '.join([member.name for member in guild.members])
    log.info(f'Guild Members:\n - {members}')

###################################
# Bot commands

# Admin only, comp creation
@bot.command(pass_context=True)
@commands.check_any(commands.has_role("Green Team"), 
                    commands.has_role("Director"), 
                    commands.has_guild_permissions(administrator=True))
async def init(ctx: commands.context.Context):
    log.info('Command \'init\' invoked. Creating channels and roles')
    await ctx.send('Command \'init\' invoked. Creating channels and roles')
    guild = discord.utils.get(bot.guilds, id=guild_id)
    comp_name = Settings.get().comp_name

    gt_role = discord.utils.get(guild.roles, name='Green Team')
    rt_role = discord.utils.get(guild.roles, name='Red Team')
    director_role = discord.utils.get(guild.roles, name='Director')

    if gt_role is None:
        await guild.create_role(name='Green Team', color=discord.Color.green())
    if rt_role is None:
        await guild.create_role(name='Red Team', color=discord.Color.red())
    if director_role is None:
        await guild.create_role(name='Director', permissions=discord.Permissions().all(), color=discord.Color.green())

    gt_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        gt_role: discord.PermissionOverwrite(read_messages=True)
    }

    rt_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        rt_role: discord.PermissionOverwrite(read_messages=True)
    }
    
    for role in guild.roles:
        if (role.name == f'{comp_name.lower().capitalize()} Competitor'
            or role.name == f'{comp_name.lower().capitalize()} Developer'):
            await role.delete()

    comp_role = await guild.create_role(name=f'{comp_name.lower().capitalize()} Competitor', color=discord.Color.purple())

    dev_role = await guild.create_role(name=f'{comp_name.lower().capitalize()} Developer', color=discord.Color.gold())
    dev_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        dev_role: discord.PermissionOverwrite(read_messages=True)
    }

    comp_cat = discord.utils.get(guild.categories, name=comp_name)
    if comp_cat is not None:
        for channel in comp_cat.channels:
            await channel.delete()
        await comp_cat.delete()

    main_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        comp_role: discord.PermissionOverwrite(read_messages=True),
        dev_role: discord.PermissionOverwrite(read_messages=True),
        gt_role: discord.PermissionOverwrite(read_messages=True),
        rt_role: discord.PermissionOverwrite(read_messages=True),
        director_role: discord.PermissionOverwrite(read_messages=True)
    }

    comp_cat = await guild.create_category(name=comp_name, overwrites=main_overwrites)
    await comp_cat.create_text_channel(name='announcements', overwrites=main_overwrites)
    await comp_cat.create_text_channel(name='general', overwrites=main_overwrites)
    await comp_cat.create_text_channel(name='green-team-alert', overwrites=gt_overwrites)
    await comp_cat.create_text_channel(name='dev-general', overwrites=dev_overwrites)
    await comp_cat.create_voice_channel(name='dev-voice', overwrites=dev_overwrites)
    await comp_cat.create_voice_channel(name='general', overwrites=main_overwrites)

    log.info('Finished! Created roles and channels')
    await ctx.send('Finished! Created roles and channels')

@bot.command(pass_context=True)
@commands.check_any(commands.has_role("Green Team"), 
                    commands.has_role("Director"), 
                    commands.has_guild_permissions(administrator=True))
async def teardown(ctx: commands.context.Context):
    log.info('Command \'teardown\' invoked. Tearing down channels and roles')
    await ctx.send('Command \'teardown\' invoked. Tearing down channels and roles')

    guild = discord.utils.get(bot.guilds, id=guild_id)
    comp_name = Settings.get().comp_name

    await delete_teams(ctx)

    await discord.utils.get(guild.roles, name=f'{comp_name.lower().capitalize()} Competitor').delete()
    await discord.utils.get(guild.roles, name=f'{comp_name.lower().capitalize()} Developer').delete()

    comp_cat = discord.utils.get(guild.categories, name=comp_name)
    for channel in comp_cat.channels:
        await channel.delete()
    await comp_cat.delete()

    log.info(f'Finished! Tore down related objects for \'{comp_name}\'')
    await ctx.send(f'Finished! Tore down related objects for \'{comp_name}\'')

@bot.command(pass_context=True)
@commands.check_any(commands.has_role("Green Team"), 
                    commands.has_role("Director"), 
                    commands.has_guild_permissions(administrator=True))
async def create_teams(ctx: commands.context.Context):
    log.info('Command \'create_teams\' invoked. Creating teams')
    await ctx.send('Command \'create_teams\' invoked. Creating teams')
    guild = discord.utils.get(bot.guilds, id=guild_id)
    comp_name = Settings.get().comp_name

    await delete_teams(ctx)

    username_pw_combos = {}

    with TextIOWrapper(BytesIO(await ctx.message.attachments[0].read())) as f:
        csvreader = csv.reader(f)
        identifier = ParableUser.last_identifier() + 1
        for row in csvreader:
            teamname = row.pop(0)

            Team.add(Team(
                name=teamname,
                identifier=identifier,
                score=0
            )).text
            parable_pw = create_pw(length=24)
            ParableUser.add(ParableUser(
                username=teamname,
                identifier=identifier,
                permission_level=2,
                password=parable_pw
            ))

            username_pw_combos.update({
                teamname: parable_pw
            })

            team_role = await guild.create_role(name=f'Team {teamname}')
            team_overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                team_role: discord.PermissionOverwrite(read_messages=True),
                discord.utils.get(guild.roles, name='Green Team'): discord.PermissionOverwrite(read_messages=True)
            }

            team_cat = await guild.create_category(name=f'{comp_name.lower().capitalize()} {teamname}', overwrites=team_overwrites)
            await team_cat.create_text_channel(name='team-chat', overwrites=team_overwrites)
            await team_cat.create_voice_channel(name='team-voice', overwrites=team_overwrites)
            
            for teammate in row:
                member = discord.utils.get(guild.members, name=teammate)
                roles = [
                    team_role,
                    discord.utils.get(guild.roles, name=f'{comp_name.lower().capitalize()} Competitor')
                ]
                for role in roles:
                    await member.add_roles(role)

            identifier = identifier + 1
    """except:
        log.info('No CSV provided! Cannot create teams')
        await ctx.send('No CSV provided! Cannot create teams')
        return"""

    log.info('Finished! Created teams')
    await ctx.send('Finished! Created teams')

@bot.command(pass_context=True)
@commands.check_any(commands.has_role("Green Team"), 
                    commands.has_role("Director"), 
                    commands.has_guild_permissions(administrator=True))
async def delete_teams(ctx: commands.context.Context):
    log.info('Command \'delete_teams\' invoked. Deleting teams')
    await ctx.send('Command \'delete_teams\' invoked. Deleting teams')
    guild = discord.utils.get(bot.guilds, id=guild_id)
    comp_name = Settings.get().comp_name

    competitor_role_re = re.compile(r'^Team\s[a-zA-Z0-9]+$')
    competitor_cat_re = re.compile(fr'^{comp_name.lower().capitalize()}\s[a-zA-Z0-9]+$')

    for role in guild.roles:
        if competitor_role_re.match(role.name) is not None:
            await role.delete()

    for category in guild.categories:
        if competitor_cat_re.match(category.name):
            for channel in category.channels:
                await channel.delete()
            await category.delete()

    db_teams = Team.list()
    for team in db_teams:
        Team.delete(team.identifier)
        ParableUser.delete(team.name)

    log.info('Finished! Deleted teams')
    await ctx.send('Finished! Deleted teams')


# Green team support commands
@bot.command(pass_context=True)
@commands.check_any(commands.has_role(f'{Settings.get().comp_name.lower().capitalize()} Competitor'),
                    commands.has_role("Green Team"), 
                    commands.has_role("Director"), 
                    commands.has_guild_permissions(administrator=True))
async def request(ctx: commands.context.Context, *args):
    log.info('Command \'request\' invoked. Someone has a GT request.')
    guild = discord.utils.get(bot.guilds, id=guild_id)
    gt_alert_channel = discord.utils.get(guild.text_channels, name='green-team-alert')
    competitor_role_re = re.compile(r'^Team\s[a-zA-Z0-9]+$')
    for role in ctx.author.roles:
        if competitor_role_re.match(role.name):
            comp_role = role.name
    if comp_role is None:
        comp_role = ctx.author.name

    if args[0] == 'support':
        await gt_alert_channel.send(f'Support request for **{comp_role}**!')
        await ctx.send('Support request sent! A Green Team member will be with you ASAP')
    
    elif args[0] == 'reset':
        box_names = [box.name for box in Box.list()]
        if args[1] not in box_names:
            await ctx.send(f'The box you specified, **{args[1]}**, does not exist!')
        else:
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            await ctx.send(f'Please confirm that you want to request a box reset for **{args[1]}**! This CANNOT be undone. (y/n)')
            
            try:
                response = await bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send('Timeout! Request expired, please run the command again')
            
            if response.content.lower() in ('yes', 'y'):
                await ctx.send('Box reset request sent! Please hang tight.')
                await gt_alert_channel.send(f'Box reset request! **{comp_role}** would like a reset on **{args[1]}**')
            else:
                await ctx.send('Box reset request cancelled!')

if __name__ == '__main__':
    bot.run(getenv("DISCORD_API_KEY"), log_handler=None)