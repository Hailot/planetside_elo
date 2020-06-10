import os

import discord
import mysql.connector
from discord.utils import get
from discord.ext import commands

db = mysql.connector.connect(
    host='localhost',
    database='planetside_data',
    user='andrew',
    passwd='2a.x6dR2V+vf@qt'
)
if db.is_connected():
    print('Connected to MySQL database')

mycursor = db.cursor()
teamSize = 0
teamSizeMax = 12
roster = ''
team1_roster = ''
team2_roster = ''
team1_captain = ' '
team2_captain = ' '
map_list = ''
temp_map_list = ''


def add_to_team_roster(new_player):
    global roster
    roster += new_player


def add_to_team_one_roster(new_player):
    global team1_roster
    team1_roster += new_player


def remove_from_team_roster(new_player):
    global roster
    roster = roster.replace(new_player, '')


def assign_captains():
    mycursor.execute(f"SELECT `score` FROM `planetside_users` WHERE `discord` = {team1_captain}")
    team1_captain_score = mycursor.fetchone()
    mycursor.execute(f"SELECT `score` FROM `planetside_users` WHERE `discord` = {team2_captain}")
    team2_captain_score = mycursor.fetchone()
    mycursor.execute(f"SELECT `score` FROM `planetside_users` WHERE `discord` = {roster}")
    player_score = mycursor.fetchone()
    if player_score[0] > team1_captain_score[0] or team1_captain.isspace():
        global team1_captain
        team1_captain = roster
    elif player_score[0] > team2_captain_score[0] or team2_captain.isspace():
        global team2_captain
        team2_captain = roster


class EloSystem(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online')

    @commands.command()
    async def register(self, message):
        member = message.author
        mycursor.execute(f"SELECT * FROM `planetside_users` WHERE `discord` = {message.author.id}")
        result = mycursor.fetchone()
        role = get(member.guild.roles, name="Registered")
        await member.add_roles(role)
        if result is None:
            await message.channel.send(f'{message.author.mention} You are now registered!')
            mycursor.execute(f"INSERT INTO `planetside_users` (`discord`) VALUES({message.author.id})")
            db.commit()
        else:
            mycursor.execute(f"SELECT score FROM `planetside_users` WHERE `discord` = {message.author.id}")
            result = mycursor.fetchone()
            await message.channel.send(
                f'{message.author.mention} You are already registered!\nYour current score: {result[0]}')

    @commands.command()
    async def win(self, message):
        mycursor.execute(f"SELECT discord, score FROM `planetside_users` WHERE `discord` = {message.author.id}")
        result = mycursor.fetchone()
        exp = int(result[1]) + 10
        mycursor.execute(f"UPDATE `planetside_users` SET `score` = {exp} WHERE `discord` = {message.author.id}")
        db.commit()
        await message.channel.send(f'{message.author.mention} You won! Your score now is {exp}')

    @commands.command()
    async def loss(self, message):
        mycursor.execute(f"SELECT discord, score FROM `planetside_users` WHERE `discord` = {message.author.id}")
        result = mycursor.fetchone()
        exp = int(result[1]) - 10
        if exp < 0:
            exp = 0
        mycursor.execute(f"UPDATE `planetside_users` SET `score` = {exp} WHERE `discord` = {message.author.id}")
        db.commit()
        await message.channel.send(f'{message.author.mention} You lost. Your score now is {exp}')

    @commands.command()
    async def join(self, message):
        global roster
        global teamSize
        if roster.find(f"{message.author.mention}") != -1:
            await message.channel.send("You're already queued for a match!")
        else:
            teamSize += 1
            add_to_team_roster(f"{message.author.mention}\n")
        team_embed = discord.Embed(
            title=f'Lobby: {teamSize} / {teamSizeMax}',
            description=f"{roster}",
            colour=discord.Color.orange()
        )
        await message.channel.send(embed=team_embed)
        if teamSize == teamSizeMax:
            assign_captains()

    @commands.command()
    async def leave(self, message):
        global roster
        global teamSize
        if roster.find(f"{message.author.mention}") == -1:
            await message.channel.send("You're not queued for a match!")
        else:
            teamSize -= 1
            remove_from_team_roster(f'{message.author.mention}\n')
        team_embed = discord.Embed(
            title=f'Lobby: {teamSize} / {teamSizeMax}',
            description=f"{roster}",
            colour=discord.Color.orange()
        )
        await message.channel.send(embed=team_embed)

    @commands.command()
    async def queue(self, message):
        team_embed = discord.Embed(
            title=f'Lobby: {teamSize} / {teamSizeMax}',
            description=f"{roster}",
            colour=discord.Color.orange()
        )
        await message.channel.send(embed=team_embed)

    @commands.command()
    async def teams(self, message):
        global roster
        global teamSize
        team_embed = discord.Embed(
            title=f'Current Teams: {teamSize} / {teamSizeMax}',
            colour=discord.Color.orange()
        )
        team_embed.add_field(name="Team 1", value=f"Captain: \n Players:\n {roster}", inline=True)
        team_embed.add_field(name="Team 2", value=f"Captain: \n Players:\n {roster}", inline=True)
        team_embed.add_field(name="Remaining Players", value=f"{roster}", inline=True)

        await message.channel.send(embed=team_embed)

    @commands.command()
    async def pick(self, message, member: discord.Member):
        global roster
        global teamSize
        await message.channel.send(f'{message.author.mention} picked {member.mention}!')
        remove_from_team_roster(member.mention)
        add_to_team_one_roster(member.mention)
        team_embed = discord.Embed(
            colour=discord.Color.orange()
        )
        team_embed.add_field(name="Team 1", value=f"Captain:\n {team1_captain}\n Players:\n {team1_roster}",
                             inline=True)
        team_embed.add_field(name="Team 2", value=f"Captain:\n {team2_captain}\n Players:\n {team2_roster}",
                             inline=True)
        team_embed.add_field(name="Remaining", value=f"Players: {roster}", inline=True)

        await message.channel.send(embed=team_embed)

    @commands.command()
    async def compete(self, message):
        mycursor.execute(f"SELECT * FROM `planetside_users` WHERE `discord` = {message.author.id}")
        result = mycursor.fetchone()
        if result is None:
            await message.channel.send(f'{message.author.mention} You are now registered!')
            mycursor.execute(f"INSERT INTO `planetside_users` (`discord`) VALUES({message.author.id})")
            db.commit()
        else:
            mycursor.execute(f"SELECT score FROM `planetside_users` WHERE `discord` = {message.author.id}")
            result = mycursor.fetchone()
            await message.channel.send(
                f'{message.author.mention} You are already registered!\nYour current score: {result[0]}')

    @commands.command()
    async def clear(self, ctx):
        await ctx.channel.purge(limit=10)


def setup(client):
    client.add_cog(EloSystem(client))
