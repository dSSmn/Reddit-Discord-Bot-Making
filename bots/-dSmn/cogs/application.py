import validators
import discord
import aiohttp
import json

from discord.ext import commands

class Application():

    def __init__(self, bot):
        self.bot = bot

        self.apps = bot.apps
        self.session = bot.session
        self.steam_api_key = bot.steam_api_key
        self.game_id = bot.game_id


    @commands.command(name='apply', pass_context=True)
    async def c_apply(self, ctx, steamprofile : str, age : int, *, timezone : str):
        """Make an application that will be stored."""

        author = ctx.message.author
        server = ctx.message.server

        all_users = self.apps.get('users', {})
        server_users = all_users.get(server.id, {})

        if author.id in server_users:
            await self.bot.send_message(author, 'You are already in the database!')
            await self.bot.add_reaction(ctx.message, '❌')
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

        response = await self.api_call('ISteamUser', 'ResolveVanityURL', 'v0001', vanityurl=sid)
        try:
            sid = response['steamid']
        except:
            await self.bot.send_message(author, 'Steam profile not valid.') # Handle invalid Steam IDs.
            await self.bot.add_reaction(ctx.message, '❌')
            return



        user_data = server_users.get(author.id, {})
        user_data['vanityname'] = sid_old
        user_data['steamid'] = sid
        user_data['age'] = age
        user_data['timezone'] = timezone

        server_users[author.id] = user_data
        all_users[server.id] = server_users
        await self.apps.put('users', all_users)

        await self.bot.add_reaction(ctx.message, '✅') # Command ran to completion. Yay!



    @commands.command(name='view', pass_context=True)
    async def c_view(self, ctx, user : discord.Member=None):
        """View the application for a specified user.

        If no user is specified, your own application will be shown."""

        server = ctx.message.server
        author = ctx.message.author

        if not user:
            user = ctx.message.author

        all_users = self.apps.get('users', {})
        server_users = all_users.get(ctx.message.server.id, {})

        if user.id not in server_users:
            await self.bot.send_message(author, 'You/that user is not in the database.')
            await self.bot.add_reaction(ctx.message, '❌')
            return

        user_data = server_users.get(user.id, {})
        if not user.avatar_url:
            a_url = user.default_avatar_url
        else:
            a_url = user.avatar_url
        steam_url = 'https://www.steamcommunity.com/id/' + user_data['vanityname']

        total_games = await self.api_call('IPlayerService', 'GetOwnedGames', 'v0001', userid=user_data['steamid'])
        total_games = total_games['games']
        for game in total_games:
            if game['appid'] == self.game_id:
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

        steam_profile = await self.api_call('ISteamUser', 'GetPlayerSummaries', 'v0002', userids=user_data['steamid'])
        steam_profile = steam_profile['players'][0]

        embed.add_field(name='Steam Name', value=steam_profile['personaname'])
        try:
            embed.set_thumbnail(url=steam_profile['avatarmedium'])
        except:
            pass
        try:
            if steam_profile['gameid'] == str(self.game_id):
                embed.colour = 0x1BE118
            else:
                embed.colour = 0xe04545
        except KeyError:
            embed.colour = 0xe04545

        embed.add_field(name='Age', value=user_data['age'], inline=False)
        embed.add_field(name='Timezone', value=user_data['timezone'], inline=False)
        embed.title = 'User Info'

        await self.bot.add_reaction(ctx.message, '✅') # Command ran to completion. Yay!
        await self.bot.send_message(author, embed=embed)


    @commands.command(no_pm=True, pass_context=True)
    async def removeme(self, ctx):
        """Removes the command user from the app database."""

        author = ctx.message.author
        server = ctx.message.server

        all_users = self.apps.get('users', {})
        server_users = all_users.get(server.id, {})

        if author.id not in server_users:
            await self.bot.send_message(author, 'You are not in the database.')
            await self.bot.add_reaction(ctx.message, '❌')
            return

        del server_users[author.id]

        all_users[server.id] = server_users
        await self.apps.put('users', all_users)

        await self.bot.add_reaction(ctx.message, '✅') # Command ran to completion. Yay!



    async def api_call(self, service, call, version, userid=None, vanityurl=None, userids=None):
        base_url = f"http://api.steampowered.com/{service}/{call}/{version}/?key={self.steam_api_key}"
        if userid:
            base_url += f'&steamid={userid}'
        if vanityurl:
            base_url += f'&vanityurl={vanityurl}'
        if userids:
            base_url += f'&steamids={userids}'

        async with self.session.get(base_url) as rawdata:
            response_obj = await rawdata.json()

            if len(response_obj.keys()) == 1 and 'response' in response_obj:
                return response_obj['response']
            else:
                return response_obj

def setup(bot):
    bot.add_cog(Application(bot))
