from time import sleep
from ..bot_config import bot, commands

#Adjustable parameters of the 🍋 wave
curve = [0,1,4,7,8,7,4,1]   #Shape of the curve
width = 3                   #Number of lemons per row
count = 1                   #Number of unit waves per message
limit = 100                 #Maximum number of messages to prevent abuse

lemon_wave  = ''
for i in curve:
    s  = ' '*i
    s += '🍋'*width
    s += ' '*(max(curve)-i)
    s += '\n'
    lemon_wave += s

lemon_wave *= count

@bot.command()
async def lemon(ctx:commands.Context, n:int=5) -> None:
    '''🍋 Lemon 🍋'''
    #Prevent over-abuse
    n = min(n,limit)

    for i in range(n):
        await ctx.send(lemon_wave)
        sleep(1)
