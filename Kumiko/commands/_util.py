#File to store common utility functions for Kumiko

def ping(user_id:int|str) -> str:
    '''Takes in a discord id and returns a string to ping that user'''
    return f'<@!{user_id}>'
