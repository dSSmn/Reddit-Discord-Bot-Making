# Usage: !help [command]

bot_prefix = '!' # Change this to be whatever you want the prefix for your bot to be.
description = 'This is a Discord bot for /u/-dSmn that is used for storing Steam user data.' # Change this for a custom description.
game_id = 252490 # This is the id of the game that we will search statistics for. Currently set to Rust.
owner_id = 'user id here' # How to get User ID: https://github.com/TheTrain2000/Discord-Bot/wiki/Obtaining-Your-User-ID

bot_token = 'bot token here' # Put your Discord bot token here. Obtain one here: https://discordapp.com/developers/applications/me
steam_api_key = 'steam api key here' # Put your Steam API key here. Obtain one here: http://steamcommunity.com/dev/apikey

# Do not edit below here unless you know what you are doing!

import traceback
import discord
import aiohttp
import sys
import os

from discord.ext import commands
from cogs.utils import config

startup_cogs = [
    'cogs.admin',
    'cogs.application',
    'cogs.management'
]

app_path = os.path.dirname(os.path.abspath(sys.argv[0]))
users = os.path.join(app_path, 'users.json')
ratings = os.path.join(app_path, 'ratings.json')

bot = commands.Bot(command_prefix=bot_prefix, description=description)

bot.apps = config.Config(users)
bot.ratings = config.Config(ratings)
bot.steam_api_key = steam_api_key
bot.game_id = game_id
bot.owner_id = owner_id

bot.session = aiohttp.ClientSession(loop=bot.loop)

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
        await bot.add_reaction(ctx.message, '❌')
        await bot.send_message(ctx.message.author, 'Permission denied.')
    else:
        tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        print(tb)

if __name__ == "__main__":
    for extension in startup_cogs:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            log.info(f'Failed to load extension {extension}\n{exc}')

    bot.run(bot_token)
