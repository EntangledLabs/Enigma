from os import getenv, getcwd
from os.path import join
from io import TextIOWrapper, BytesIO, StringIO
import asyncio
from datetime import datetime
import csv, re

from dotenv import load_dotenv

import discord
from discord.ext import commands

from praxos.logger import log, write_log_header
from praxos.models.settings import Settings
from praxos.models.team import RvBTeam
from praxos.models.box import Box
from praxos.models.user import ParableUser

###############
# TODO: Add "praxos event" creation
# TODO: Add team creds

load_dotenv(override=True)

logs_path = join(getcwd(), 'logs')
log_file = join(logs_path, 'praxos.log')

guild_id = int(getenv('DISCORD_GUILD_ID'))

# Create the praxos bot
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
    log.debug(f'Guild Members:\n - {members}')

    log.info("Praxos is ready!")

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
    comp_name = Settings.get_setting('comp_name')

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
        if (role.name == f'{comp_name} Competitor'
            or role.name == f'{comp_name} Developer'):
            await role.delete()

    comp_role = await guild.create_role(name=f'{comp_name} Competitor', color=discord.Color.purple())

    dev_role = await guild.create_role(name=f'{comp_name} Developer', color=discord.Color.gold())
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

    announcement_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        gt_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        rt_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        director_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    comp_cat = await guild.create_category(name=comp_name, overwrites=main_overwrites)
    await comp_cat.create_text_channel(name='announcements', overwrites=announcement_overwrites)
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
    comp_name = Settings.get_setting('comp_name')

    await delete_teams(ctx)

    await discord.utils.get(guild.roles, name=f'{comp_name} Competitor').delete()
    await discord.utils.get(guild.roles, name=f'{comp_name} Developer').delete()

    comp_cat = discord.utils.get(guild.categories, name=comp_name)

    for channel in comp_cat.channels:
        await channel.delete()
    await comp_cat.delete()

    log.info(f'Finished! Tore down related objects for **\'{comp_name}\'**')
    await ctx.send(f'Finished! Tore down related objects for **\'{comp_name}\'**')

@bot.command(pass_context=True)
@commands.check_any(commands.has_role("Green Team"), 
                    commands.has_role("Director"), 
                    commands.has_guild_permissions(administrator=True))
async def create_teams(ctx: commands.context.Context):
    log.info('Command \'create_teams\' invoked. Creating teams')
    await ctx.send('Command \'create_teams\' invoked. Creating teams')
    guild = discord.utils.get(bot.guilds, id=guild_id)
    comp_name = Settings.get_setting('comp_name')

    await delete_teams(ctx)
    username_pw_combos = {}

    with TextIOWrapper(BytesIO(await ctx.message.attachments[0].read())) as f:
        csvreader = csv.reader(f)
        identifier = ParableUser.last_identifier() + 1

        for row in csvreader:
            teamname = row.pop(0)

            user = ParableUser(
                username=teamname,
                identifier=identifier,
                permission_level=2
            )
            parable_pw = user.create_pw(24)
            user.add_to_db()

            RvBTeam(
                name=teamname,
                identifier=identifier,
                score=0
            ).add_to_db()

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

            team_cat = await guild.create_category(name=f'{comp_name} {teamname}', overwrites=team_overwrites)
            await team_cat.create_text_channel(name='team-chat', overwrites=team_overwrites)
            await team_cat.create_voice_channel(name='team-voice', overwrites=team_overwrites)

            for teammate in row:
                member = discord.utils.get(guild.members, name=teammate)
                roles = [
                    team_role,
                    discord.utils.get(guild.roles, name=f'{comp_name} Competitor')
                ]
                for role in roles:
                    await member.add_roles(role)

            await team_cat.text_channels[0].send(f'{team_role.mention} Welcome to {comp_name}! Your Parable login is **{teamname}** with password **{parable_pw}**')

            identifier = identifier + 1

    csvfile = StringIO()
    fieldnames = ['team', 'password']


    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    for team, password in username_pw_combos.items():
        writer.writerow({'team': team, 'password': password})
    csvfile.seek(0)

    buffer = BytesIO()
    buffer.write(csvfile.getvalue().encode('utf-8'))
    buffer.seek(0)
    buffer.name = 'users.csv'

    log.info('Finished! Created teams')
    await ctx.send('Finished! Created teams', file=discord.File(buffer))

@bot.command(pass_context=True)
@commands.check_any(commands.has_role("Green Team"), 
                    commands.has_role("Director"), 
                    commands.has_guild_permissions(administrator=True))
async def delete_teams(ctx: commands.context.Context):
    log.info('Command \'delete_teams\' invoked. Deleting teams')
    await ctx.send('Command \'delete_teams\' invoked. Deleting teams')
    guild = discord.utils.get(bot.guilds, id=guild_id)
    comp_name = Settings.get_setting('comp_name')

    competitor_role_re = re.compile(r'^Team\s[a-zA-Z0-9]+$')
    competitor_cat_re = re.compile(fr'^{comp_name}\s[a-zA-Z0-9]+$')

    log.debug("Removing team roles")
    for role in guild.roles:
        if competitor_role_re.match(role.name) is not None:
            await role.delete()

    log.debug("Removing team categories and channels")
    for category in guild.categories:
        if competitor_cat_re.match(category.name):
            for channel in category.channels:
                await channel.delete()
            await category.delete()

    log.debug("Deleting teams")
    db_teams = RvBTeam.find_all()
    for team in db_teams:
        team.remove_from_db()

    log.debug("Deleting users")
    db_users = ParableUser.find_all()
    for user in db_users:
        user.remove_from_db()

    log.info('Finished! Deleted teams')
    await ctx.send('Finished! Deleted teams')


# Green team support commands
@bot.command(pass_context=True)
@commands.check_any(commands.has_role(f'{Settings.get_setting('comp_name')} Competitor'),
                    commands.has_role("Green Team"), 
                    commands.has_role("Director"), 
                    commands.has_guild_permissions(administrator=True))
async def request(ctx: commands.context.Context, *args):
    log.info('Command \'request\' invoked. Someone has a GT request.')
    guild = discord.utils.get(bot.guilds, id=guild_id)
    gt_alert_channel = discord.utils.get(guild.text_channels, name='green-team-alert')
    gt_role = discord.utils.get(guild.roles, name='Green Team')
    competitor_role_re = re.compile(r'^Team\s[a-zA-Z0-9]+$')
    for role in ctx.author.roles:
        if competitor_role_re.match(role.name):
            comp_role = role.name

    if comp_role is None:
        comp_role = ctx.author.name

    if args[0] == 'support':
        await gt_alert_channel.send(f'{gt_role.mention} Support request for **{comp_role}**! -> {ctx.channel.mention}')
        await ctx.send('Support request sent! A Green Team member will be with you ASAP')
    
    elif args[0] == 'reset':
        box_names = [box.name for box in Box.find_all()]
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
                return
            
            if response.content.lower() in ('yes', 'y'):
                await ctx.send('Box reset request sent! Please hang tight.')
                await gt_alert_channel.send(f'{gt_role.mention} Box reset request! **{comp_role}** would like a reset on **{args[1]}**')
            else:
                await ctx.send('Box reset request cancelled!')

if __name__ == '__main__':
    write_log_header()

    log.info("Welcome to Praxos discord bot for Enigma Scoring Engine!")
    log.info("Entangled was still in pain while making this")

    bot.run(getenv("DISCORD_API_KEY"), log_handler=None)