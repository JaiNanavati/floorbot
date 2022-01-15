import os
import random

import discord

from discord.ext import commands
from nft import get_floor_price



TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


# # client = discord.Client()
#
# @client.event
# async def on_ready():
#     print(f'{client.user.name} has connected to Discord!')

@bot.command(name='floor', help='collection slug, property type (optional), property value (optional)')
async def floor(ctx, slug: str, prop: str=None, *, arg=None):
    prop_val = arg
    if prop:
        if not prop_val:
            response =  'Specify value along with your property'
    response = get_floor_price(slug, prop, prop_val)
    await ctx.send(response)

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#
#     message_arr = message.content.split()
#     if len(message_arr) < 4 or len(message_arr) > 4:
#         raise discord.DiscordException
#
#
#
#
#
#     if message.content == 'floor!':
#         response = random.choice(brooklyn_99_quotes)
#         await message.channel.send(response)
#     elif message.content == 'raise-exception':
#         raise discord.DiscordException

bot.run(TOKEN)
