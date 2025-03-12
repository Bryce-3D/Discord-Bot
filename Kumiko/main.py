'''
Credits to 
    https://github.com/Rapptz/discord.py/blob/v1.7.3/examples/basic_bot.py
for being used as reference code during the early stages of development.
'''
import asyncio
import json
from requests import get as get_url
from datetime import datetime as dt

import discord
from discord.ext import commands

#Bot token is stored in a separate file for secrecy
from Token import token
from Kumiko.bot_config import bot
from Kumiko.commands import *
from Kumiko.misc import testing


#https://stackoverflow.com/questions/62544309/why-client-emojis-newer-version-of-client-get-all-emojis-returns-empy-list-wh
#https://stackoverflow.com/questions/71959420/client-init-missing-1-required-keyword-only-argument-intents
client = discord.Client(intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'Running the bot {bot.user.name}')
    print('~' * 75)

bot.run(token)
