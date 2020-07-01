import asyncio
import random
import discord
import mysql.connector
from discord.utils import get
from discord.ext import commands
from decouple import config
import time

Database_Username = config('LOCALHOST_USER')
Database_Password = config('LOCALHOST_PASSWORD')

db = mysql.connector.connect(
    host='localhost',
    database='planetside_data',
    user=Database_Username,
    passwd=Database_Password
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
jaegerUsername = 'jaegerUsername'
jaegerPassword = 'jaegerPassword'


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
    team_embed.add_field(name="Team 1",
                         value=f"Captain: \n {team1_captain} ({team1_faction})\n Players:" + "\n".join(team1_roster),
                         inline=True)
    team_embed.add_field(name="Team 2",
                         value=f"Captain: \n {team2_captain} ({team2_faction})\n Players:" + "\n".join(team2_roster),
                         inline=True)
    team_embed.add_field(name="Remaining", value="Players:" + "\n".join(roster), inline=True)
    return team_embed


# TODO: Split into various cogs
# TODO: def player_list(): add a player list call
# TODO: async def autopick(): auto picks teams
# TODO: def map_remove(): removes a map that is currently in use
# TODO: def map_add(): adds a map that is no longer in use
# TODO: def map_check(): edits the map list based on available maps


def reset():
    global faction_list
    global temp_map_list
    faction_list = ['VS', 'NC', 'TR']
    temp_map_list = map_list.copy()


async def match_keeper(ctx):
    match_keep_role = get(ctx.message.guild.roles, name='Match Leader')
    await ctx.channel.send(f'{ctx.author.mention} has been selected to submit the final match score!')
    await asyncio.sleep(30 * 60)
    await ctx.author.add_roles(match_keep_role)
    await asyncio.sleep(60 * 60)
    match_role_true = get(ctx.author.roles, name='Match Leader')
    if match_role_true:
        await ctx.author.remove_roles(match_keep_role)
        await ctx.channel.send(f'{ctx.author.mention} has forgotten to submit the score of the previous match :(')


class EloSystem(commands.Cog):
    """
    A class used to contain all of the commands

    Methods
    -------
    on_ready(self)
        Prints the animals name and what sound it makes
    """

    def __init__(self, client):
        self.client = client

    # @commands.command()  # !register [@member]

    # @commands.command()  # !register [@member]
    # @commands.guild_only()
    # async def register(self, ctx, member: discord.Member):
    #     user = ctx.author
    #     role = get(user.roles, name="Admin")
    #     if role is not None:
    #         mycursor.execute(f"INSERT INTO `planetside_users` (`discord`) VALUES({member.id})")
    #         db.commit()
    #         role = get(member.guild.roles, name="Registered")
    #         await member.add_roles(role)
    #         await member.send("Congrats! You have been approved to use Open League, "
    #                           "brought to you by Planetside Infantry League.\n"
    #                           "You should now have access to all of the OL channels")
    #         await ctx.channel.send(f'{ctx.author.mention} registered {member.mention}!')

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is online')

    @commands.command()
    @commands.guild_only()
    async def test(self, ctx):
        # global team1_captain
        # global team_pick_captain
        # team1_captain = ctx.author.id
        # team_pick_captain = ctx.author.id
        # add(roster, ctx.author.mention)
        await match_keeper(ctx)

    """
    Registered Commands

    !join
    !leave
    !queue
    !maps
    """

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx):
        """Returned argument a is squared."""
        if lobby.count(f"{ctx.author.mention}") == 0:
            add(lobby, ctx.author.mention)
            await ctx.channel.send("You've been added to the queue!")
        else:
            await ctx.channel.send("You're already queued for a match!")
        await ctx.channel.send(embed=lobby_list())
        if len(lobby) == teamSizeMax:
            if roster:
                await ctx.channel.send(
                    "There is currently a match being picked right now, please try again after picking is finished")
            else:
                assign_captains()

    @commands.command()
    @commands.guild_only()
    async def leave(self, ctx):
        if lobby.count(f"{ctx.author.mention}") == 1:
            remove(lobby, ctx.author.mention)
            await ctx.channel.send("You've been removed from the     queue.")
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
        await ctx.channel.send('Current Map Pool: \n> ' + "\n> ".join(map_list))

    # Team-Captain Commands

    # !faction
    # !ban
    # !pick
    # !auto_pick
    # !players

    @commands.command()  # !account
    @commands.guild_only()
    async def account(self, ctx):
        if ctx.author.id == team1_captain or ctx.author.id == team2_captain:
            await ctx.channel.send(
                'Accounts sent out. Please check your Discord DM\'s for each account and the rules surrounding them.')
            for player in roster:
                mycursor.execute(f"SELECT * FROM `planetside_users` WHERE `discord` = {player[2:-1]}")
                info = mycursor.fetchone()
                if info[4] is None:
                    user = await self.client.fetch_user(player[2:-1])
                    embed = discord.Embed(
                        colour=discord.Color.orange(),
                        title='Jaeger Account Info:',
                        description=f'**MUST READ: [Rules](https://planetsideguide.com/other/jaeger/)**\n'
                                    f'Username: `{jaegerUsername}`\n '
                                    f'Password: `{jaegerPassword}`',
                    )
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/703912354269888572/727931056476389396/PIL_Logo11_Zoomed.png")
                    embed.set_footer(
                        text='Failure to follow these rules can result in your suspension of __**ALL**__ Jaeger events.')
                    await user.send(embed=embed)
        else:
            await ctx.channel.send('You have to be picking player to use this command!')

    @commands.command()  # !faction [VS/NC/TR]
    @commands.guild_only()
    async def faction(self, ctx):
        global team1_faction
        global team2_faction
        if ctx.author.id == team_pick_captain:
            if team1_faction and team2_faction:
                await ctx.channel.send(
                    f'{ctx.author.mention}, you have already picked a faction! Please pick a player instead.')
            elif not ctx.message.content[9:] in faction_list:
                await ctx.channel.send(
                    f'{ctx.author.mention} {ctx.message.content[9:]} is not a valid faction. Choose either ' + ", ".join(
                        faction_list))
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
    @commands.guild_only()
    async def ban(self, ctx):
        global match_map
        if ctx.author.id == team_pick_captain:
            if not team1_faction or not team2_faction:
                await ctx.channel.send(f'{ctx.author.mention} please pick your faction')
            elif match_map:
                await ctx.channel.send(
                    f'{ctx.author.mention} your map has already been selected ({match_map}), please pick a player')
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
    @commands.guild_only()
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
        await ctx.channel.send(embed=match_list())
        if not roster:
            await match_keeper(ctx, ctx.author.id)
            reset()
            await ctx.channel.send('Teams and factions are picked, prepare to play!')

    # @commands.command()  # !auto_pick
    # @commands.guild_only()
    # async def auto_pick(self, ctx):
    #     if ctx.author.id == team_pick_captain:
    #         if not team1_faction or not team2_faction:
    #             await ctx.channel.send(f'{ctx.author.mention} please pick your faction first')
    #         elif not match_map:
    #             await ctx.channel.send(f'{ctx.author.mention} please ban a map from the pool first')
    #     else:
    #         await ctx.channel.send(f'{ctx.author.mention} it is not your turn to pick!')
    #     await ctx.channel.send(embed=match_list())
    #     if not roster:
    #         reset()
    #         await ctx.channel.send('Teams and factions are picked, prepare to play!')

    # @commands.command()  # !players
    # @commands.guild_only()
    # async def players(self, ctx):
    #     if ctx.author.id == team_pick_captain:
    #         embed = discord.Embed(
    #             description='Remaining Player List:',
    #             colour=discord.Color.orange()
    #         )
    #         for player in roster:
    #             mycursor.execute(f"SELECT * FROM `planetside_users` WHERE `discord` = {player[2:-1]}")
    #             stats = mycursor.fetchone()
    #             user = await self.client.fetch_user(player[2:-1])
    #             embed.add_field(name=f'{user}', value=f'Matches Played: {stats[2]} \n'
    #                                                   f'Live [Main](https://ps2.fisu.pw/player/?name=rapidrelief1)\n'
    #                                                   f'Jaeger [VS](https://ps2.fisu.pw/player/?name=rapidrelief1) '
    #                                                   f'[NC](https://ps2.fisu.pw/player/?name=rapidrelief1) '
    #                                                   f'[TR](https://ps2.fisu.pw/player/?name=rapidrelief1)',
    #                             inline=False)
    #         await ctx.author.send(embed=embed)
    #     else:
    #         ctx.channel.send('You have to be picking player to use this command!')

    @commands.command()  # !submit [matchID]
    @commands.guild_only()
    async def submit(self, ctx):
        match_keep = get(ctx.author.roles, name="Match Leader")
        if match_keep:
            s = ctx.message.content.split(' ')
            match_score = int(s[1])
            await ctx.author.remove_roles(match_keep)
            await ctx.channel.send(f'Thank you for submitting your match results {ctx.author.mention}.')
        else:
            await ctx.channel.send(f'{ctx.author.mention}, only the Match Leader can submit the results of a match.')

    # Admin Commands

    # !register
    # !clear_queue
    # !clear_match
    # !map_add
    # !map_remove
    # !suspend

    @commands.command()  # !register [@member]
    @commands.guild_only()
    async def register(self, ctx, member: discord.Member):
        user = ctx.author
        role = get(user.roles, name="Admin")
        if role is not None:
            mycursor.execute(f"INSERT INTO `planetside_users` (`discord`) VALUES({member.id})")
            db.commit()
            role = get(member.guild.roles, name="Registered")
            await member.add_roles(role)
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

    @commands.command()  # !suspend [@member] [time in minutes] [reasoning]
    @commands.guild_only()
    async def suspend(self, ctx, member: discord.Member):
        admin_role = get(ctx.author.roles, name="Admin")
        if admin_role:
            s = ctx.message.content.split(' ')
            suspend_time = int(s[2])
            remove(s, s[2])
            remove(s, s[1])
            remove(s, s[0])
            registered_role = get(member.guild.roles, name="Registered")
            await member.remove_roles(registered_role)
            await member.send(f'You have been temporarily suspended from Open League for:\n'
                              f'> ' + ' '.join(s) + '\n'
                                                    f'You will be able to play again in: **{int(suspend_time / 60)} hour(s) and {suspend_time % 60} minutes**')
            await ctx.channel.send(
                f'{ctx.author.mention} suspended {member.mention} for **{int(suspend_time / 60)} hour(s) and {suspend_time % 60} minutes**!')
            await asyncio.sleep(suspend_time * 60)
            await member.add_roles(registered_role)
            await member.send(f'You now have permission to play Open League again. Play nice!')
            await ctx.channel.send(f'{ctx.author.mention}, {member.mention} has been unsuspended.')


def setup(client):
    client.add_cog(EloSystem(client))
