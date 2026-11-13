import discord
from discord.ext import commands
from enum import IntEnum, StrEnum

from Kumiko.bot_config import bot
from Kumiko.util import MEX,ping

# TODO: Make lobbies tied to channels rather than using a lobby id
# TODO: Clean out unnecesary comments
# TODO: Go over suggestions in tictactoe comments.txt and delete that file when done
# TODO: Bug fixes obv
# TODO: Raise exceptions instead of returning status codes (?)

'''
Buglist
- %tictactoe leave raises "Cannot send an empty message"
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

    # TODO: Delete this function and reinitialize on restart instead
    def restart(self) -> None:
        for r in range(3):
            for c in range(3):
                self.board[r][c] = None
        self.is_P1_turn = True

    def __str__(self) -> str:
        b = [
            [' ' if cell is None else cell for cell in row]
            for row in self.board
        ]
        return (
            f' {b[0][0]} | {b[0][1]} | {b[0][2]} \n'
            '---+---+---\n'
            f' {b[1][0]} | {b[1][1]} | {b[1][2]} \n'
            '---+---+---\n'
            f' {b[2][0]} | {b[2][1]} | {b[2][2]} \n'
        )

# TODO: Make an unstarted lobby have self.tictactoe = None and delete 
#  self.is_started or make it an @property
class Lobby:
    '''
    A class to represent a tic-tac-toe game lobby.

    The returned `StatusCode`s listed in the documentation are listed in 
    the order they are checked in the implementation, with the exception 
    of `StatusCode.Success` always being the first listed one.
    '''
    def __init__(self, lobby_id:int, P1:discord.User|discord.Member|None,
            P2:discord.User|discord.Member|None):
        self.tictactoe:TicTacToe = TicTacToe()
        self.lobby_id:int = lobby_id
        self.P1:discord.User|discord.Member|None = P1
        self.P2:discord.User|discord.Member|None = P2
        self.is_started:bool = False
    
    @property
    def player_count(self) -> int:
        return (self.P1 is not None) + (self.P2 is not None)

    def is_in(self, player:discord.User|discord.Member) -> bool:
        return self.P1 == player or self.P2 == player

    def add_player(self, player:discord.User|discord.Member) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`   if the player was added successfully
            `InLobby`   if the player is already in the lobby
            `FullLobby` if the lobby is already full
        '''
        if self.is_in(player):
            return StatusCode.InLobby
        if self.player_count == 2:
            return StatusCode.FullLobby

        if self.P1 is None:
            self.P1 = player
        else:
            self.P2 = player
        return StatusCode.Success
    
    def remove_player(self, player:discord.User|discord.Member) -> StatusCode:
        '''
        Removes a player and resets the game if it was started.

        Returns
        -------
        One of the following `StatusCode`s
            'Success'      if the player was removed successfully
            'NotInLobby'   if the player doesn't exist
        '''
        if self.is_started:
            self.reset()
        if not self.is_in(player):
            return StatusCode.NotInLobby

        if self.P1 == player:
            self.P1 = None
        else:
            self.P2 = None
        return StatusCode.Success

    def swap_players(self) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`      if the swap was successful
            `StartedLobby` if the lobby was already started
        '''
        if self.is_started:
            return StatusCode.StartedLobby
        self.P1, self.P2 = self.P2, self.P1
        return StatusCode.Success

    def start(self) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`      if the game was started successfully
            `NotFullLobby` if the lobby was not full
            `StartedLobby` if the lobby has already started
        '''
        if self.player_count != 2:
            return StatusCode.NotFullLobby
        if self.is_started:
            return StatusCode.StartedLobby
        self.is_started = True
        return StatusCode.Success
    
    def get_next_to_move(self) -> discord.User|discord.Member|None:
        if not self.is_started:
            return None
        if self.tictactoe.is_P1_turn:
            return self.P1
        else:
            return self.P2

    def reset(self) -> None:
        '''Resets the state of the game while keeping the players in'''
        # TODO: Deprecate restart() and reinitialize/set to None
        self.tictactoe.restart()
        self.is_started = False
    
    def place(self, player:discord.User|discord.Member, r:int, c:int
            ) -> StatusCode:
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
        if not self.is_in(player):
            return StatusCode.NotInLobby
        if not self.is_started:
            return StatusCode.UnstartedLobby

        if self.tictactoe.is_P1_turn and self.P2 == player:
            return StatusCode.NotYourTurn
        if not self.tictactoe.is_P1_turn and self.P1 == player:
            return StatusCode.NotYourTurn
        
        return self.tictactoe.place(r,c)

    def __str__(self) -> str:
        s = f'Tic-tac-toe lobby {self.lobby_id}\n'
        if self.P1 == None:
            s += 'There is currently no Player X\n'
        else:
            s += f'Player 1 ({PlayerStr.P1}) is {self.P1.name}\n'
        if self.P2 == None:
            s += 'There is currently no Player O\n'
        else:
            s += f'Player 2 ({PlayerStr.P2}) is {self.P2.name}\n'
        s += '\n'
        
        if not self.is_started:
            s += 'The game hasn\'t started yet'
            return s

        player_to_move = self.P1 if self.tictactoe.is_P1_turn else self.P2
        s += f"{player_to_move.name} to move"
        s += f'```\n{self.tictactoe}```\n'
        return s

class Lobbies:
    '''
    A class to represent the set of all tictactoe lobbies.

    This is functionally a namespace to neatly group everything relating to 
    the set of all lobbies together.

    The returned `StatusCode`s listed in the documentation are listed in 
    the order they are checked in the implementation, with the exception 
    of `StatusCode.Success` always being the first listed one.
    '''
    #lobby_id_to_lobby[i] = lobby number i
    lobby_id_to_lobby:dict[int,Lobby] = {}
    #user_to_lobby_id[user] = lobby id of user
    user_to_lobby_id:dict[discord.User|discord.Member,int] = {}

    @staticmethod
    def is_in_some_lobby(user:discord.User|discord.Member) -> bool:
        return user in Lobbies.user_to_lobby_id

    @staticmethod
    def lobby_create(user:discord.User|discord.Member) -> int|None:
        '''
        Create a lobby for `user` who goes first by default.
        
        Returns
        -------
        The lobby id of the newly generated lobby or 
        `None` if the user is already in a lobby.
        '''
        if Lobbies.is_in_some_lobby(user):
            return None
        lobby_id = MEX(Lobbies.lobby_id_to_lobby)
        lobby = Lobby(lobby_id, P1=user, P2=None)
        Lobbies.lobby_id_to_lobby[lobby_id] = lobby
        Lobbies.user_to_lobby_id[user] = lobby_id
        return lobby_id

    @staticmethod
    def get_lobby_id(user:discord.User|discord.Member) -> int|None:
        if not Lobbies.is_in_some_lobby(user):
            return None
        return Lobbies.user_to_lobby_id[user]

    @staticmethod
    def get_next_to_move(lobby_id:int) -> discord.User|discord.Member|None:
        if lobby_id not in Lobbies.lobby_id_to_lobby:
            return None
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        return lobby.get_next_to_move()

    @staticmethod
    def join(lobby_id:int, user:discord.User|discord.Member) -> StatusCode:
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
        if Lobbies.is_in_some_lobby(user):
            return StatusCode.InLobby
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if lobby.player_count == 2:
            return StatusCode.FullLobby
        lobby.add_player(user)
        Lobbies.user_to_lobby_id[user] = lobby_id
        return StatusCode.Success

    @staticmethod
    def leave(user:discord.User|discord.Member) -> StatusCode:
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
        if not Lobbies.is_in_some_lobby(user):
            return StatusCode.NotInLobby
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]

        if lobby.is_started:
            lobby.reset()
        lobby.remove_player(user)
        del Lobbies.user_to_lobby_id[user]
        if lobby.player_count == 0:
            del Lobbies.lobby_id_to_lobby[lobby_id]

    @staticmethod
    def swap(user:discord.User|discord.Member) -> StatusCode:
        '''
        Swaps P1 and P2 in the lobby of `user`
        
        Returns
        -------
        One of the following `StatusCode`s
            `Success`      if swapped successfully
            `NotInLobby`   if the user is not in a lobby
            `StartedLobby` if the user is in a started lobby
        '''
        if not Lobbies.is_in_some_lobby(user):
            return StatusCode.NotInLobby
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if lobby.is_started:
            return StatusCode.StartedLobby
        lobby.swap_players()
        return StatusCode.Success

    @staticmethod
    def start(user:discord.User|discord.Member) -> StatusCode:
        '''
        Returns
        -------
        One of the following `StatusCode`s
            `Success`      if the game was started successfully
            `NotInLobby`   if the user is not in a lobby
            `NotFullLobby  if the user is in a non-full lobby
            `StartedLobby` if the user is already in a started lobby
        '''
        if not Lobbies.is_in_some_lobby(user):
            return StatusCode.NotInLobby
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]
        if lobby.player_count != 2:
            return StatusCode.NotFullLobby
        if lobby.is_started:
            return StatusCode.StartedLobby
        lobby.start()
        return StatusCode.Success

    @staticmethod
    def place(user:discord.User|discord.Member, r:int, c:int) -> StatusCode:
        '''
        Lets the user place their mark on (r,c)
        
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
        if not Lobbies.is_in_some_lobby(user):
            return StatusCode.NotInLobby
        lobby_id = Lobbies.user_to_lobby_id[user]
        lobby = Lobbies.lobby_id_to_lobby[lobby_id]

        #Try to do the move and clean up if the game ended
        status_code = lobby.place(user, r, c)
        # if status_code == StatusCode.GameOver:
        #     del Lobbies.user_to_lobby_id[lobby.P1]
        #     del Lobbies.user_to_lobby_id[lobby.P2]
        #     del Lobbies.lobby_id_to_lobby[lobby_id]
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
    def create(lobby_id:str|None, user:discord.User|discord.Member) -> str:
        '''Generates the message to send for Lobbies.create()'''
        if lobby_id != None:
            return (f"Created a lobby with id {lobby_id} for {ping(user)}\n"
                    f"Use `%tictactoe join {lobby_id}` to join")
        else:
            return f"{ping(user)}, you're already in a lobby"

    @staticmethod
    def join(status_code:StatusCode, lobby_id:int,
            user:discord.User|discord.Member) -> str|None:
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
            user:discord.User|discord.Member) -> str|None:
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
            user:discord.User|discord.Member) -> str|None:
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
            user:discord.User|discord.Member) -> str|None:
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
            user:discord.Member|discord.User, row:int, col:int) -> str|None:
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
    def view(user:discord.User|discord.Member) -> str:
        '''Generates the message to send for Lobbies.view()'''
        if not Lobbies.is_in_some_lobby(user):
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
    user:discord.User|discord.Member = ctx.author

    #Usage: `%tictactoe create`
    if cmd == 'create':
        lobby_id = Lobbies.lobby_create(user)
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
