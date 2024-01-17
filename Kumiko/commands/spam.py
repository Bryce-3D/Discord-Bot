import random
import asyncio
from ..bot_config import bot, commands



@bot.command()
async def spam(ctx:commands.Context, n:int=5) -> None:
    '''h a'''
    msges = ['TODO: Put some messages here']
    l = len(msges)

    #Prevent over-abuse
    n = min(n,100)

    for i in range(n):
        msg = ''
        for i in range(15):
            msg += random.choice(msges)
            msg += '\n'
        await ctx.send(msg)
        await asyncio.sleep(3)
