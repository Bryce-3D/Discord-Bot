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
- %tictactoe place does not properly check whose turn it is and you can move 
  for your opponent
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

    def get_player_to_move(self) -> DiscordUser|None:
        if not self.is_started:
            return None
        return self.P1 if self.tictactoe.is_P1_turn else self.P2

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

    Public functions return the msg to be sent by the discord bot.
    '''
    # TODO: Abstract out common responses such as "you're not in a lobby"
    # out into a class attribute or something similar

    lobby_id_to_lobby:dict[int,LobbyState] = {}
    user_to_lobby_id:dict[DiscordUser,int] = {}

    @staticmethod
    def _is_in_lobby(user:DiscordUser) -> bool:
        return user in Lobbies.user_to_lobby_id

    @staticmethod
    def _nuke(lobby_id:int) -> None:
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        P1, P2 = lobby.P1, lobby.P2
        if P1 != None:
            del Lobbies.user_to_lobby_id[P1]
        if P2 != None:
            del Lobbies.user_to_lobby_id[P2]
        del Lobbies.lobby_id_to_lobby[lobby_id]

    @staticmethod
    def create(user:DiscordUser) -> str:
        '''Create a lobby for `user` who goes first by default.'''
        if Lobbies._is_in_lobby(user):
            return f"{ping(user)} you're already in a lobby"

        lobby_id = MEX(Lobbies.lobby_id_to_lobby)
        lobby = LobbyState(lobby_id=lobby_id, P1=user, P2=None, tictactoe=None)
        Lobbies.lobby_id_to_lobby[lobby_id] = lobby
        Lobbies.user_to_lobby_id[user] = lobby_id

        return (
            f"Created a lobby with id {lobby_id} for {ping(user)}\n"
            f"Use `%tictactoe join {lobby_id}` to join"
        )

    @staticmethod
    def join(lobby_id:int, user:DiscordUser) -> str:
        if Lobbies._is_in_lobby(user):
            return (
                f"{ping(user)} you're already in a lobby\n"
                "Please leave first if you want to join another lobby"
            )
        if lobby_id not in Lobbies.lobby_id_to_lobby:
            return f"{ping(user)} no lobbies with the id {lobby_id} exist"

        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if lobby.is_full:
            return f"{ping(user)} sorry lobby {lobby_id} is already full"

        if lobby.P1 is None:
            lobby.P1 = user
        else:
            lobby.P2 = user
        Lobbies.user_to_lobby_id[user] = lobby_id

        return f"{ping(user)} successfully joined lobby {lobby_id}"

    @staticmethod
    def leave(user:DiscordUser) -> str:
        '''
        Lets a user leave a tic-tac-toe lobby.

        If the lobby was a started game, also resets the game.
        If the lobby is empty after the player leaves, also deletes the lobby.
        '''
        if not Lobbies._is_in_lobby(user):
            return f"{ping(user)} you're not in any lobby"
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

        return f"{ping(user)} has left lobby {lobby_id}"

    @staticmethod
    def swap(user:DiscordUser) -> str:
        '''Swap Players 1 and 2 in `user`'s lobby'''
        if not Lobbies._is_in_lobby(user):
            return f"{ping(user)} you're not in any lobby"
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if lobby.is_started:
            return f"{ping(user)} you can't swap once the game has started"
        lobby.P1, lobby.P2 = lobby.P2, lobby.P1
        return f"{ping(user)} successfully swapped players in lobby {lobby_id}"

    @staticmethod
    def start(user:DiscordUser) -> str:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`      if the game was started successfully
            `NotInLobby`   if the user is not in a lobby
            `NotFullLobby  if the user is in a non-full lobby
            `StartedLobby` if the user is already in a started lobby
        '''
        if not Lobbies._is_in_lobby(user):
            return f"{ping(user)} you're not in any lobby"
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if not lobby.is_full:
            return f"{ping(user)} your lobby isn't full yet"
        if lobby.is_started:
            return f"{ping(user)} your lobby has already started"

        lobby.tictactoe = TicTacToe()
        return (
            f"{ping(user)} started lobby {lobby_id}\n"
            f"{ping(lobby.P1)} goes first"
        )

    @staticmethod
    def place(user:DiscordUser, r:int, c:int) -> str:
        # TODO: Handle draws properly
        if not Lobbies._is_in_lobby(user):
            return f"{ping(user)} you're not in any lobby"

        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if not lobby.is_started:
            return f"{ping(user)} your lobby hasn't started yet"

        current_to_move = lobby.get_player_to_move()
        if user != current_to_move:
            return f"{ping(user)} it's not your turn"

        status_code = lobby.tictactoe.place(r, c)
        if status_code == StatusCode.CellOutOfRange:
            return f"{ping(user)} that is not inside the board"
        if status_code == StatusCode.CellUnavailable:
            return f"{ping(user)} ({r},{c}) is already marked"

        if status_code == StatusCode.GameOver:
            Lobbies._nuke(lobby_id)
            return '\n'.join([
                "**Game over**",
                f"{ping(user)} won!",
                "",
                f"{lobby}",
            ])
        
        if status_code == StatusCode.Success:
            next_to_move = lobby.get_player_to_move()
            return '\n'.join([
                f"{ping(current_to_move)} marked ({r},{c})",
                f"{ping(next_to_move)}'s turn to move",
                f"{lobby}",
            ])

        raise Exception(f'Unexpected status code received: {status_code}')

    @staticmethod
    def view(user:DiscordUser) -> str:
        '''Let a user view their lobby'''
        if not Lobbies._is_in_lobby(user):
            return f"{ping(user)} you're not in any lobby"
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        return str(lobby)



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
    cmd = cmd.lower()
    user:DiscordUser = ctx.author

    #Usage: `%tictactoe create`
    if cmd == 'create':
        msg = Lobbies.create(user)
        await ctx.send(msg)
        return
    
    #Usage: `%tictactoe join lobby_id`
    elif cmd == 'join':
        #Lacking arguments
        if len(args) < 1:
            await ctx.send(
                "Please put a lobby id to join\n"
                "Sample usage: `%tictactoe join 21`"
            )
            return
        #Non-integer lobby id
        lobby_id = args[0]
        if not lobby_id.isdigit():
            await ctx.send(
                f"{lobby_id} is not a valid lobby id, please use the digits only"
            )
            return
        
        lobby_id = int(lobby_id)
        msg = Lobbies.join(lobby_id, user)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe leave`
    elif cmd == 'leave':
        msg = Lobbies.leave(user)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe swap`
    elif cmd == 'swap':
        msg = Lobbies.swap(user)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe start`
    elif cmd == 'start':
        msg = Lobbies.start(user)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe place row col`
    elif cmd == 'place':
        #Lacking arguments
        if len(args) < 2:
            await ctx.send(
                "Please put what row and column you want to place in\n"
                "Sample usage: `%tictactoe place 0 1"
            )
            return
        #Non-integer row or col
        row,col = args[0],args[1]
        if not (row.isdigit() and col.isdigit()):
            await ctx.send(
                f"At least one of {row}, {col} is not an integer, "
                "please use integers from 0 to 2 only\n"
                "Sample usage: `%tictactoe place 0 1"
            )
            return

        row,col = int(row),int(col)
        msg = Lobbies.place(user, row, col)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe view`
    elif cmd == 'view':
        msg = Lobbies.view(user)
        await ctx.send(msg)
        return
    
    #Invalid tic-tac-toe subcommand given
    else:
        await ctx.send(
            f"{cmd} is not a valid tictactoe subcommand\n"
            f"Please use %help for more info"
        )
