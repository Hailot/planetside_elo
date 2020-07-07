import asyncio
import random
import discord
import mysql.connector
from discord.utils import get
from discord.ext import commands
from decouple import config

from lobby import *
from maps import *
from match import *
from display import *
from teams import clear_roster
from update import *


class AdminCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Admin Cog is online')

    """
    Admin Commands

    !register
    !clear_queue
    !clear_match
    !map_add
    !map_remove
    !suspend
    """

    @commands.command()  # !register [@member]
    @commands.guild_only()
    async def register(self, ctx, member: discord.Member):
        role = get(ctx.author.roles, name="PIL Pugs Staff")
        if role is not None:
            role = get(member.guild.roles, name="PIL Pugs")
            await member.add_roles(role)
            await member.send("Congrats! You have been approved to use Open League, "
                              "brought to you by Planetside Infantry League.\n"
                              "You should now have access to all of the OL channels")
            await ctx.channel.send(f'{ctx.author.mention} registered {member.mention}!')
        else:
            await ctx.channel.send(f'{ctx.author.mention}, {member.mention} is already registered!')

    @commands.command()  # !clear_queue
    @commands.guild_only()
    async def clear_queue(self, ctx):
        role = get(ctx.author.roles, name="PIL Pugs Staff")
        if role:
            clear_lobby()
            await ctx.channel.send(f'{ctx.author.mention} Lobby cleared!')
            await ctx.channel.send(embed=lobby_list())

    @commands.command()  # !clear_match
    @commands.guild_only()
    async def clear_match(self, ctx):
        role = get(ctx.author.roles, name="PIL Pugs Staff")
        if role:
            clear_roster()
            await ctx.channel.send(f'{ctx.author.mention} Match cleared!')

    @commands.command()  # !map_add
    @commands.guild_only()
    async def map_add(self, ctx):
        role = get(ctx.author.roles, name="PIL Pugs Staff")
        if role:
            add_map(ctx.message.content[9:])
            await ctx.channel.send(f'{ctx.author.mention} Map added!')
            await ctx.channel.send('Current Map Pool: \n> ' + "\n> ".join(get_maps()))

    @commands.command()  # !map_remove
    @commands.guild_only()
    async def map_remove(self, ctx):
        role = get(ctx.author.roles, name="PIL Pugs Staff")
        if role:
            remove_map(ctx.message.content[9:])
            await ctx.channel.send(f'{ctx.author.mention} Map removed.')
            await ctx.channel.send('Current Map Pool: \n> ' + "\n> ".join(get_maps()))

    @commands.command()  # !suspend [@member] [time in minutes] [reasoning]
    @commands.guild_only()
    async def suspend(self, ctx, member: discord.Member):
        role = get(ctx.author.roles, name="PIL Pugs Staff")
        if role:
            s = ctx.message.content.split(' ')
            suspend_time = int(s[2])
            remove(s, s[2])
            remove(s, s[1])
            remove(s, s[0])
            role = get(member.guild.roles, name="PIL Pugs")
            await member.remove_roles(role)
            await member.send(f'You have been temporarily suspended from Open League for:\n'
                              f'> ' + ' '.join(s) + '\n'
                                                    f'You will be able to play again in: **{int(suspend_time / 60)} hour(s) and {suspend_time % 60} minutes**')
            await ctx.channel.send(
                f'{ctx.author.mention} suspended {member.mention} for **{int(suspend_time / 60)} hour(s) and {suspend_time % 60} minutes**!')
            await asyncio.sleep(suspend_time * 60)
            await member.add_roles(role)
            await member.send(f'You now have permission to play Open League again. Play nice!')
            await ctx.channel.send(f'{ctx.author.mention}, {member.mention} has been unsuspended.')


def setup(client):
    client.add_cog(AdminCog(client))
