'''
File to store common utility functions for Kumiko
'''

from Kumiko.types import DiscordChannel, DiscordUser

def ping(user:DiscordUser) -> str:
    '''Returns a string that pings the user'''
    return f'<@!{user.id}>'

def channel_str(channel:DiscordChannel) -> str:
    '''Returns a string linking to the given channel'''
    return f'<#{channel.id}>'
