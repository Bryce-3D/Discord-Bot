from dataclasses import dataclass
from discord.ext import commands
from enum import IntEnum, StrEnum

from Kumiko.bot_config import bot
from Kumiko.util import channel_str, ping
from Kumiko.types import DiscordChannel, DiscordUser

# TODO: Make lobbies tied to channels rather than using a lobby id

class StatusCode(IntEnum):
    '''Status Codes used to manage Tic-Tac-Toe'''
    SuccessAndNotGameOver = 0
    CellOutOfRange        = 1
    CellUnavailable       = 2
    GameOverNotTied       = 3
    GameOverTied          = 4



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

    @property
    def _number_of_filled_cells(self):
        return sum([
            sum([cell is not None for cell in row])
            for row in self.board
        ])
    
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

    def place(self, row:int, col:int) -> StatusCode:
        '''Let the next player place on row `r` and column `c`'''
        if self.get_winner() is not None:
            raise Exception('Cannot place when the game is already over')

        if row < 0 or row > 2 or col < 0 or col > 2:
            return StatusCode.CellOutOfRange
        if self.board[row][col] != None:
            return StatusCode.CellUnavailable

        self.board[row][col] = PlayerStr.P1 if self.is_P1_turn else PlayerStr.P2
        self.is_P1_turn = not self.is_P1_turn

        if self.get_winner() is not None:
            return StatusCode.GameOverNotTied
        if self._number_of_filled_cells == 9:
            return StatusCode.GameOverTied
        return StatusCode.SuccessAndNotGameOver

    def __str__(self) -> str:
        winner = self.get_winner()
        if winner is not None:
            header = f'Player {1 if winner == PlayerStr.P1 else 2} wins'
        elif self._number_of_filled_cells == 9:
            header = 'Game tied'
        else:
            header = f'It is Player {1 if self.is_P1_turn else 2}\'s turn'

        board_str = [
            [' ' if cell is None else cell for cell in row]
            for row in self.board
        ]

        return '\n'.join([
            header,
            '```',
            f' {board_str[0][0]} | {board_str[0][1]} | {board_str[0][2]} ',
            '---+---+---',
            f' {board_str[1][0]} | {board_str[1][1]} | {board_str[1][2]} ',
            '---+---+---',
            f' {board_str[2][0]} | {board_str[2][1]} | {board_str[2][2]} ',
            '```',
        ])



@dataclass
class LobbyState:
    channel:DiscordChannel
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

    def is_in(self, user:DiscordUser) -> bool:
        return self.P1 == user or self.P2 == user

    def get_player_to_move(self) -> DiscordUser|None:
        if not self.is_started:
            return None
        return self.P1 if self.tictactoe.is_P1_turn else self.P2

    def __str__(self) -> str:
        strings = [f'Tic-tac-toe lobby in {channel_str(self.channel)}']

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

    channel_to_lobby:dict[DiscordChannel,LobbyState] = {}

    @staticmethod
    def _is_in_lobby(channel:DiscordChannel, user:DiscordUser) -> bool:
        if channel not in Lobbies.channel_to_lobby:
            return False
        lobby = Lobbies.channel_to_lobby[channel]
        return lobby.is_in(user)

    @staticmethod
    def _init_lobby(channel:DiscordChannel) -> LobbyState:
        '''Does all the setup associated with making a lobby'''
        lobby = LobbyState(
            channel=channel,
            P1=None,
            P2=None,
            tictactoe=None,
        )
        Lobbies.channel_to_lobby[channel] = lobby
        return lobby

    @staticmethod
    def _nuke(channel:DiscordChannel) -> None:
        '''Does all the cleanup associated with nuking a lobby'''
        if channel not in Lobbies.channel_to_lobby:
            return
        del Lobbies.channel_to_lobby[channel]

    @staticmethod
    def join(channel:DiscordChannel, user:DiscordUser) -> str:
        if Lobbies._is_in_lobby(channel, user):
            return f"{ping(user)} you're already in this lobby"

        if channel not in Lobbies.channel_to_lobby:
            lobby = Lobbies._init_lobby(channel)
        else:
            lobby = Lobbies.channel_to_lobby[channel]

        if lobby.is_full:
            return f"Sorry {ping(user)}, the lobby in {channel_str(channel)} is already full"

        if lobby.P1 is None:
            lobby.P1 = user
        else:
            lobby.P2 = user
        return f"{ping(user)} joined the lobby in {channel_str(channel)}"

    @staticmethod
    def leave(channel:DiscordChannel, user:DiscordUser) -> str:
        '''
        Lets a user leave a tic-tac-toe lobby.

        If the lobby was a started game, also resets the game.
        If the lobby is empty after the player leaves, also deletes the lobby.
        '''
        if not Lobbies._is_in_lobby(channel, user):
            return f"{ping(user)} you're not in the lobby for {channel_str(channel)}"
        lobby = Lobbies.channel_to_lobby[channel]

        if lobby.P1 == user:
            lobby.P1 = None
        else:
            lobby.P2 = None
        if lobby.is_started:
            lobby.tictactoe = None
        if lobby.is_empty:
            Lobbies._nuke(channel)

        return f"{ping(user)} has left the lobby in {channel_str(channel)}"

    @staticmethod
    def swap(channel:DiscordChannel, user:DiscordUser) -> str:
        '''Swap Players 1 and 2'''
        if not Lobbies._is_in_lobby(channel, user):
            return f"{ping(user)} you're not in the lobby in {channel_str(channel)}"
        lobby = Lobbies.channel_to_lobby[channel]
        if lobby.is_started:
            return f"{ping(user)} you can't swap once the game has started"
        lobby.P1, lobby.P2 = lobby.P2, lobby.P1
        return f"{ping(user)} successfully swapped players in the lobby"

    @staticmethod
    def start(channel:DiscordChannel, user:DiscordUser) -> str:
        if not Lobbies._is_in_lobby(channel, user):
            return f"{ping(user)} you're not in the lobby in {channel_str(channel)}"
        lobby = Lobbies.channel_to_lobby[channel]
        if not lobby.is_full:
            return f"{ping(user)} the lobby isn't full yet"
        if lobby.is_started:
            return f"{ping(user)} the lobby has already started"

        lobby.tictactoe = TicTacToe()
        return (
            f"{ping(user)} started the lobby in {channel_str(channel)}\n"
            f"{ping(lobby.P1)} goes first"
        )

    @staticmethod
    def place(channel:DiscordChannel, user:DiscordUser, row:int, col:int) -> str:
        if not Lobbies._is_in_lobby(channel, user):
            return f"{ping(user)} you're not in the lobby in {channel_str(channel)}"

        lobby = Lobbies.channel_to_lobby[channel]
        if not lobby.is_started:
            return f"{ping(user)} the lobby hasn't started yet"

        current_to_move = lobby.get_player_to_move()
        if user != current_to_move:
            return f"{ping(user)} it's not your turn"

        status_code = lobby.tictactoe.place(row, col)
        if status_code == StatusCode.CellOutOfRange:
            return f"{ping(user)} that is not inside the board"
        if status_code == StatusCode.CellUnavailable:
            return f"{ping(user)} ({row},{col}) is already marked"

        if status_code == StatusCode.GameOverNotTied:
            Lobbies._nuke(channel)
            return '\n'.join([
                "**Game over**",
                f"{ping(user)} won!",
                "",
                f"{lobby}",
            ])

        if status_code == StatusCode.GameOverTied:
            Lobbies._nuke(channel)
            return '\n'.join([
                "**Game over**",
                "",
                f"{lobby}",
            ])
        
        if status_code == StatusCode.SuccessAndNotGameOver:
            next_to_move = lobby.get_player_to_move()
            return '\n'.join([
                f"{ping(current_to_move)} marked ({row},{col})",
                f"{ping(next_to_move)}'s turn to move",
                f"{lobby}",
            ])

        raise Exception(f'Unexpected status code received: {status_code}')

    @staticmethod
    def view(channel:DiscordChannel) -> str:
        if channel not in Lobbies.channel_to_lobby:
            return f"There is currently no lobby in {channel_str(channel)}"
        lobby = Lobbies.channel_to_lobby[channel]
        return str(lobby)



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
        The sub-command being invoked. This is not case sensitive.
    *args : str
        The arguments passed to the given sub-command
    '''
    cmd = cmd.lower()
    user:DiscordUser = ctx.author
    channel:DiscordChannel = ctx.channel
    
    #Usage: `%tictactoe join`
    if cmd == 'join':
        msg = Lobbies.join(channel, user)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe leave`
    elif cmd == 'leave':
        msg = Lobbies.leave(channel, user)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe swap`
    elif cmd == 'swap':
        msg = Lobbies.swap(channel, user)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe start`
    elif cmd == 'start':
        msg = Lobbies.start(channel, user)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe place row col`
    elif cmd == 'place':
        #Lacking arguments
        if len(args) < 2:
            await ctx.send("Please put the row and column you want to place in")
            return
        #Non-integer row or col
        row,col = args[0],args[1]
        if not (row.isdigit() and col.isdigit()):
            await ctx.send(f"At least one of {row=}, {col=} is not an integer")
            return

        row,col = int(row),int(col)
        msg = Lobbies.place(channel, user, row, col)
        await ctx.send(msg)
        return

    #Usage: `%tictactoe view`
    elif cmd == 'view':
        msg = Lobbies.view(channel)
        await ctx.send(msg)
        return
    
    #Invalid tic-tac-toe subcommand given
    else:
        await ctx.send(f"{cmd} is not a valid tictactoe subcommand\n")
