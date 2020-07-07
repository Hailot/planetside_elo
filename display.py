import asyncio
import random
import discord
import mysql.connector
from discord.utils import get
from discord.ext import commands
from decouple import config

from faction import *
from lobby import *
from teams import *


def lobby_list():
    team_embed = discord.Embed(
        description="\n".join(lobby),
        colour=discord.Color.orange()
    )
    team_embed.set_author(name=f'Lobby: {len(lobby)} / 12')
    return team_embed


def match_list():
    team_embed = discord.Embed(
        colour=discord.Color.orange()
    )
    team_embed.add_field(name="Team 1",
                         value=f"Captain: \n {get_captains()[0]} ({get_faction_team()[0]})\n Players:" + "\n".join(
                             get_roster()[0]),
                         inline=True)
    team_embed.add_field(name="Team 2",
                         value=f"Captain: \n {get_captains()[1]} ({get_faction_team()[1]})\n Players:" + "\n".join(
                             get_roster()[1]),
                         inline=True)
    team_embed.add_field(name="Remaining", value="Players:" + "\n".join(roster), inline=True)
    return team_embed


def account_info():
    embed = discord.Embed(
        colour=discord.Color.orange(),
        title='Jaeger Account Info:',
        description=f'**MUST READ: [Rules](https://planetsideguide.com/other/jaeger/)**\n'
                    f'Username: ``\n '
                    f'Password: ``',
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/703912354269888572/727931056476389396/PIL_Logo11_Zoomed.png")
    embed.set_footer(
        text='Failure to follow these rules can result in your suspension of __**ALL**__ Jaeger events.')
