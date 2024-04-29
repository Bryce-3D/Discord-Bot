import random
from Kumiko.bot_config import bot, commands



@bot.command()
async def choose(ctx:commands.Context, *items:str) -> None:
    '''Prints a random item from a list of items'''
    if len(items) == 0:
        await ctx.send('Please put at least one option')
        return
    await ctx.send(random.choice(items))
