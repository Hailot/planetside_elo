import asyncio
import random
import discord
from discord.utils import get
from discord.ext import commands
from decouple import config

from captains import *
from faction import get_faction, set_faction_team
from lobby import *
from maps import *
from match import *
from display import *
from teams import clear_roster
from update import *
import mariadb
import sys

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user='root',
        password='pugs1337',
        host='db',
        port=3306,
        database="planetside_data"
    )
    print('OpenLeague.py connected to MariaDB database')
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
myCursor = conn.cursor()

team_pick_captain = ''


def assign_captains():
    global team_pick_captain
    set_match()
    for player in roster:
        myCursor.execute(f"SELECT `is_teamcaptain` FROM `planetside_users` WHERE `discord` = {player[2:-1]}")
        captain_option = myCursor.fetchone()
        myCursor.execute(f"SELECT `is_teamcaptain` FROM `planetside_users` WHERE `discord` = {captains[0][2:-1]}")
        captain0_option = myCursor.fetchone()
        myCursor.execute(f"SELECT `is_teamcaptain` FROM `planetside_users` WHERE `discord` = {captains[1][2:-1]}")
        captain1_option = myCursor.fetchone()
        if captain_option == 0:
            pass
        elif not captains[0]:
            captains[0] = player
        elif not captains[1]:
            captains[1] = player
        elif captain_option > captain0_option:
            captains[0] = player
        elif captain_option > captain1_option:
            captains[1] = player
    remove_match(captains[0])
    remove_match(captains[1])
    coin = random.randint(0, 1)
    if coin == 0:
        team_pick_captain = captains[0]
    elif coin == 1:
        team_pick_captain = captains[1]


def pick_switch():
    global team_pick_captain
    if team_pick_captain == captains[0]:
        team_pick_captain = captains[1]
    elif team_pick_captain == captains[1]:
        team_pick_captain = captains[0]


async def set_match_leader(ctx):
    match_keep_role = get(ctx.message.guild.roles, name='Match Leader')
    await ctx.channel.send(f'{ctx.author.mention} has been selected to submit the final match score!')
    await asyncio.sleep(30 * 60)
    await ctx.author.add_roles(match_keep_role)
    await asyncio.sleep(60 * 60)
    match_role_true = get(ctx.author.roles, name='Match Leader')
    if match_role_true:
        await ctx.author.remove_roles(match_keep_role)
        await ctx.channel.send(f'{ctx.author.mention} has forgotten to submit the score of the previous match :(')
