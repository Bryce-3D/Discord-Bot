import random
import asyncio
from ..bot_config import bot, commands



@bot.command()
async def spam(ctx:commands.Context, n:int=5) -> None:
    '''h a'''
    msges = ['OMG IT\'S A SUSSY AMOGUS BAKA-CHAN', 
             'I\'ve been mixing my own urine, various perfumes and chemicals to make the perfect emulatuon of Hoshimachi Suisei\'s urine scent.', 
             'Genshin Impact is a game which has sucked away my soul and killed my dog.', 
             'Gura my dog died ***LET\'S GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO***',
             'Meto mis juevos en tu *boca*',
             'Genshin Impact is a game which has sucked away my soul and killed my dog',
             'L + Ratio']
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
