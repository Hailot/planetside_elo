import os

import discord
from discord.ext import commands

client = commands.Bot(command_prefix='!')

client.remove_command('help')


# msg = message.content.toLowerCase()


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def help(message):
    # await message.channel.purge(limit=1)
    embed = discord.Embed(
        colour=discord.Color.orange()
    )
    embed.set_author(name='General Commands')
    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Question_mark_%28black%29.svg/1200px-Question_mark_%28black%29.svg.png")
    embed.add_field(name='Lobby Commands', value='`!register` \n'
                                                 '`!join` \n'
                                                 '`!leave` \n'
                                                 '`!queue` \n'
                                                 '`!teams` ', inline=True)
    embed.add_field(name='Lobby Commands', value='Registers the user\n'
                                                 'Join the queue for a match\n'
                                                 'Leave the queue for a match\n'
                                                 'See the current match queue\n'
                                                 '', inline=True)

    await message.channel.send(f'{message.author.mention} Here is a list of the commands: ')
    embeda = discord.Embed(
        colour=discord.Color.orange()
    )
    embeda.set_author(name='Team Captain Commands')
    embeda.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Question_mark_%28black%29.svg/1200px-Question_mark_%28black%29.svg.png")
    embeda.add_field(name='Lobby Commands', value='`!ban "mapname"` \n'
                                                  '`!pick "@user"` \n', inline=True)
    embeda.add_field(name='Lobby Commands', value='Bans a map \n'
                                                  'Picks a player\n', inline=True)
    embedb = discord.Embed(
        colour=discord.Color.orange()
    )
    embedb.set_author(name='Other Commands')
    embedb.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Question_mark_%28black%29.svg/1200px-Question_mark_%28black%29.svg.png")
    embedb.add_field(name='Lobby Commands', value='`!help` \n'
                                                  '`!smile` \n'
                                                  , inline=True)
    embedb.add_field(name='Lobby Commands', value='Brings up this prompt\n'
                                                  'Sends you a smile\n'
                                                  , inline=True)

    embedb.set_footer(text='Made by Rapid',
                      icon_url='https://cdn.discordapp.com/attachments/702303117450018896/717756306190237696/PIL_Logo_toby_dog_prison.png')

    await message.channel.send(embed=embed)
    await message.channel.send(embed=embeda)
    await message.channel.send(embed=embedb)


@client.command()
async def smile(ctx):
    await ctx.channel.send(f':slight_smile:{ctx.author.mention}')


@client.event
async def on_command_error(message, error):
    if isinstance(error, commands.CommandNotFound):
        await message.send(f'{message.author.mention} Invalid command, try again')
    else:
        raise error


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run('NzE5OTAzMjU4MzIzNDUxOTI2.Xt-XNg.iW00he4GtkIMYuwbdfo66uicwJg')
