import discord
from discord.ext import commands

description = '''I'm a bot, I guess'''

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(
    command_prefix='%',
    description=description,
    intents=intents,
    help_command=None
)
