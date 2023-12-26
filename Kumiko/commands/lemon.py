from ..bot_config import bot, commands

#Adjustable parameters of the 🍋 wave
cap   = 8
curve = [0,1,4,7,8,7,4,1]
width = 3
count = 3

lemon_wave  = ''
for i in curve:
    s  = ' '*i
    s += '🍋'*3
    s += ' '*(cap-i)
    s += '\n'
    lemon_wave += s

lemon_wave *= count

# lemon_wave  = '🍋🍋🍋      \n'
# lemon_wave += '   🍋🍋🍋   \n'
# lemon_wave += '      🍋🍋🍋\n'
# lemon_wave += '   🍋🍋🍋   \n'
# lemon_wave *= 5

@bot.command()
async def lemon(ctx:commands.Context, n:int=5) -> None:
    '''🍋 Lemon 🍋'''
    #Prevent over-abuse
    n = min(n,100)

    for i in range(n):
        await ctx.send(lemon_wave)
