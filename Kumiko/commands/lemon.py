from ..bot_config import bot, commands



@bot.command()
async def lemon(ctx:commands.Context, n:int=5) -> None:
    '''🍋 Lemon 🍋'''
    #Prevent over-abuse
    n = min(n,100)

    lemon  = '🍋🍋🍋    \n'
    lemon += '  🍋🍋🍋  \n'
    lemon += '    🍋🍋🍋\n'
    lemon += '  🍋🍋🍋  \n'
    for i in range(n):
        await ctx.send(lemon)
