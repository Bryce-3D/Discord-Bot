import discord
from discord.ext.commands import has_permissions
from ..bot_config import bot, commands



@bot.command()
@has_permissions(administrator=True)
async def test(ctx:commands.Context) -> None:
    await ctx.channel.send('You are a discord mod :skull:')

@test.error
async def test_error(ctx:commands.Context, error:discord.ext.commands.errors) -> None:
    await ctx.channel.send('Congrats you are not a discord mod (yet)')
    await ctx.channel.send(error)
    await ctx.channel.send(type(error))
