from ..bot_config import bot, commands



@bot.command()
async def imo(ctx:commands.Context, country:str=None) -> None:
    '''Search the IMO stats of a country'''
    if country == None:
        await ctx.send('https://www.imo-official.org/default.aspx')
    else:
        await ctx.send(f'https://www.imo-official.org/country_info.aspx?code={country.upper()}')
