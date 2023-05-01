# This example requires the 'members' privileged intents

import discord
from discord.ext import commands

#For rng purposes
import random
#For async sleeping
import asyncio
#For Optional type hinting
from typing import Optional
#For the bot token
from Token import token


description = '''I'm a bot, I guess'''

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='%', description=description, intents=intents)

#https://stackoverflow.com/questions/62544309/why-client-emojis-newer-version-of-client-get-all-emojis-returns-empy-list-wh
#https://stackoverflow.com/questions/71959420/client-init-missing-1-required-keyword-only-argument-intents
client = discord.Client(intents=discord.Intents.default())


#Utilities ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Dict to quickly convert a digit to it's spelling
digit_to_word = {0:'zero', 1:'one', 2:'two', 3:'three', 4:'four', 
            5:'five', 6:'six', 7:'seven', 8:'eight', 9:'nine'}
#Dict to quickly convert a digit to it's keycap emoji
num_to_keycap = {0:'0️⃣', 1:'1️⃣', 2:'2️⃣', 3:'3️⃣', 4:'4️⃣', 
                 5:'5️⃣', 6:'6️⃣', 7:'7️⃣', 8:'8️⃣', 9:'9️⃣', 10:'🔟'}



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Bot commands
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command()
async def nusmods(ctx:commands.Context, module_code:str=None) -> None:
    '''Returns the link to a given module in nusmods if a valid module code is given.
    Otherwise, returns a link to the module search page of nusmods.'''
    if module_code == None:
        await ctx.send('https://nusmods.com/modules/')
    else:
        await ctx.send('https://nusmods.com/modules/' + module_code.upper())



@bot.command()
async def suipiss(ctx:commands.Context) -> None:
    '''suipiss'''
    await ctx.send('https://www.youtube.com/watch?v=mayWtLidGlA')



@bot.command()
async def choose(ctx:commands.Context, *items:list[str]) -> None:
    '''Prints a random item from a list of items'''
    await ctx.send(random.choice(items))



@bot.command()
async def poll(ctx:commands.Context, question:str, *choices:list[str]) -> None:
    '''Creates a poll with a question and a (possibly null) set of choices'''
    msg_text = question

    #If no choices given
    if len(choices) == 0:
        msg = await ctx.send(msg_text)
        await msg.add_reaction('<:ya:1102451988005929021>')
        await msg.add_reaction('<:meh:1102451982750457996>')
        await msg.add_reaction('<:na:1102451985954902036>')
    
    #If choices are given
    else:
        #If too many choices, tell them to put less
        if len(choices) > 10:
            await ctx.send('Pls put at most 10 options')
        else:   #If not too many choices
            #Add the choices to the msg
            for i in range(len(choices)):
                msg_text += '\n'
                msg_text += f':{digit_to_word[i]}: - {choices[i]}'
            
            msg = await ctx.send(msg_text)   #Send the msg

            #Add reactions
            for i in range(len(choices)):
                await msg.add_reaction(num_to_keycap[i])



@bot.command()
async def imo(ctx:commands.Context, country:str=None) -> None:
    '''Search the IMO stats of a country'''
    if country == None:
        await ctx.send('https://www.imo-official.org/default.aspx')
    else:
        await ctx.send(f'https://www.imo-official.org/country_info.aspx?code={country.upper()}')



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
        


@bot.command()
async def meta(ctx:commands.Context) -> None:
    '''Meto mis juevos en tu boca'''
    msges = ['I have one question to ask slayer.',
             'What\'s the name of the VR company owned by the lizard man?',
             'It\'s Meta hellboy',
             'METO MIS JUEVOS EN TU ***BOCA***']
    
    for msg in msges:
        await ctx.send(msg)
        await asyncio.sleep(5)



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





#Sample codes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Taken from 
# https://github.com/Rapptz/discord.py/blob/v1.7.3/examples/basic_bot.py

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('~' * 75)

bot.run(token)

# @bot.command()
# async def add(ctx, left: int, right: int):
#     """Adds two numbers together."""
#     await ctx.send(left + right)

# @bot.command()
# async def roll(ctx, dice: str):
#     """Rolls a dice in NdN format."""
#     try:
#         rolls, limit = map(int, dice.split('d'))
#     except Exception:
#         await ctx.send('Format has to be in NdN!')
#         return

#     result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
#     await ctx.send(result)

# @bot.command(description='For when you wanna settle the score some other way')
# async def choose(ctx, *choices: str):
#     """Chooses between multiple choices."""
#     await ctx.send(random.choice(choices))

# @bot.command()
# async def repeat(ctx, times: int, content='repeating...'):
#     """Repeats a message multiple times."""
#     for i in range(times):
#         await ctx.send(content)

# @bot.command()
# async def joined(ctx, member: discord.Member):
#     """Says when a member joined."""
#     await ctx.send('{0.name} joined in {0.joined_at}'.format(member))

# @bot.group()
# async def cool(ctx):
#     """Says if a user is cool.
#     In reality this just checks if a subcommand is being invoked.
#     """
#     if ctx.invoked_subcommand is None:
#         await ctx.send('No, {0.subcommand_passed} is not cool'.format(ctx))

# @cool.command(name='bot')
# async def _bot(ctx):
#     """Is the bot cool?"""
#     await ctx.send('Yes, the bot is cool.')
