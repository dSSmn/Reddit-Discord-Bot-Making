import discord

from discord.ext import commands

class Management():

    def __init__(self, bot):
        self.bot = bot

        self.apps = bot.apps

    @commands.command(no_pm=True, pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def appremove(self, ctx, user : discord.Member):
        """Removes a specified user from the app database."""

        author = ctx.message.author
        server = ctx.message.server

        all_users = self.apps.get('users', {})
        server_users = all_users.get(server.id, {})

        if user.id not in server_users:
            await self.bot.send_message(author, 'That user is not in the database.')
            await self.bot.add_reaction(ctx.message, '❌')
            return

        del server_users[user.id]

        all_users[server.id] = server_users
        await self.apps.put('users', all_users)

        await self.bot.add_reaction(ctx.message, '✅') # Command ran to completion. Yay!


def setup(bot):
    bot.add_cog(Management(bot))
