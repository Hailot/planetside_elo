import random
import discord
import mysql.connector
from discord.utils import get
from discord.ext import commands
import time

db = mysql.connector.connect(
    host='localhost',
    database='planetside_data',
    user='andrew',
    passwd='2a.x6dR2V+vf@qt'
)
if db.is_connected():
    print('Connected to MySQL database')
    mycursor = db.cursor()

teamSizeMax = 12
lobby = []
roster = []
team1_roster = []
team2_roster = []
team1_captain = ''
team2_captain = ''
team_pick_captain = ''
team1_faction = ''
team2_faction = ''
faction_list = ['VS', 'NC', 'TR']
map_list = [
    'Acan Southern',
    'Chac Fusion Labs',
    'Ghanan Southern',
    'Peris Eastern',
    'Xenotech Labs',
    'Pale Canyon'
]
temp_map_list = map_list.copy()
match_map = ''


def add(group, item):
    group.append(item)


def remove(group, item):
    group.remove(item)


def assign_captains():
    global team1_captain
    global team2_captain
    global roster
    global lobby
    global team_pick_captain
    roster = lobby.copy()
    lobby.clear()
    for player in roster:
        if team1_captain == '':
            team1_captain = player
        elif team2_captain == '':
            team2_captain = player
        else:
            mycursor.execute(f"SELECT * FROM `planetside_users` WHERE `discord` = {team1_captain[2:-1]}")
            team1_captain_score = mycursor.fetchone()
            mycursor.execute(f"SELECT * FROM `planetside_users` WHERE `discord` = {team2_captain[2:-1]}")
            team2_captain_score = mycursor.fetchone()
            mycursor.execute(f"SELECT * FROM `planetside_users` WHERE `discord` = {player[2:-1]}")
            player_score = mycursor.fetchone()
            if player_score[2] > team1_captain_score[2]:
                team1_captain = player
            elif player_score[2] > team2_captain_score[2]:
                team2_captain = player
    remove(roster, team1_captain)
    remove(roster, team2_captain)
    coin = random.randint(1, 2)
    if coin == 1:
        team_pick_captain = team1_captain
    if coin == 2:
        team_pick_captain = team2_captain


def pick_switch():
    global team_pick_captain
    if team_pick_captain == team1_captain:
        team_pick_captain = team2_captain
    elif team_pick_captain == team2_captain:
        team_pick_captain = team1_captain


def lobby_list():
    team_embed = discord.Embed(
        description="\n".join(lobby),
        colour=discord.Color.orange()
    )
    team_embed.set_author(name=f'Lobby: {len(lobby)} / {teamSizeMax}')
    return team_embed


def match_list():
    team_embed = discord.Embed(
        colour=discord.Color.orange()
    )
    team_embed.add_field(name="Team 1", value=f"Captain: \n {team1_captain} ({team1_faction})\n Players:" + "\n".join(team1_roster),
                         inline=True)
    team_embed.add_field(name="Team 2", value=f"Captain: \n {team2_captain} ({team2_faction})\n Players:" + "\n".join(team2_roster),
                         inline=True)
    team_embed.add_field(name="Remaining", value="Players:" + "\n".join(roster), inline=True)
    return team_embed


def reset():
    global faction_list
    global temp_map_list
    faction_list = ['VS', 'NC', 'TR']
    temp_map_list = map_list.copy()


class EloSystem(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online')

    @commands.command()
    async def test(self, ctx):
        await ctx.channel.send(embed=match_list())

    # Registered Commands

    # !join
    # !leave
    # !queue
    # !maps

    @commands.command()
    async def join(self, ctx):
        if lobby.count(f"{ctx.author.mention}") == 0:
            add(lobby, ctx.author.mention)
            await ctx.channel.send("You've been added to the queue!")
        else:
            await ctx.channel.send("You're already queued for a match!")
        await ctx.channel.send(embed=lobby_list())
        if len(lobby) == teamSizeMax:
            if roster:
                await ctx.channel.send("There is currently a match being picked right now, please try again after picking is finished")
            else:
                assign_captains()

    @commands.command()
    async def leave(self, ctx):
        if lobby.count(f"{ctx.author.mention}") == 1:
            remove(lobby, ctx.author.mention)
            await ctx.channel.send("You've been removed from the     queue.")
        else:
            await ctx.channel.send("You're not queued for a match!")
        await ctx.channel.send(embed=lobby_list())

    @commands.command()
    async def queue(self, ctx):
        await ctx.channel.send(embed=lobby_list())

    @commands.command()
    async def maps(self, ctx):
        await ctx.channel.send('Current Map Pool: \n> ' + "\n> ".join(map_list))

    # Team-Captain Commands

    # !faction
    # !ban
    # !pick

    @commands.command()  # !faction [VS/NC/TR]
    async def faction(self, ctx):
        global team1_faction
        global team2_faction
        if ctx.author.id == team_pick_captain:
            if team1_faction and team2_faction:
                await ctx.channel.send(f'{ctx.author.mention}, you have already picked a faction! Please pick a player instead.')
            elif not ctx.message.content[9:] in faction_list:
                await ctx.channel.send(f'{ctx.author.mention} {ctx.message.content[9:]} is not a valid faction. Choose either ' + ", ".join(faction_list))
            else:
                if ctx.author.id == team1_captain:
                    team1_faction = ctx.message.content[9:]
                elif ctx.author.id == team2_captain:
                    team2_faction = ctx.message.content[9:]
                remove(faction_list, ctx.message.content[9:])
                pick_switch()
                await ctx.channel.send(f'{ctx.author.mention} picked {ctx.message.content[9:]}!')
        else:
            await ctx.channel.send(f'{ctx.author.mention} it is not your turn to pick!')

    @commands.command()  # !ban [Map Name]
    async def ban(self, ctx):
        global match_map
        if ctx.author.id == team_pick_captain:
            if not team1_faction or not team2_faction:
                await ctx.channel.send(f'{ctx.author.mention} please pick your faction')
            elif match_map:
                await ctx.channel.send(f'{ctx.author.mention} your map has already been selected ({match_map}), please pick a player')
            else:
                remove(temp_map_list, ctx.message.content[5:])
                pick_switch()
                await ctx.channel.send(f'{ctx.author.mention} banned {ctx.message.content[5:]}!')
                if len(temp_map_list) <= 4:
                    match_map = temp_map_list[random.randint(0, len(temp_map_list) - 1)]
                await ctx.channel.send(f'The map will be {match_map}!')
        else:
            await ctx.channel.send(f'{ctx.author.mention} it is not your turn to pick!')

    @commands.command()  # !pick [@member]
    async def pick(self, ctx, member: discord.Member):
        if ctx.author.id == team_pick_captain:
            if not team1_faction or not team2_faction:
                await ctx.channel.send(f'{ctx.author.mention} please pick your faction first')
            elif not match_map:
                await ctx.channel.send(f'{ctx.author.mention} please ban a map from the pool first')
            else:
                if ctx.author.id == team1_captain:
                    add(team1_roster, member.mention)
                elif ctx.author.id == team2_captain:
                    add(team2_roster, member.mention)
                remove(roster, member.mention)
                pick_switch()
                await ctx.channel.send(f'{ctx.author.mention} picked {member.mention}!')
        else:
            await ctx.channel.send(f'{ctx.author.mention} it is not your turn to pick!')
        if not roster:
            await ctx.channel.send('Teams and factions are picked, prepare to play!')
        await ctx.channel.send(embed=match_list())
        reset()

    # Admin Commands

    # !register
    # !suspend
    # !map_add
    # !map_remove
    # !clear_queue
    # !clear_match

    @commands.command()  # !register [@user]
    @commands.guild_only()
    async def register(self, ctx, member: discord.Member):
        user = ctx.author
        role = get(user.roles, name="Admin")
        if role is not None:
            mycursor.execute(f"INSERT INTO `planetside_users` (`discord`) VALUES({member.id})")
            db.commit()
            await member.send("Congrats! You have been approved to use Open League, "
                              "brought to you by Planetside Infantry League.\n"
                              "You should now have access to all of the OL channels")
            await ctx.channel.send(f'{ctx.author.mention} registered {member.mention}!')

    @commands.command()  # !clear_queue
    @commands.guild_only()
    async def clear_queue(self, ctx):
        global lobby
        user = ctx.author
        role = get(user.roles, name="Admin")
        if role:
            lobby.clear()
            await ctx.channel.send(f'{ctx.author.mention} Lobby cleared!')
            await ctx.channel.send(embed=lobby_list())

    @commands.command()  # !clear_match
    @commands.guild_only()
    async def clear_match(self, ctx):
        global roster
        role = get(ctx.author.roles, name="Admin")
        if role:
            roster.clear()
            reset()
            await ctx.channel.send(f'{ctx.author.mention} Match cleared!')
            await ctx.channel.send(embed=match_list())

    @commands.command()  # !map_add
    @commands.guild_only()
    async def map_add(self, ctx):
        global map_list
        global temp_map_list
        role = get(ctx.author.roles, name="Admin")
        if role:
            add(map_list, ctx.message.content[9:])
            temp_map_list = map_list.copy()
            await ctx.channel.send(f'{ctx.author.mention} Map added!')
            await ctx.channel.send('Current Map Pool: \n> ' + "\n> ".join(map_list))

    @commands.command()  # !map_remove
    @commands.guild_only()
    async def map_remove(self, ctx):
        global map_list
        global temp_map_list
        role = get(ctx.author.roles, name="Admin")
        if role:
            remove(map_list, ctx.message.content[9:])
            temp_map_list = map_list.copy()
            await ctx.channel.send(f'{ctx.author.mention} Map removed.')
            await ctx.channel.send('Current Map Pool: \n> ' + "\n> ".join(map_list))


def setup(client):
    client.add_cog(EloSystem(client))
