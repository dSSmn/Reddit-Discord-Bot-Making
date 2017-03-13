import validators
import discord
import aiohttp
import json

from discord.ext import commands
from .utils import checks

class Admin():

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_messages=True)
    async def bingo(self, ctx):
        await self.bot.add_reaction(ctx.message, '🇧')
        await self.bot.add_reaction(ctx.message, '🇮')
        await self.bot.add_reaction(ctx.message, '🇳')
        await self.bot.add_reaction(ctx.message, '🇬')
        await self.bot.add_reaction(ctx.message, '🇴')
        await self.bot.add_reaction(ctx.message, '❕')

    @commands.command(name='reload', hidden=True, pass_context=True)
    @checks.is_owner()
    async def _reload(self, ctx, *, extension_name : str):
        """Reloads an extension."""
        if extension_name == "all":
            for cog in list(self.bot.cogs.keys()):
                try:
                    cog = "cogs." + cog.lower()
                    self.bot.unload_extension(cog)
                    self.bot.load_extension(cog)
                except (AttributeError, ImportError) as e:
                    await ctx.channel.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return
        try:
            self.bot.unload_extension(extension_name)
            self.bot.load_extension(extension_name)
        except ImportError:
            await ctx.channel.send("Cog not found.")
            return

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def load(self, ctx, *, extension_name : str):
        """Loads an extension."""
        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            await ctx.channel.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
            return

    @commands.command(hidden=True, pass_context=True)
    @checks.is_owner()
    async def unload(self, ctx, *, extension_name : str):
        """Unloads an extension."""
        self.bot.unload_extension(extension_name)

    @commands.command(hidden=True, name='logout')
    @checks.is_owner()
    async def _logout(self):
        """Turns off the bot."""
        await self.bot.logout()

def setup(bot):
    bot.add_cog(Admin(bot))
