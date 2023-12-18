# This example requires the 'members' privileged intents

import discord
from discord.ext import commands

#For rng purposes
import random
#For async sleeping
import asyncio
#For Optional type hinting
from typing import Optional
#For JSON processing
import json
#For NUSMods API
from requests import get as get_url
#For getting the time
from datetime import datetime as dt

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
async def nusmods(ctx:commands.Context, mod_code:str=None, 
                  AY:str=None) -> None:
    '''
    Usage
        %nusmods mod_code AY
    
    Sends information about the given module in the given AY.
    AY defaults to the current AY if it is not provided.

    Returns a link to NUSMods along with a quick guide on how to use this 
    command if no argument is prodivded.
    '''
    # TODO: Maybe make this compute the vacancies by summing over each of the ff
    #     lecs
    #     tuts
    #     labs
    #     sectional teachings
    # then taking the min among them

    def append_sample(s:str) -> str:
        '''Appends a sample usage of this command to a string `s`'''
        s += '\n'
        s += 'Command Usage:\n'
        s += '`%nusmods mod_code AY`\n'
        s += 'Examples:\n'
        s += '`%nusmods LAJ1201`\n'
        s += '`%nusmods CS2040S 2021-2022`\n'
        s += '*If the AY is not provided, the current AY is used by default'
        return s
    
    def is_valid_ay(s:str) -> bool:
        '''
        Checks whether `s` is a valid input for AY.
        Will be functional until AY9998-9999.
        '''
        #Check that it is XXXX-XXXX
        if len(s) != 9:
            return False
        if s[4] != '-':
            return False

        #Check that the other characters are normal digits
        digs = [str(i) for i in range(10)]
        for c in s[:4]:
            if c not in digs:
                return False
        for c in s[5:]:
            if c not in digs:
                return False
        
        #Check that the years are consecutive in order
        y0 = int(s[:4])
        y1 = int(s[5:])
        if y1-y0 != 1:
            return False

        return True
    
    def is_future_ay(s:str) -> bool:
        '''
        Given a valid AY string `s`, checks whether 
        this is a future AY or not
        '''
        y0 = int(s[:4])      #1nd year of the AY
        y = dt.now().year    #Current year
        m = dt.now().month   #Current month
        if y0 > y:           #Year too far in the future
            return True
        if y0 == y and m <= 6:   #Possible but too early in the year
            return True
        return False

    def is_alphanumeric(s:str) -> bool:
        '''Checks whether `s` only consists of a-z,A-Z,0-9'''
        def help(c:chr) -> bool:
            '''Check for a single character'''
            if 'a' <= c <= 'z':
                return True
            if 'A' <= c <= 'Z':
                return True
            if '0' <= c <= '9':
                return True
            return False

        #Check every character in s
        for c in s:
            if not help(c):
                return False
        return True

    def curr_ay() -> str:
        '''Generates the AY string for the current AY'''
        now = dt.now()
        y = now.year    #y = int(now.strftime('%Y'))
        m = now.month   #m = int(now.strftime('%m'))
        if m <= 6:
            return f'{y-1}-{y}'
        else:
            return f'{y}-{y+1}'

    #Default behavior when no arguments are given
    if mod_code == None:
        s  = 'NUSMods is a useful website for looking up timetables '
        s += 'and information regarding classes in NUS.\n'
        s += 'https://nusmods.com/modules/\n'
        s += 'Please enter a module code to look up information for it.'
        s += '\n'
        s  = append_sample(s)
        await ctx.send(s)
        return
    
    #Check that the inputted module code only has alphanumeric characters
    if not is_alphanumeric(mod_code):
        s  = 'Please only use alphanumeric characters (`A-Z, a-z, 0-9`) '
        s += 'in the module code'
        await ctx.send(s)
        return
    
    #Check that the inputted AY is valid
    if AY !=None and not is_valid_ay(AY):
        s  = 'Invalid `AY` format, pls type as'
        s += '`XXXX-YYYY` where `YYYY = XXXX+1`.\n'
        s += 'Use `%nusmods` for some sample usages.'
        await ctx.send(s)
        return

    #Uppercase mod_code and default to current AY if none given
    mod_code = mod_code.upper()
    if AY == None:
        AY = curr_ay()
    
    #Check that the inputted AY is not in the future
    if is_future_ay(AY):
        s  = 'Sorry, that `AY` is in the future. I cannot predict the future.'
        await ctx.send(s)
        return
    
    #Try retrieving info through the NUSMods API
    API = 'https://api.nusmods.com/v2'
    r = get_url(f'{API}/{AY}/modules/{mod_code}.json')
    if r.status_code == 404:
        s  = 'Error 404 received, pls double check that this module '
        s += 'exists in the given AY'
        await ctx.send(s)
        return
    
    #Get the needed data
    data = r.json()
    mod_code = data['moduleCode']
    mod_name = data['title']

    #mod_sems will be a subset of {'Sem 1', 'Sem 2', 'ST I', 'ST II'} 
    #concatenated by •
    mod_sems = [i['semester'] for i in data['semesterData']]
    sem_num_to_str = {1:'Sem 1', 2:'Sem 2', 3:'ST I', 4:'ST II'}
    mod_sems = [sem_num_to_str[i] for i in mod_sems]
    mod_sems = ' • '.join(mod_sems)
    #Corner case of not being offered this AY
    if mod_sems == '':
        mod_sems = 'Not offered this AY'

    mod_info = data['description']

    #Mods that need this mod as a prerequisite
    if 'fulfillRequirements' in data:
        mod_unlock = data['fulfillRequirements']
        mod_unlock = ', '.join(mod_unlock)
    else:
        mod_unlock = 'Nothing'
    
    mod_mcs  = data['moduleCredit']

    emb = discord.Embed(
        title = f'{mod_code} {mod_name}',
        url   = f'https://nusmods.com/modules/{mod_code}',
        description = f'AY {AY}\n{mod_sems}',
        color = 0xff6d01
    )
    emb.add_field(
        name   = 'Module Info',
        value  = mod_info,
        inline = False
    )
    emb.add_field(
        name   = '*Prereq of',
        value  = mod_unlock,
        inline = True
    )
    emb.add_field(
        name   = 'MCs',
        value  = mod_mcs,
        inline = True
    )

    disc  = '*Disclaimer: Prereqs might be inaccurate when viewing a '
    disc += 'non-canonical variant of a module such as CS1101S vs CS1010'
    emb.add_field(
        name   = '',
        value  = disc,
        inline = False
    )

    await ctx.channel.send(embed=emb)



@bot.command()
async def suipiss(ctx:commands.Context) -> None:
    '''suipiss'''
    await ctx.send('https://www.youtube.com/watch?v=mayWtLidGlA')



@bot.command()
async def choose(ctx:commands.Context, *items:str) -> None:
    '''Prints a random item from a list of items'''
    await ctx.send(random.choice(items))



@bot.command()
async def poll(ctx:commands.Context, question:str, *choices:str) -> None:
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
