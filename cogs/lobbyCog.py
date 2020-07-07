import os
import discord
from discord.ext import commands
from discord.utils import get
from decouple import config
from display import *
from lobby import *
from maps import *


class LobbyCog(commands.Cog):
    """
    A class used to contain all of the general lobby commands

    Methods
    -------
    on_ready(self)
        Prints that the cog is running on startup
    """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Lobby Cog is online')

    """
    Registered Commands:

    !join
    !leave
    !queue
    !match
    !maps
    """

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx):
        if ctx.author.mention in lobby:
            await ctx.channel.send("You're already queued for a match!")
        else:
            add_lobby(ctx.author.mention)
            await ctx.channel.send("You've been added to the queue!")
        await ctx.channel.send(embed=lobby_list())
        if len(lobby) == 12:
            if get_match():
                await ctx.channel.send(
                    "There is currently a match being picked right now, please try again after picking is finished")
            # else:
            #     assign_captains()

    @commands.command()
    @commands.guild_only()
    async def leave(self, ctx):
        if ctx.author.mention in lobby:
            remove_lobby(ctx.author.mention)
            await ctx.channel.send("You've been removed from the queue.")
        else:
            await ctx.channel.send("You're not queued for a match!")
        await ctx.channel.send(embed=lobby_list())

    @commands.command()
    @commands.guild_only()
    async def queue(self, ctx):
        await ctx.channel.send(embed=lobby_list())

    @commands.command()
    @commands.guild_only()
    async def maps(self, ctx):
        await ctx.channel.send('Current Map Pool: \n> ' + "\n> ".join(get_maps()))


def setup(client):
    client.add_cog(LobbyCog(client))
