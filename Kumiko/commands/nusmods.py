import discord
from requests import get as get_url
from datetime import datetime as dt
from ..bot_config import bot, commands



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
