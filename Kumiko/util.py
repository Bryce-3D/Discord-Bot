'''
File to store common utility functions for Kumiko
'''

import discord

def MEX(d:dict|set) -> int:
    '''Returns the MEX of a dict or set'''
    ans = 0
    while ans in d:
        ans += 1
    return ans

def ping(user:discord.User|discord.Member) -> str:
    '''Returns a string that pings the user'''
    return f'<@!{user.id}>'
