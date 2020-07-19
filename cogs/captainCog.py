import os
import discord
import mysql.connector
from discord.ext import commands
from discord.utils import get
from decouple import config

from captains import *
from display import *
from maps import *
from match import *
from OpenLeague import *
import mariadb
import sys
from submit import *

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user='root',
        password='pugs1337',
        host='db',
        database="planetside_data"
    )
    print('Captain Cog connected to MariaDB database')
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
myCursor = conn.cursor()


class CaptainCog(commands.Cog):
    """
    A class used to contain all of the captain commands

    Methods
    -------
    on_ready(self)
        Prints that the cog is running on startup
    """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Captain Cog is online')

    """
    Team-Captain Commands:

    !account
    !faction
    !ban
    !pick
    # !auto_pick
    # !players
    !submit
    """

    @commands.command()  # !account
    @commands.guild_only()
    async def account(self, ctx):
        if ctx.author.id in captains:
            await ctx.channel.send(
                'Accounts sent out. Please check your Discord DM\'s for each account and the rules surrounding them.')
            for player in players:
                myCursor.execute(f"SELECT * FROM `planetside_users` WHERE `discord` = {player[2:-1]}")
                info = myCursor.fetchone()
                if info[4] is None:
                    user = await self.client.fetch_user(player[2:-1])
                    await user.send(embed=account_info)
        else:
            await ctx.channel.send('You have to be picking player to use this command!')

    @commands.command()  # !faction [VS/NC/TR]
    @commands.guild_only()
    async def faction(self, ctx):
        if ctx.author.id == team_pick_captain:
            if len(factions_team) == 2:
                await ctx.channel.send(
                    f'{ctx.author.mention}, you have already picked a faction! Please pick a player instead.')
            elif not ctx.message.content[9:] in get_faction():
                await ctx.channel.send(
                    f'{ctx.author.mention} {ctx.message.content[9:]} is not a valid faction. Choose either ' + ", ".join(
                        get_faction()))
            else:
                set_faction_team(ctx.message.content[9:], captains.index(ctx.author.mention))
                pick_switch()
                await ctx.channel.send(f'{ctx.author.mention} picked {ctx.message.content[9:]}!')
        else:
            await ctx.channel.send(f'{ctx.author.mention} it is not your turn to pick!')

    @commands.command()  # !pick [@member]
    @commands.guild_only()
    async def pick(self, ctx, member: discord.Member):
        if ctx.author.id == team_pick_captain:
            if len(factions_team) != 2:
                await ctx.channel.send(f'{ctx.author.mention} please pick your faction first')
            # elif len(map_match) != 1:
            #     await ctx.channel.send(f'{ctx.author.mention} please ban a map from the pool first')
            elif member.mention not in roster:
                await ctx.channel.send(f'{ctx.author.mention}, you cannot pick {member.mention}')
            else:
                add_roster(member.mention, captains.index(ctx.author.mention))
                pick_switch()
                await ctx.channel.send(f'{ctx.author.mention} picked {member.mention}!')
                await ctx.channel.send(embed=match_list())
        else:
            await ctx.channel.send(f'{ctx.author.mention} it is not your turn to pick!')
        if not roster:
            await set_match_leader(ctx)
            await ctx.channel.send('Teams and factions are picked, prepare to play!')

    @commands.command()  # !submit [matchID]
    @commands.guild_only()
    async def submit(self, ctx):
        match_keep = get(ctx.author.roles, name="Match Leader")
        if match_keep:
            s = ctx.message.content.split(' ')
            match_score = int(s[1])
            submit(match_score)
            await ctx.author.remove_roles(match_keep)
            await ctx.channel.send(f'Thank you for submitting your match results {ctx.author.mention}.')
        else:
            await ctx.channel.send(f'{ctx.author.mention}, only the Match Leader can submit the results of a match.')


def setup(client):
    client.add_cog(CaptainCog(client))
