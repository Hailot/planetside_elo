import os
import discord
from discord.ext import commands
from discord.utils import get
from decouple import config

client = commands.Bot(command_prefix='!')
client.remove_command('help')

Discord_Token = config('DISCORD_TOKEN')


@client.command()
@commands.guild_only()
async def help(ctx):
    embed = discord.Embed(
        colour=discord.Color.orange()
    )
    embed.set_author(name='Your Commands')
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/703912354269888572/727931056476389396/PIL_Logo11_Zoomed.png")
    embed.add_field(name='Lobby Commands',
                    value='`!join` - Join the lobby for a match\n'
                          '`!leave` - Leave the lobby for a match\n'
                          '`!queue` - See the current match lobby'
                    , inline=False)
    embed.add_field(name='Team Captain Commands',
                    value='`!account` - Passes out accounts to those players who need them\n'
                          '`!faction` `VS`/`NC`/`TR` - Picks a faction\n'
                          '`!ban` `map name` - Removes a map from the map pool\n'
                          '`!pick` `@player` - Picks a player\n'
                          '`!submit` `matchID` - Submit the results of the match.'
                    # '`!players` - DM\'s remaining player\'s stats'
                    # '`!autopick`- '
                    , inline=False)
    embed.add_field(name='Other Commands',
                    value='`!help` - Brings up this prompt\n'
                          '`!maps` - See the current map rotation'
                    , inline=False)
    user = ctx.author
    role = get(user.roles, name="Admin")
    if role:
        embed.add_field(name='Admin Commands',
                        value='`!register` - Registers the user\n', inline=False)
        embed.add_field(name='Admin Match Commands',
                        value='`!clear_queue` - Clears the lobby queue\n'
                              '`!clear_match` - Clears the match roster\n'
                              '`!map_add` - Adds a map to a pool\n'
                              '`!map_remove` - Removes a map from the pool', inline=False)
    embed.set_footer(text='Made by Rapid',
                     icon_url='https://cdn.discordapp.com/attachments/702303117450018896/717756306190237696/PIL_Logo_toby_dog_prison.png')
    await ctx.channel.send(f'{ctx.author.mention} Here is a list of the commands you have access to: ')
    await ctx.channel.send(embed=embed)


@client.event
async def on_command_error(message, error):
    if isinstance(error, commands.CommandNotFound):
        await message.send(f'{message.author.mention} Invalid command, please try again.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await message.send(f'{message.author.mention} You must specify a specific person, try again.')
    elif isinstance(error, commands.NoPrivateMessage):
        await message.send(f'{message.author.mention} You can\'t use that command in DMs, sorry.')
    else:
        raise error


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(Discord_Token)
