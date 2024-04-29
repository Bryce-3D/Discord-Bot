import discord
from Kumiko.bot_config import bot, commands

Kumiko_commands = [
    'choose',
    'help',
    'imo',
    'lemon',
    'nusmods',
    'pekopeko',
    'poll',
    'spam',
    'suipiss',
]

@bot.command()
async def help(ctx:commands.Context, cmd:str=None) -> None:
    '''
    Usage
        %help cmd
    
    If cmd is not provided, sends a list of all commands with a short description.
    If cmd is provided, sends a detailed description of how to use %cmd
    '''

    if cmd == None:
        s  = 'Hi! My prefix is `%`\n'
        s += 'Use `%help cmd` for more detailed information on a specific command'
        emb = discord.Embed(
            title = '**Help**',
            description = s,
            color = 0xff6d01
        )

        s  = '> `%choose` - Choose an option from a given list of items\n'
        s += '> `%help` - Used to display info about commands\n'
        s += '> `%imo` - Used to send the link to a country\'s IMO page\n'
        s += '> `%lemon` - Spams a lemon wave\n'
        s += '> `%nusmods` - Used to look up information on modules in NUS through the NUSMods API\n'
        s += '> `%pekopeko` - Generates a random string of Pekora\'s laugh\n'
        s += '> `%poll` - Sends a poll in the form of a message\n'
        s += '> `%spam` - Spams the chat\n'
        s += '> `%suipiss` - Sends a link to a youtube video about suipiss'
        emb.add_field(
            name   = '__Commands__', 
            value  = s,
            inline = False
        )
        await ctx.channel.send(embed=emb)
        return
    
    if cmd not in Kumiko_commands:
        await ctx.send(f'I don\'t have any command called `{cmd}`')
        return
    
    await ctx.send('TODO')
