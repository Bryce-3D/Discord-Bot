#File to store common utility functions for Kumiko

from __future__ import annotations

def MEX(d:dict|set) -> int:
    '''Returns the MEX of a dict or set'''
    ans = 0
    while ans in d:
        ans += 1
    return ans

def ping(user_id:int|str) -> str:
    '''Takes in a discord id and returns a string to ping that user'''
    return f'<@!{user_id}>'
