import os
import random
import json
import discord

from discord.ext import commands
from nft import get_floor_price, get_collection
from utils import lower




TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


# # client = discord.Client()
#
# @client.event
# async def on_ready():
#     print(f'{client.user.name} has connected to Discord!')

@bot.command(name='list')
async def list(ctx):
    list = []
    await ctx.send(f'Collections supported:{list}')

@bot.command(name='floor', help='collection slug, property type (optional), property value (optional)')
async def floor(ctx, slug: str, prop: str=None, *, arg=None):
    prop_val = arg
    if prop:
        if not prop_val:
            response =  'Specify value along with your property'
    response = await get_floor_price(slug, prop, prop_val)
    await ctx.send(response)


@bot.command(name='create', help='Provides functionality to support a new collection')
async def create(ctx, slug: str):
    response_json = get_collection(slug)
    print(response_json)
    if response_json:
        response_json['collection']['traits'] = lower(response_json['collection']['traits'])
        with open('collections/'+slug+'.json', 'w', encoding='utf-8') as f:
            json.dump(response_json, f, ensure_ascii=False, indent=4)
            await ctx.send(f'Successfully added support for {slug}')
    else:
        await ctx.send(f'Failed to add support for {slug}')
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
