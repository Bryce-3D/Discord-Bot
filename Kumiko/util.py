'''
File to store common utility functions for Kumiko
'''

from Kumiko.types import DiscordChannel, DiscordUser

def MEX(d:dict|set) -> int:
    '''Returns the MEX of a dict or set'''
    ans = 0
    while ans in d:
        ans += 1
    return ans

def ping(user:DiscordUser) -> str:
    '''Returns a string that pings the user'''
    return f'<@!{user.id}>'

def channel_str(channel:DiscordChannel) -> str:
    '''Returns a string linking to the given channel'''
    return f'<#{channel.id}>'
