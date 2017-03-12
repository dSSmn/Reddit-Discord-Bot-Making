# Usage: !help [command]

bot_prefix = '!' # Change this to be whatever you want the prefix for your bot to be.
description = 'This is a Discord bot for /u/-dSmn that is used for storing Steam user data.' # Change this for a custom description.
game_id = 252490 # This is the id of the game that we will search statistics for. Currently set to Rust.

bot_token = 'bot token here' # Put your Discord bot token here. Obtain one here: https://discordapp.com/developers/applications/me
steam_api_key = 'steam api key here' # Put your Steam API key here. Obtain one here: http://steamcommunity.com/dev/apikey

# Do not edit below here unless you know what you are doing!

import validators
import traceback
import discord
import aiohttp
import json
import sys
import os

from discord.ext import commands
from datetime import datetime
from utils import config

app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
users = os.path.join(app_path, 'users.json')
ratings = os.path.join(app_path, 'ratings.json')

users = config.Config(users)
ratings = config.Config(ratings)

bot = commands.Bot(command_prefix=bot_prefix, description=description)

session = aiohttp.ClientSession(loop=bot.loop)

@bot.event
async def on_ready():
    print('Logged in as')
    print('Name: {}'.format(bot.user.name))
    print('ID: {}'.format(bot.user.id))
    print('-----')

@bot.event
async def on_command_error(exc, ctx):
    e = getattr(exc, 'original', exc)
    if isinstance(e, (commands.MissingRequiredArgument, commands.CommandOnCooldown, discord.Forbidden)):
        await bot.send_message(ctx.message.channel, str(e))
    elif isinstance(e, commands.CheckFailure):
        await bot.send_message(ctx.message.channel, 'Permission denied.')
    else:
        tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        print(tb)

@bot.command(name='apply', pass_context=True)
async def c_apply(ctx, steamprofile : str, age : int, *, timezone : str):
    """Make an application that will be stored."""

    author = ctx.message.author
    server = ctx.message.server

    all_users = users.get('users', {})
    server_users = all_users.get(server.id, {})

    if author.id in server_users:
        await bot.send_message(author, 'You are already in the database!')
        return

    if validators.url(steamprofile):
        steamprofile = steamprofile.split('/')

        sid = steamprofile.pop(-1)
        sid_old = sid
        if not sid:
            sid = steamprofile.pop(-2)
            sid_old = sid
    else:
        sid = steamprofile
        sid_old = sid

    response = await api_call('ISteamUser', 'ResolveVanityURL', 'v0001', vanityurl=sid)
    try:
        sid = response['steamid']
    except:
        await bot.send_message(author, 'Steam profile not valid.') # Handle invalid Steam IDs.
        return



    user_data = server_users.get(author.id, {})
    user_data['vanityname'] = sid_old
    user_data['steamid'] = sid
    user_data['age'] = age
    user_data['timezone'] = timezone

    server_users[author.id] = user_data
    all_users[server.id] = server_users
    await users.put('users', all_users)

    await bot.send_message(author, '👍') # Command ran to completion. Yay!



@bot.command(name='view', pass_context=True)
async def c_view(ctx, user : discord.Member=None):
    """View the application for a specified user.

    If no user is specified, your own application will be shown."""

    server = ctx.message.server

    if not user:
        user = ctx.message.author

    all_users = users.get('users', {})
    server_users = all_users.get(ctx.message.server.id, {})

    if user.id not in server_users:
        await bot.send_message(ctx.message.author, 'You/that user is not in the database.')
        return

    user_data = server_users.get(user.id, {})
    if not user.avatar_url:
        a_url = user.default_avatar_url
    else:
        a_url = user.avatar_url
    steam_url = 'https://www.steamcommunity.com/id/' + user_data['vanityname']

    total_games = await api_call('IPlayerService', 'GetOwnedGames', 'v0001', userid=user_data['steamid'])
    total_games = total_games['games']
    for game in total_games:
        if game['appid'] == game_id:
            try:
                total_hours = round(game['playtime_forever']/60, 2)
            except:
                total_hours = 0
            try:
                pasttwoweeks = round(game['playtime_2weeks']/60, 2)
            except:
                pasttwoweeks = 0
            break
    else:
        total_hours = 0
        pasttwoweeks = 0

    embed = discord.Embed()

    embed.set_author(name=user.name, icon_url=a_url, url=steam_url)

    embed.add_field(name='Playtime', value=f'Total Hours: {total_hours} hours\nPast 2 Weeks: {pasttwoweeks} hours')

    steam_profile = await api_call('ISteamUser', 'GetPlayerSummaries', 'v0002', userids=user_data['steamid'])
    steam_profile = steam_profile['players'][0]

    embed.add_field(name='Steam Name', value=steam_profile['personaname'])
    try:
        embed.set_thumbnail(url=steam_profile['avatarmedium'])
    except:
        pass
    try:
        if steam_profile['gameid'] == str(game_id):
            embed.colour = 0x1BE118
        else:
            embed.colour = 0xe04545
    except KeyError:
        embed.colour = 0xe04545

    embed.add_field(name='Age', value=user_data['age'], inline=False)
    embed.add_field(name='Timezone', value=user_data['timezone'], inline=False)
    embed.title = 'User Info'

    await bot.say(embed=embed)


async def api_call(service, call, version, userid=None, vanityurl=None, userids=None):
    base_url = f"http://api.steampowered.com/{service}/{call}/{version}/?key={steam_api_key}"
    if userid:
        base_url += f'&steamid={userid}'
    if vanityurl:
        base_url += f'&vanityurl={vanityurl}'
    if userids:
        base_url += f'&steamids={userids}'

    async with session.get(base_url) as rawdata:
        response_obj = await rawdata.json()

        if len(response_obj.keys()) == 1 and 'response' in response_obj:
            return response_obj['response']
        else:
            return response_obj

bot.run(bot_token)
