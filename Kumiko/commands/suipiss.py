from discord.ext import commands

from Kumiko.bot_config import bot


@bot.command()
async def suipiss(ctx: commands.Context) -> None:
    '''suipiss'''
    await ctx.send('https://www.youtube.com/watch?v=mayWtLidGlA')
