import discord
import os

from discord.ext import commands
from random import choice

# Usage: Enter the command to have the bot send a random message from the specified text file.
# If there is anything after the command (in the same message), the bot will send the message as text-to-speech.

bot_prefix = '!' # Change this to be whatever you want the prefix for your bot to be.
command_name = 'print_line' # Change this to be whatever you want the name of the command to be.
txt_file_name = 'lines.txt' # Change this to the name of your text file.
description = 'This is a Discord bot for /u/the-parapper that says random lines from a text file.' # Change this for a custom description.

# Do not edit below here unless you know what you are doing!

bot = commands.Bot(command_prefix=bot_prefix, description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print('Name: {}'.format(bot.user.name))
    print('ID: {}'.format(bot.user.name))
    print('-----')



@bot.command(name=command_name, pass_context=True)
async def prnt_line(ctx, tts=None):
    lines = read_file(txt_file_name)

    if tts:

        try:
            await bot.send_message(ctx.message.channel, content=choice(lines), tts=True)
        except:
            pass # Couldn't send TTS message.

        return

    try:
        await bot.send_message(ctx.message.channel, content=choice(lines))
    except:
        pass # Couldn't send message.


def read_file(file_name):
    dirpath = os.path.dirname(__file__)
    filename = os.path.join(dirpath, file_name)

    lines = []
    with open(filename) as fp:
        for line in fp:
            lines.append(line)

    return lines

bot.run('enter your token here')
