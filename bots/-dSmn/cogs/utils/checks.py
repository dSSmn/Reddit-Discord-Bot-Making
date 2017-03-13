from discord.ext import commands
import discord.utils

def is_owner_check(ctx):
    return ctx.message.author.id == ctx.bot.owner_id

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx))
