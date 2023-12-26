import random
from ..bot_config import bot, commands



@bot.command()
async def choose(ctx:commands.Context, *items:str) -> None:
    '''Prints a random item from a list of items'''
    await ctx.send(random.choice(items))
