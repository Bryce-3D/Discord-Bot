import discord
from ..bot_config import bot, commands



@bot.command()
async def help(ctx:commands.Context, cmd:str=None) -> None:
    '''
    Usage
        %help cmd
    
    If cmd is not provided, sends a list of all commands with a short description.
    If cmd is provided, sends a detailed description of how to use %cmd
    '''

    emb = discord.Embed(
        title = '**Help**',
        description = "Hi! My prefix is `%`",
        color = 0xff6d01
    )
    emb.add_field(
        name   = '__Commands__', 
        value  = '> TODO',
        inline = False
    )
    await ctx.channel.send(embed=emb)
