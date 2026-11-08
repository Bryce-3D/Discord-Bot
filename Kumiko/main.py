'''
Credits to 
    https://github.com/Rapptz/discord.py/blob/v1.7.3/examples/basic_bot.py
for being used as reference code during the early stages of development.
'''
import discord
from discord.ext import commands

#Bot token is stored in a separate file for secrecy
from Kumiko.Token import token
from Kumiko.bot_config import bot
from Kumiko.commands import *
from Kumiko.misc import testing


@bot.event
async def on_ready():
    print(f'Running the bot {bot.user.name}')
    print('~' * 75)

bot.run(token)
