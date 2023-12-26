import random
from typing import Optional
from ..bot_config import bot, commands



#ha[i][j] = the ith ha capitalization nested between j pairs of asterisks
ha = [['ha','hA','Ha','HA']]
for i in range(3):
    ha.append(['*' + i + '*' for i in ha[-1]])
arr = ['↗️', '↘️']

@bot.command()
async def pekopeko(ctx:commands.Context, min_ha:Optional[int]=None, max_ha:Optional[int]=None) -> None:
    '''
    Channel your inner peko laugh. 
    Number of ha's is 
        default = randomly chosen in [10:30]
        one arg = that arg
        two args = range(arg0, arg1)
    Taken from my repository Random
    '''
    #Determine number of laughs to put
    if min_ha == None:
        n = random.randrange(10,30)
    elif max_ha == None:
        n = min_ha
        if n <= 0:
            await ctx.send(f'{n} isn\'t a positive integer...')
            return
    else:
        m,M = min_ha,max_ha
        if m <= 0 and M <= 0:
            await ctx.send(f'{m} and {M} aren\'t positive integers...')
            return
        elif m <= 0:
            await ctx.send(f'{m} isn\'t a positive integer...')
            return
        elif M <= 0:
            await ctx.send(f'{M} isn\'t a positive integer...')
            return
        elif m >= M:
            await ctx.send(f'[{m},{M}) isn\'t a valid interval...')
            return
        n = random.randrange(m, M)
    
    #Nerf to make sure it fits in one message
    n = min(n,200)
    s = []

    #Randomly put together the selected number of ha's
    for Homu in range(n):
        s.append( random.choice(random.choice(ha)) )
        s.append( random.choice(arr) )

    s = ' '.join(s)
    await ctx.send(s)
