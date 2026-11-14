import discord
from dataclasses import dataclass
from discord.ext import commands
from enum import IntEnum, StrEnum

from Kumiko.bot_config import bot
from Kumiko.util import MEX,ping
from Kumiko.types import DiscordUser

# TODO: Make lobbies tied to channels rather than using a lobby id
# TODO: Clean out unnecesary comments
# TODO: Go over suggestions in tictactoe comments.txt and delete that file when done
# TODO: Bug fixes obv
# TODO: Raise exceptions instead of returning status codes (?)

'''
Buglist
- %tictactoe leave raises "Cannot send an empty message"
    * Now says "left lobby None" after reducing Lobby to dataclass LobbyState
- Properly end tied games
'''

class StatusCode(IntEnum):
    '''Status Codes used to manage Tic-Tac-Toe'''
    Success          =  0
    NotInLobby       =  1
    InLobby          =  2
    FullLobby        =  3
    NotFullLobby     =  4
    StartedLobby     =  5
    UnstartedLobby   =  6
    NonexistentLobby =  7
    NotYourTurn      =  8
    CellOutOfRange   =  9
    CellUnavailable  = 10
    GameOver         = 11



class PlayerStr(StrEnum):
    P1 = 'X'
    P2 = 'O'



class TicTacToe:
    '''
    A class to represent the state of a tic-tac-toe game.

    The returned `StatusCode`s listed in the documentation are listed in 
    the order they are checked in the implementation, with the exception 
    of `StatusCode.Success` always being the first listed one.
    '''
    def __init__(self):
        self.board:list[list[PlayerStr|None]] = [
            [None for c in range(3)] for r in range(3)
        ]
        self.is_P1_turn:bool = True
    
    def _win_check(self, player:PlayerStr) -> bool:
        #Check rows
        for r in range(3):
            if self.board[r][0] == self.board[r][1] == self.board[r][2] == player:
                return True
        #Check cols
        for c in range(3):
            if self.board[0][c] == self.board[1][c] == self.board[2][c] == player:
                return True
        #Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == player:
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == player:
            return True
        return False
    
    def get_winner(self) -> PlayerStr|None:
        if self._win_check(PlayerStr.P1):
            return PlayerStr.P1
        if self._win_check(PlayerStr.P2):
            return PlayerStr.P2
        return None

    def place(self, r:int, c:int) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`         if the cell was filled successfully
                              AND does not end the game
            `CellOutOfRange`  if the provided coordinates are out of range
            `CellUnavailable` if the cell is not available
            `GameOver`        if a player has won or the game is a draw
        '''
        if r < 0 or r > 2 or c < 0 or c > 2:
            return StatusCode.CellOutOfRange
        if self.board[r][c] != None:
            return StatusCode.CellUnavailable

        self.board[r][c] = PlayerStr.P1 if self.is_P1_turn else PlayerStr.P2
        self.is_P1_turn = not self.is_P1_turn

        if self.get_winner() != None:
            return StatusCode.GameOver
        # TODO: Also check for draws
        return StatusCode.Success

    def __str__(self) -> str:
        b = [
            [' ' if cell is None else cell for cell in row]
            for row in self.board
        ]
        return '\n'.join([
            # TODO: Edit the first line if the game is over (win/draw)
            f'It is Player {1 if self.is_P1_turn else 2}\'s turn',
            '```',
            f' {b[0][0]} | {b[0][1]} | {b[0][2]} ',
            '---+---+---',
            f' {b[1][0]} | {b[1][1]} | {b[1][2]} ',
            '---+---+---',
            f' {b[2][0]} | {b[2][1]} | {b[2][2]} ',
            '```',
        ])



@dataclass
class LobbyState:
    lobby_id:int
    P1:DiscordUser|None
    P2:DiscordUser|None
    tictactoe:TicTacToe|None

    @property
    def is_empty(self) -> bool:
        return self.P1 is None and self.P2 is None

    @property
    def is_full(self) -> bool:
        return self.P1 is not None and self.P2 is not None

    @property
    def is_started(self) -> bool:
        return self.tictactoe is not None

    def __str__(self) -> str:
        strings = [f'Tic-tac-toe lobby {self.lobby_id}']

        if self.P1 == None:
            strings.append('There is no Player 1')
        else:
            strings.append(f'Player 1 ({PlayerStr.P1}) is {self.P1.name}')
        if self.P2 == None:
            strings.append('There is no Player 2')
        else:
            strings.append(f'Player 2 ({PlayerStr.P2}) is {self.P2.name}\n')

        if not self.is_started:
            strings.append('The game hasn\'t started yet')
        else:
            strings.append(str(self.tictactoe))

        return '\n'.join(strings)



class Lobbies:
    '''
    Holds and manages all tictactoe game lobbies.

    The returned `StatusCode`s listed in the documentation are listed in 
    the order they are checked in the implementation, with the exception 
    of `StatusCode.Success` always being the first listed one.
    '''
    lobby_id_to_lobby:dict[int,LobbyState] = {}
    user_to_lobby_id:dict[DiscordUser,int] = {}

    @staticmethod
    def is_in_lobby(user:DiscordUser) -> bool:
        return user in Lobbies.user_to_lobby_id

    @staticmethod
    def get_lobby_id(user:DiscordUser) -> int|None:
        if not Lobbies.is_in_lobby(user):
            return None
        return Lobbies.user_to_lobby_id[user]

    @staticmethod
    def get_next_to_move(lobby_id:int) -> DiscordUser|None:
        if lobby_id not in Lobbies.lobby_id_to_lobby:
            return None
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if not lobby.is_started:
            return None

        if lobby.tictactoe.is_P1_turn:
            return lobby.P1
        else:
            return lobby.P2

    @staticmethod
    def create(user:DiscordUser) -> int|None:
        '''
        Create a lobby for `user` who goes first by default.
        
        Returns
        -------
        The lobby id of the newly generated lobby or 
        `None` if the user is already in a lobby.
        '''
        if Lobbies.is_in_lobby(user):
            return None
        lobby_id = MEX(Lobbies.lobby_id_to_lobby)
        lobby = LobbyState(lobby_id=lobby_id, P1=user, P2=None, tictactoe=None)
        Lobbies.lobby_id_to_lobby[lobby_id] = lobby
        Lobbies.user_to_lobby_id[user] = lobby_id
        return lobby_id

    @staticmethod
    def join(lobby_id:int, user:DiscordUser) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`          if the user joined the lobby successfully
            `NonexistentLobby` if the lobby does not exist
            `InLobby`          if the user is already in a lobby
            `FullLobby`        if the lobby is already full
        '''
        if lobby_id not in Lobbies.lobby_id_to_lobby:
            return StatusCode.NonexistentLobby
        if Lobbies.is_in_lobby(user):
            return StatusCode.InLobby
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if lobby.is_full:
            return StatusCode.FullLobby

        if lobby.P1 is None:
            lobby.P1 = user
        else:
            lobby.P2 = user
        Lobbies.user_to_lobby_id[user] = lobby_id

        return StatusCode.Success

    @staticmethod
    def leave(user:DiscordUser) -> StatusCode:
        '''
        Lets a user leave a tic-tac-toe lobby.

        If the lobby was a started game, also resets the game.
        If the lobby is empty after the player leaves, also destroys 
        the lobby.
        
        Returns
        -------
        One of the following `StatusCode`s
            `Success`    if the user left the lobby successfully
            `NotInLobby` if they are not in a lobby
        '''
        if not Lobbies.is_in_lobby(user):
            return StatusCode.NotInLobby
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]

        if lobby.is_started:
            lobby.tictactoe = None
        if lobby.P1 == user:
            lobby.P1 = None
        else:
            lobby.P2 = None
        del Lobbies.user_to_lobby_id[user]
        if lobby.is_empty:
            del Lobbies.lobby_id_to_lobby[lobby_id]

        return StatusCode.Success

    @staticmethod
    def swap(user:DiscordUser) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`      if swapped successfully
            `NotInLobby`   if the user is not in a lobby
            `StartedLobby` if the user is in a started lobby
        '''
        if not Lobbies.is_in_lobby(user):
            return StatusCode.NotInLobby
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if lobby.is_started:
            return StatusCode.StartedLobby
        lobby.P1, lobby.P2 = lobby.P2, lobby.P1
        return StatusCode.Success

    @staticmethod
    def start(user:DiscordUser) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`      if the game was started successfully
            `NotInLobby`   if the user is not in a lobby
            `NotFullLobby  if the user is in a non-full lobby
            `StartedLobby` if the user is already in a started lobby
        '''
        if not Lobbies.is_in_lobby(user):
            return StatusCode.NotInLobby
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if not lobby.is_full:
            return StatusCode.NotFullLobby
        if lobby.is_started:
            return StatusCode.StartedLobby
        lobby.tictactoe = TicTacToe()
        return StatusCode.Success

    @staticmethod
    def place(user:DiscordUser, r:int, c:int) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`         if the move was done successfully
                              AND does not end the game
            `NotInLobby`      if the user is not in the lobby
            `UnstartedLobby`  if the game hasn't started
            `NotYourTurn`     if it is not the player's turn
            `CellOutOfRange`  if the provided coordinates are out of range
            `CellUnavailable` if the spot is already filled
            `GameOver`        if a player has won
        '''
        if not Lobbies.is_in_lobby(user):
            return StatusCode.NotInLobby
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]

        #Try to do the move and clean up if the game ended
        status_code = lobby.tictactoe.place(r, c)
        return status_code

    @staticmethod
    def nuke(lobby_id:int) -> None:
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        P1, P2 = lobby.P1, lobby.P2
        if P1 != None:
            del Lobbies.user_to_lobby_id[P1]
        if P2 != None:
            del Lobbies.user_to_lobby_id[P2]
        del Lobbies.lobby_id_to_lobby[lobby_id]



class RespMsg:
    '''
    A class to generate response messages related to `%tictactoe`.

    This is functionally a namespace to neatly group everything relating to 
    making the messages for the bot to send together.

    This class only handles message generation when none of the arguments are 
    invalid. For example, `%tictactoe join b` wouldn't be handled here, since 
    `b` isn't even an integer in the first place.
    '''
    @staticmethod
    def create(lobby_id:str|None, user:DiscordUser) -> str:
        '''Generates the message to send for Lobbies.create()'''
        if lobby_id != None:
            return (f"Created a lobby with id {lobby_id} for {ping(user)}\n"
                    f"Use `%tictactoe join {lobby_id}` to join")
        else:
            return f"{ping(user)}, you're already in a lobby"

    @staticmethod
    def join(status_code:StatusCode, lobby_id:int,
            user:DiscordUser) -> str|None:
        '''
        Generates the message to send for Lobbies.join().

        Returns
        -------
        The message for the status code from Lobbies.join().
        None if a status code that Lobbies.join() cannot 
        return is given.
        '''
        if status_code == StatusCode.Success:
            return f"{ping(user)} successfully joined lobby {lobby_id}"
        elif status_code == StatusCode.NonexistentLobby:
            return f"{ping(user)} no lobbies with the id {lobby_id} exist"
        elif status_code == StatusCode.InLobby:
            return (f"{ping(user)} you're already in a lobby\n"
                    "Please leave first if you want to join another lobby")
        elif status_code == StatusCode.FullLobby:
            return f"{ping(user)} sorry lobby {lobby_id} is already full"
        else:
            return None
        
    @staticmethod
    def leave(status_code:StatusCode, lobby_id:int|None, 
            user:DiscordUser) -> str|None:
        '''
        Generates the message to send for Lobbies.leave().

        Returns
        -------
        The message for the status code from Lobbies.leave().
        None if a status code that Lobbies.leave() cannot 
        return is given.
        '''
        if status_code == StatusCode.Success:
            return f"{ping(user)} has left lobby {lobby_id}"
        elif status_code == StatusCode.NotInLobby:
            return f"{ping(user)} you're not in any lobby"
        else:
            return None
        
    @staticmethod
    def swap(status_code:StatusCode, lobby_id:int|None, 
            user:DiscordUser) -> str|None:
        '''
        Generates the message to send for Lobbies.swap().

        Returns
        -------
        The message for the status code from Lobbies.swap().
        None if a status code that Lobbies.swap() cannot 
        return is given.
        '''
        if status_code == StatusCode.Success:
            return (f"{ping(user)} successfully swapped "
                    f"the players in lobby {lobby_id}")
        elif status_code == StatusCode.NotInLobby:
            return f"{ping(user)} you're not in any lobby"
        elif status_code == StatusCode.StartedLobby:
            return f"{ping(user)} you can't swap once the game has started"
        else: 
            return None
    
    @staticmethod
    def start(status_code:StatusCode, lobby_id:int|None, 
            user:DiscordUser) -> str|None:
        '''
        Generates the message to send for Lobbies.start().

        Returns
        -------
        The message for the status code from Lobbies.start().
        None if a status code that Lobbies.start() cannot 
        return is given.
        '''
        if status_code == StatusCode.Success:
            to_move_id = Lobbies.get_next_to_move(lobby_id)
            return (f"{ping(user)} started lobby {lobby_id}\n"
                    f"{ping(to_move_id)} goes first")
        elif status_code == StatusCode.NotInLobby:
            return f"{ping(user)} you're not in any lobby"
        elif status_code == StatusCode.NotFullLobby:
            return f"{ping(user)} your lobby isn't full yet"
        elif status_code == StatusCode.StartedLobby:
            return f"{ping(user)} your lobby has already started"
        else:
            return None
    
    @staticmethod
    def place(status_code:StatusCode, lobby_id:int|None,
            user:DiscordUser, row:int, col:int) -> str|None:
        '''
        Generates the message to send for Lobbies.place().

        Returns
        -------
        The message for the status code from Lobbies.place().
        None if a status code that Lobbies.place() cannot 
        return is given.
        '''
        if status_code == StatusCode.Success:
            to_move_id = Lobbies.get_next_to_move(lobby_id)
            lobby = Lobbies.lobby_id_to_lobby[lobby_id]
            return (f"{ping(user)} marked ({row},{col})\n"
                    f"{ping(to_move_id)}'s turn to move\n"
                    f"{lobby}")
        elif status_code == StatusCode.NotInLobby:
            return f"{ping(user)} you're not in any lobby"
        elif status_code == StatusCode.UnstartedLobby:
            return f"{ping(user)} your lobby hasn't started yet"
        elif status_code == StatusCode.NotYourTurn:
            return f"{ping(user)} it's not your turn"
        elif status_code == StatusCode.CellOutOfRange:
            return f"{ping(user)} that is not inside the board"
        elif status_code == StatusCode.CellUnavailable:
            return f"{ping(user)} ({row},{col}) is already marked"
        elif status_code == StatusCode.GameOver:
            lobby = Lobbies.lobby_id_to_lobby[lobby_id]
            return ("**Game over**\n"
                    f"{ping(user)} won!\n"
                    f"\n"
                    f"{lobby}")
        else:
            return None
    
    @staticmethod
    def view(user:DiscordUser) -> str:
        '''Generates the message to send for Lobbies.view()'''
        if not Lobbies.is_in_lobby(user):
            return f"{ping(user)} you're not in any lobby"
        lobby_id = Lobbies.get_lobby_id(user)
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        return f"{lobby}"


#TODO
#Make the debug message also log in my personal server for easy access
#inside stop().

@bot.command()
async def tictactoe(ctx:commands.Context, cmd:str, *args:str) -> None:
    '''
    Main command to drive the logic of %tictactoe

    If more arguments are provided than necessary, then the extra 
    arguments are simply ignored.

    The internals of this function mostly deal with parsing the arguments 
    and sending the messages out.
    
    Arguments
    ---------
    cmd : str
        The command being invoked. This is not case sensitive. 
        The inputted command must be one of
            create
            join
            leave
            swap
            start
            place
            view
    *args : str
        The arguments passed to the given sub-command
    '''
    def debug_msg() -> str:
        '''
        Generates a debug message to give information.

        Returns
        -------
        A message containing information on how the invalid state 
        was triggered.
        '''
        msg = ("Invalid state attained in %tictactoe\n"
               f"Command used: %tictactoe {cmd} {' '.join(args)}\n"
               f"Invoked by: {user.display_name} ({user.id})")
        return msg
    
    async def stop() -> None:
        '''Stops the function when an invalid state happens.'''
        msg = debug_msg()
        await ctx.send(msg)
        raise Exception(msg)

    cmd = cmd.lower()
    user:DiscordUser = ctx.author

    #Usage: `%tictactoe create`
    if cmd == 'create':
        lobby_id = Lobbies.create(user)
        msg = RespMsg.create(lobby_id, user)
        await ctx.send(msg)
        return
    
    #Usage: `%tictactoe join lobby_id`
    elif cmd == 'join':
        #Lacking arguments
        if len(args) < 1:
            await ctx.send(("Please put a lobby id to join\n"
                            "Sample usage: `%tictactoe join 21`"))
            return
        #Non-integer lobby id
        lobby_id = args[0]
        if not lobby_id.isdigit():
            await ctx.send((f"{lobby_id} is not a valid lobby id, "
                            "please use the digits 0 to 9 only"))
            return
        
        lobby_id = int(lobby_id)
        status_code = Lobbies.join(lobby_id, user)

        msg = RespMsg.join(status_code, lobby_id, user)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe leave`
    elif cmd == 'leave':
        status_code = Lobbies.leave(user)
        lobby_id = Lobbies.get_lobby_id(user)
        msg = RespMsg.leave(status_code, lobby_id, user)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe swap`
    elif cmd == 'swap':
        status_code = Lobbies.swap(user)
        lobby_id = Lobbies.get_lobby_id(user)
        msg = RespMsg.swap(status_code, lobby_id, user)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe start`
    elif cmd == 'start':
        status_code = Lobbies.start(user)
        lobby_id = Lobbies.get_lobby_id(user)
        msg = RespMsg.start(status_code, lobby_id, user)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe place row col`
    elif cmd == 'place':
        #Lacking arguments
        if len(args) < 2:
            msg = ("Please put what row and column you want to place in\n"
                   "Sample usage: `%tictactoe place 0 1")
            await ctx.send(msg)
            return
        #Non-integer row or col
        row,col = args[0],args[1]
        if not (row.isdigit() and col.isdigit()):
            msg = (f"At least one of {row}, {col} is not an integer, "
                   "please use integers from 0 to 2 only\n"
                   "Sample usage: `%tictactoe place 0 1")
            await ctx.send(msg)
            return

        row,col = int(row),int(col)
        status_code = Lobbies.place(user, row, col)
        lobby_id = Lobbies.get_lobby_id(user)
        #Generate the message before nuking the lobby
        msg = RespMsg.place(status_code, lobby_id, user, row, col)
        if status_code == StatusCode.GameOver:
            Lobbies.nuke(lobby_id)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe view`
    elif cmd == 'view':
        msg = RespMsg.view(user)
        await ctx.send(msg)
    
    #Invalid tic-tac-toe subcommand given
    else:
        msg = (f"{cmd} is not a valid tictactoe subcommand\n"
               f"Please use %help for more info")
        await ctx.send(msg)
