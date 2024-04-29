from Kumiko.bot_config import bot, commands
from enum import IntEnum
from Kumiko.util import MEX,ping

class TTTStatusCode(IntEnum):
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

class TicTacToe:
    '''
    A class to represent the state of a tic-tac-toe game.

    Contains the tic-tac-toe board as well as a lot of helper functions to 
    make it easier to use. X always goes before O in this implementation.

    The returned `TTTStatusCode`s listed in the documentation are listed in 
    the order they are checked in the implementation, with the exception 
    of `TTTStatusCode.Success` always being the first listed one.

    Attributes
    ----------
    board : list[list[str]]
        The 3x3 tic-tac-toe board
    filled : int
        The number of cells in the board filled so far.
    '''
    def __init__(self):
        '''Initialize a game of tic-tac-toe'''
        self.board:list[list[str]] = [
            [' ' for c in range(3)] for r in range(3)
        ]
        self.filled = 0
    
    def win_check(self, player:str) -> bool:
        '''
        Checks if the specified player has won the game.

        Parameters
        ----------
        player : str
            The specified player. either 'X' or 'O'

        Returns
        -------
        True if player has a line on the board, False otherwise

        Raises
        ------
        Exception() if the player is not `X` or `O`.
        '''
        if player not in {'X','O'}:
            err_msg  = f'TicTacToe.win_check({player}) '
            err_msg += 'is an invalid function call'
            raise Exception(err_msg)
        
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
    
    def get_winner(self) -> str|None:
        '''
        Gets the winner of the Tic-Tac-Toe game.

        Returns
        -------
        'X' or 'O' if one of them has won the game.
        `None` if no one has won yet.
        '''
        if self.win_check('X'):
            return 'X'
        if self.win_check('O'):
            return 'O'
        return None

    def get_turn(self) -> str:
        '''
        Returns whose turn it currently is

        Returns
        -------
        'X' is it is player X's turn, 'O' otherwise
        '''
        return 'X' if self.filled%2 == 0 else 'O'

    def place(self, r:int, c:int) -> TTTStatusCode:
        '''
        Place an X or O in (r,c) depending on whose turn it is
        
        Parameters
        ----------
        r : int
            The row number of the cell being filled
        c : int
            The col number of the cell being filled
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`         if the cell was filled successfully
            `CellOutOfRange`  if the provided coordinates are out of range
            `CellUnavailable` if the cell is not available
        '''
        if r < 0 or r > 2 or c < 0 or c > 2:
            return TTTStatusCode.CellOutOfRange
        if self.board[r][c] != ' ':
            return TTTStatusCode.CellUnavailable
        #Use the parity of self.filled to determine the player
        self.board[r][c] = self.get_turn()
        self.filled += 1
        return TTTStatusCode.Success
    
    def restart(self) -> None:
        '''Restarts the game state'''
        for r in range(3):
            for c in range(3):
                self.board[r][c] = ' '
        self.filled = 0

    def __str__(self) -> str:
        '''Returns a string representation of the board state'''
        b = self.board
        s = (f' {b[0][0]} | {b[0][1]} | {b[0][2]} \n'
             '---+---+---\n'
             f' {b[1][0]} | {b[1][1]} | {b[1][2]} \n'
             '---+---+---\n'
             f' {b[2][0]} | {b[2][1]} | {b[2][2]} \n')
        return s

class TicTacToeLobby:
    '''
    A class to represent a tic-tac-toe game lobby.

    The returned `TTTStatusCode`s listed in the documentation are listed in 
    the order they are checked in the implementation, with the exception 
    of `TTTStatusCode.Success` always being the first listed one.

    Attributes
    ----------
    tictactoe : Tictactoe
        The tic-tac-toe board.
    lobby_id : int
        The id of this lobby.
    player_count : int
        The number of players currently in the lobby.
    X_id : int|None
        The discord id of player X. Set to None if they don't exist.
    O_id : int|None
        The discord id of player O. Set to None if they don't exist.
    X_name : str|None
        The discord name of player X. Set to None if they don't exist.
    O_name : str|None
        The discord name of player O. Set to None if they don't exist.
    is_started : bool
        True if the game has been started, False otherwise.
    '''
    def __init__(self, lobby_id:int, X_id:int|None=None, O_id:int|None=None, 
                 X_name:str|None=None, O_name:str|None=None):
        self.tictactoe:TicTacToe = TicTacToe()
        self.lobby_id:int = lobby_id
        self.X_id:int|None = X_id
        self.O_id:int|None = O_id
        self.X_name:str|None = X_name
        self.O_name:str|None = O_name
        self.is_started:bool = False
    
    @property
    def player_count(self) -> int:
        '''The number of players in the lobby'''
        ans = 0
        if self.X_id != None:
            ans += 1
        if self.O_id != None:
            ans += 1
        return ans

    def is_in(self, id:int) -> bool:
        '''
        Checks if a given user is in the lobby.

        Parameters
        ----------
        id : int
            The discord id of the user being checked.
        
        Returns
        -------
        True if the user is in the lobby, False otherwise.
        '''
        return self.X_id == id or self.O_id == id

    def add_player(self, id:int, name:str) -> TTTStatusCode:
        '''
        Adds a player to the game.

        Parameters
        ----------
        id : int
            The discord id of the user being added
        name : str
            The discord name of the user being added

        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`   if the player was added successfully
            `FullLobby` if the lobby is already full
            `InLobby`   if the player is already in the lobby
        '''
        if self.player_count == 2:
            return TTTStatusCode.FullLobby
        if self.is_in(id):
            return TTTStatusCode.InLobby
        if self.X_id == None:
            self.X_id = id
            self.X_name = name
        else:
            self.O_id = id
            self.O_name = name
        return TTTStatusCode.Success
    
    def remove_player(self, id:int) -> TTTStatusCode:
        '''
        Removes a player from a game.

        Also automatically resets the lobby if the lobby was started.

        Parameters
        ----------
        id : int
            The discord id of the user being removed

        Returns
        -------
        One of the following `TTTStatusCode`s
            'Success'      if the player was removed successfully
            'NotInLobby'   if the player doesn't exist
        '''
        if self.is_started:
            self.reset()
        if self.O_id == id:
            self.O_id = None
            self.O_name = None
            return TTTStatusCode.Success
        if self.X_id == id:
            self.X_id = None
            self.X_name = None
            return TTTStatusCode.Success
        return TTTStatusCode.NotInLobby

    def swap_players(self) -> TTTStatusCode:
        '''
        Swap Player X and Player O.
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`      if the swap was successful
            `StartedLobby` if the lobby was already started
        '''
        if self.is_started:
            return TTTStatusCode.StartedLobby
        self.X_id,self.O_id = self.O_id,self.X_id
        self.X_name,self.O_name = self.O_name,self.X_name
        return TTTStatusCode.Success

    def start(self) -> TTTStatusCode:
        '''
        Starts the game.
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`      if the game was started successfully
            `NotFullLobby` if the lobby was not full
            `StartedLobby` if the lobby has already started
        '''
        if self.player_count != 2:
            return TTTStatusCode.NotFullLobby
        if self.is_started:
            return TTTStatusCode.StartedLobby
        self.is_started = True
        return TTTStatusCode.Success
    
    def get_next_to_move(self) -> int|None:
        '''
        Returns the discord id of the next person to move.

        Returns
        -------
        The discord id of the next person to move if the game has started 
        or `None` if the game has not started.
        '''
        if not self.is_started:
            return None
        if self.tictactoe.get_turn() == 'X':
            return self.X_id
        else:
            return self.O_id

    def reset(self) -> None:
        '''Resets the state of the game while keeping the players in'''
        self.tictactoe.restart()
        self.is_started = False
    
    def place(self, id:int, r:int, c:int) -> TTTStatusCode:
        '''
        Lets the user with discord id `id` put at (r,c).

        Assumes that the user id passed is inside the lobby.

        Parameters
        ----------
        id : int
            Discord id of the player trying to place a mark
        r : int
            The row number
        c : int
            The col number
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`         if the move was done successfully
            `NotInLobby`      if the user is not in the lobby
            `UnstartedLobby`  if the game hasn't started
            `NotYourTurn`     if it is not the player's turn
            `CellOutOfRange`  if the provided coordinates are out of range
            `CellUnavailable` if the spot is already filled
        '''
        #User is not in the lobby (should not happen)
        if not self.is_in(id):
            return TTTStatusCode.NotInLobby
        if not self.is_started:
            return TTTStatusCode.UnstartedLobby

        #O moved during X's turn
        if self.tictactoe.get_turn() == 'X' and self.O_id == id:
            return TTTStatusCode.NotYourTurn
        #X moved during O's turn
        if self.tictactoe.get_turn() == 'O' and self.X_id == id:
            return TTTStatusCode.NotYourTurn
        
        #Try to do the move and return the status code
        return self.tictactoe.place(r,c)

    def __str__(self) -> str:
        '''Returns a string representation of the game state'''
        s = f'Tic-tac-toe lobby {self.lobby_id}\n'
        if self.X_id == None:
            s += 'There is currently no Player X\n'
        else:
            s += f'Player X is {self.X_name}\n'
        if self.O_id == None:
            s += 'There is currently no Player O\n'
        else:
            s += f'Player O is {self.O_name}\n'
        s += '\n'
        
        if not self.is_started:
            s += 'The game hasn\'t started yet'
            return s

        s += f"{self.tictactoe.get_turn} to move"
        s += f'```\n{self.tictactoe}```\n'
        return s

class TicTacToeLobbies:
    '''
    A class to represent the set of all lobbies.

    This is functionally a namespace to neatly group everything relating to 
    the set of all lobbies together.

    The returned `TTTStatusCode`s listed in the documentation are listed in 
    the order they are checked in the implementation, with the exception 
    of `TTTStatusCode.Success` always being the first listed one.

    Attributes
    ----------
    lobby_id_to_lobby : dict[int,TicTacToeLobby]
        A dictionary mapping a lobby id to the corresponding lobby.
    user_to_lobby_id : dict[int,int]
        A dictionary mapping a discord id to its corresponding lobby id.
    '''
    #lobby_id_to_lobby[i] = lobby number i
    lobby_id_to_lobby:dict[int,TicTacToeLobby] = {}
    #user_to_lobby_id[k] = lobby id of discord user with id `k`
    user_to_lobby_id:dict[int,int] = {}

    @staticmethod
    def is_in_some_lobby(user_id:int) -> bool:
        '''Checks if `user_id` is in a lobby'''
        return user_id in TicTacToeLobbies.user_to_lobby_id

    @staticmethod
    def lobby_create(user_id:int, username:str) -> int|None:
        '''
        Create a lobby for `user_id`.

        The creator for the lobby goes first (X) by default.

        Parameters
        ----------
        user_id : int
            The discord id of the user who is creating a new lobby.
        username : str
            The server nickname of the user who is creating a new lobby.
        
        Returns
        -------
        The lobby id of the newly generated lobby or 
        `None` if the user is already in a lobby.
        '''
        if TicTacToeLobbies.is_in_some_lobby(user_id):
            return None
        lobby_id = MEX(TicTacToeLobbies.lobby_id_to_lobby)
        lobby = TicTacToeLobby(lobby_id, X_id=user_id, X_name=username)
        TicTacToeLobbies.lobby_id_to_lobby[lobby_id] = lobby
        TicTacToeLobbies.user_to_lobby_id[user_id] = lobby_id
        return lobby_id

    @staticmethod
    def lobby_destroy(user_id:int) -> TTTStatusCode:
        '''
        Destroys the lobby that `user_id` is currently in.

        Does so by removing all relevant entries in both the user_to_lobby_id 
        and lobby_id_to_lobby dictionaries.

        Parameters
        ----------
        user_id : int
            The discord id of the user who is destroying his current lobby.
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`    if the lobby was successfully destroyed
            `NotInLobby` if the user is not in some lobby
        '''
        if not TicTacToeLobbies.is_in_some_lobby(user_id):
            return TTTStatusCode.NotInLobby
        lobby_id = TicTacToeLobbies.user_to_lobby_id[user_id]
        lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]
        X_id = lobby.X_id
        O_id = lobby.O_id
        if X_id != None:
            del TicTacToeLobbies.user_to_lobby_id[X_id]
        if O_id != None:
            del TicTacToeLobbies.user_to_lobby_id[O_id]
        del TicTacToeLobbies.lobby_id_to_lobby[lobby_id]
        return TTTStatusCode.Success

    @staticmethod
    def get_lobby_id(user_id:int) -> int|None:
        '''
        Get the lobby id of `user_id`, or `None` if the user is not in one.

        Returns
        -------
        The lobby id if the user is in some lobby.
        'None' if the user is not in any lobby.
        '''
        if not TicTacToeLobbies.is_in_some_lobby(user_id):
            return None
        return TicTacToeLobbies.user_to_lobby_id[user_id]

    @staticmethod
    def get_next_to_move(lobby_id:int) -> int|None:
        '''
        Get the discord id of the next player to move in the specified lobby.

        Returns
        -------
        The discord id of the next player to move in the specified lobby.
        `None` if the user is not in some started lobby.
        '''
        if lobby_id not in TicTacToeLobbies.lobby_id_to_lobby:
            return None
        lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]
        return lobby.get_next_to_move()

    @staticmethod
    def join(lobby_id:int, user_id:int, username:str) -> TTTStatusCode:
        '''
        Let `user_id` join the lobby `lobby_id`.

        Parameters
        ----------
        lobby_id : int
            The lobby id of the lobby being joined
        user_id : int
            The discord id of the user who is joining the lobby
        username : str
            The server nickname of the user who is creating a new lobby.
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`          if the user joined the lobby successfully
            `NonexistentLobby` if the lobby does not exist
            `InLobby`          if the user is already in a lobby
            `FullLobby`        if the lobby is already full
        '''
        if lobby_id not in TicTacToeLobbies.lobby_id_to_lobby:
            return TTTStatusCode.NonexistentLobby
        if TicTacToeLobbies.is_in_some_lobby(user_id):
            return TTTStatusCode.InLobby
        lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]
        if lobby.player_count == 2:
            return TTTStatusCode.FullLobby
        lobby.add_player(user_id, username)
        TicTacToeLobbies.user_to_lobby_id[user_id] = lobby_id
        return TTTStatusCode.Success

    @staticmethod
    def leave(user_id:int) -> TTTStatusCode:
        '''
        Lets a user leave a tic-tac-toe lobby.

        If the lobby was a started game, also resets the game.
        If the lobby is empty after the player leaves, also destroys 
        the lobby.

        Parameters
        ----------
        user_id : int
            The discord id of the person leaving the lobby
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`    if the user left the lobby successfully
            `NotInLobby` if they are not in a lobby
        '''
        if not TicTacToeLobbies.is_in_some_lobby(user_id):
            return TTTStatusCode.NotInLobby
        lobby_id = TicTacToeLobbies.user_to_lobby_id[user_id]
        lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]

        if lobby.is_started:
            lobby.reset()
        lobby.remove_player(user_id)
        del TicTacToeLobbies.user_to_lobby_id[user_id]
        if lobby.player_count == 0:
            del TicTacToeLobbies.lobby_id_to_lobby[lobby_id]

    @staticmethod
    def swap(user_id:int) -> TTTStatusCode:
        '''
        Swaps Player O and Player X in the lobby of `user_id`

        Parameters
        ----------
        user_id : int
            The user id of the person swapping O and X
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`      if swapped successfully
            `NotInLobby`   if the user is not in a lobby
            `StartedLobby` if the user is in a started lobby
        '''
        if not TicTacToeLobbies.is_in_some_lobby(user_id):
            return TTTStatusCode.NotInLobby
        lobby_id = TicTacToeLobbies.user_to_lobby_id[user_id]
        lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]
        if lobby.is_started:
            return TTTStatusCode.StartedLobby
        lobby.swap_players()
        return TTTStatusCode.Success

    @staticmethod
    def start(user_id:int) -> TTTStatusCode:
        '''
        Starts the tic-tac-toe game that `user_id` is in

        Parameters
        ----------
        user_id : int
            The discord id of the user trying to start a game
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`      if the game was started successfully
            `NotInLobby`   if the user is not in a lobby
            `NotFullLobby  if the user is in a non-full lobby
            `StartedLobby` if the user is already in a started lobby
        '''
        if not TicTacToeLobbies.is_in_some_lobby(user_id):
            return TTTStatusCode.NotInLobby
        lobby_id = TicTacToeLobbies.user_to_lobby_id[user_id]
        lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]
        if lobby.player_count != 2:
            return TTTStatusCode.NotFullLobby
        if lobby.is_started:
            return TTTStatusCode.StartedLobby
        lobby.start()
        return TTTStatusCode.Success

    @staticmethod
    def place(user_id:int, r:int, c:int) -> TTTStatusCode:
        '''
        Lets the user place their mark on (r,c)

        Parameters
        ----------
        user_id : int
            The discord id of the user making the move
        r : int
            The row number
        c : int
            The col number
        
        Returns
        -------
        One of the following `TTTStatusCode`s
            `Success`         if the move was done successfully
            `NotInLobby`      if the user is not in the lobby
            `UnstartedLobby`  if the game hasn't started
            `NotYourTurn`     if it is not the player's turn
            `CellOutOfRange`  if the provided coordinates are out of range
            `CellUnavailable` if the spot is already filled
        '''
        if not TicTacToeLobbies.is_in_some_lobby(user_id):
            return TTTStatusCode.NotInLobby
        lobby_id = TicTacToeLobbies.user_to_lobby_id[user_id]
        lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]

        #Try to do the move and return the status code
        return lobby.place(user_id, r, c)

class TTTRespMsg:
    '''
    A class to generate response messages related to `%tictactoe`.

    This is functionally a namespace to neatly group everything relating to 
    making the messages for the bot to send together.

    This class only handles message generation when none of the arguments are 
    invalid. For example, `%tictactoe join b` wouldn't be handled here, since 
    `b` isn't even an integer in the first place.
    '''
    @staticmethod
    def create(lobby_id:str|None, user_id:int) -> str:
        '''Generates the message to send for TicTacToeLobbies.create()'''
        if lobby_id != None:
            return (f"Created a lobby with id {lobby_id} for {ping(user_id)}\n"
                    f"Use `%tictactoe join {lobby_id}` to join")
        else:
            return f"{ping(user_id)}, you're already in a lobby"

    @staticmethod
    def join(status_code:TTTStatusCode, lobby_id:int, user_id:int) -> str|None:
        '''
        Generates the message to send for TicTacToeLobbies.join().

        Returns
        -------
        The message for the status code from TicTacToeLobbies.join().
        None if a status code that TicTacToeLobbies.join() cannot 
        return is given.
        '''
        if status_code == TTTStatusCode.Success:
            return f"{ping(user_id)} successfully joined lobby {lobby_id}"
        elif status_code == TTTStatusCode.NonexistentLobby:
            return f"{ping(user_id)} no lobbies with the id {lobby_id} exist"
        elif status_code == TTTStatusCode.InLobby:
            return (f"{ping(user_id)} you're already in a lobby\n"
                    "Please leave first if you want to join another lobby")
        elif status_code == TTTStatusCode.FullLobby:
            return f"{ping(user_id)} sorry lobby {lobby_id} is already full"
        else:
            return None
        
    @staticmethod
    def leave(status_code:TTTStatusCode, lobby_id:int|None, 
              user_id:int) -> str|None:
        '''
        Generates the message to send for TicTacToeLobbies.leave().

        Returns
        -------
        The message for the status code from TicTacToeLobbies.leave().
        None if a status code that TicTacToeLobbies.leave() cannot 
        return is given.
        '''
        if status_code == TTTStatusCode.Success:
            return f"{ping(user_id)} has left lobby {lobby_id}"
        elif status_code == TTTStatusCode.NotInLobby:
            return f"{ping(user_id)} you're not in any lobby"
        else:
            return None
        
    @staticmethod
    def swap(status_code:TTTStatusCode, lobby_id:int|None, 
             user_id:int) -> str|None:
        '''
        Generates the message to send for TicTacToeLobbies.swap().

        Returns
        -------
        The message for the status code from TicTacToeLobbies.swap().
        None if a status code that TicTacToeLobbies.swap() cannot 
        return is given.
        '''
        if status_code == TTTStatusCode.Success:
            return (f"{ping(user_id)} successfully swapped "
                    f"the players in lobby {lobby_id}")
        elif status_code == TTTStatusCode.NotInLobby:
            return f"{ping(user_id)} you're not in any lobby"
        elif status_code == TTTStatusCode.StartedLobby:
            return f"{ping(user_id)} you can't swap once the game has started"
        else: 
            return None
    
    @staticmethod
    def start(status_code:TTTStatusCode, lobby_id:int|None, 
              user_id:int) -> str|None:
        '''
        Generates the message to send for TicTacToeLobbies.start().

        Returns
        -------
        The message for the status code from TicTacToeLobbies.start().
        None if a status code that TicTacToeLobbies.start() cannot 
        return is given.
        '''
        if status_code == TTTStatusCode.Success:
            to_move_id = TicTacToeLobbies.get_next_to_move(lobby_id)
            return (f"{ping(user_id)} started lobby {lobby_id}\n"
                    f"{ping(to_move_id)} goes first")
        elif status_code == TTTStatusCode.NotInLobby:
            return f"{ping(user_id)} you're not in any lobby"
        elif status_code == TTTStatusCode.NotFullLobby:
            return f"{ping(user_id)} your lobby isn't full yet"
        elif status_code == TTTStatusCode.StartedLobby:
            return f"{ping(user_id)} your lobby has already started"
        else:
            return None
    
    @staticmethod
    def place(status_code:TTTStatusCode, lobby_id:int|None, user_id:int, 
              row:int, col:int) -> str|None:
        '''
        Generates the message to send for TicTacToeLobbies.place().

        Returns
        -------
        The message for the status code from TicTacToeLobbies.place().
        None if a status code that TicTacToeLobbies.place() cannot 
        return is given.
        '''
        if status_code == TTTStatusCode.Success:
            to_move_id = TicTacToeLobbies.get_next_to_move(lobby_id)
            lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]
            return (f"{ping(user_id)} marked ({row},{col})\n"
                    f"{ping(to_move_id)}'s turn to move\n"
                    f"{lobby}")
        elif status_code == TTTStatusCode.NotInLobby:
            return f"{ping(user_id)} you're not in any lobby"
        elif status_code == TTTStatusCode.UnstartedLobby:
            return f"{ping(user_id)} your lobby hasn't started yet"
        elif status_code == TTTStatusCode.NotYourTurn:
            return f"{ping(user_id)} it's not your turn"
        elif status_code == TTTStatusCode.CellOutOfRange:
            return f"{ping(user_id)} that is not inside the board"
        elif status_code == TTTStatusCode.CellUnavailable:
            return f"{ping(user_id)} ({row},{col}) is already marked"
        else:
            return None
    
    @staticmethod
    def view(user_id:int) -> str:
        '''Generates the message to send for TicTacToeLobbies.view()'''
        if not TicTacToeLobbies.is_in_some_lobby(user_id):
            return f"{ping(user_id)} you're not in any lobby"
        lobby_id = TicTacToeLobbies.get_lobby_id(user_id)
        lobby = TicTacToeLobbies.lobby_id_to_lobby[lobby_id]
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
               f"Invoked by: {username} ({user_id})")
        return msg
    
    async def stop() -> None:
        '''Stops the function when an invalid state happens.'''
        msg = debug_msg()
        await ctx.send(msg)
        raise Exception(msg)

    cmd = cmd.lower()
    user_id:int = ctx.author.id
    username:str = ctx.author.display_name

    #Usage: `%tictactoe create`
    if cmd == 'create':
        lobby_id = TicTacToeLobbies.lobby_create(user_id)
        msg = TTTRespMsg.create(lobby_id, user_id)
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
                            "please use the digits from 0 to 9 only"))
            return
        
        lobby_id = int(lobby_id)
        status_code = TicTacToeLobbies.join(lobby_id, user_id, username)

        msg = TTTRespMsg.join(status_code, lobby_id, user_id)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe leave`
    elif cmd == 'leave':
        status_code = TicTacToeLobbies.leave(user_id)
        lobby_id = TicTacToeLobbies.get_lobby_id(user_id)
        msg = TTTRespMsg.leave(status_code, lobby_id, user_id)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe swap`
    elif cmd == 'swap':
        status_code = TicTacToeLobbies.swap(user_id)
        lobby_id = TicTacToeLobbies.get_lobby_id(user_id)
        msg = TTTRespMsg.swap(status_code, lobby_id, user_id)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe start`
    elif cmd == 'start':
        status_code = TicTacToeLobbies.start(user_id)
        lobby_id = TicTacToeLobbies.get_lobby_id(user_id)
        msg = TTTRespMsg.start(status_code, lobby_id, user_id)
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
        status_code = TicTacToeLobbies.place(user_id, row, col)
        lobby_id = TicTacToeLobbies.get_lobby_id(user_id)
        msg = TTTRespMsg.place(status_code, lobby_id, user_id, row, col)
        if msg == None:
            stop()
        await ctx.send(msg)
        return

    #Usage: `%tictactoe view`
    elif cmd == 'view':
        msg = TTTRespMsg.view(user_id)
        await ctx.send(msg)
    
    #Invalid tic-tac-toe subcommand given
    else:
        msg = (f"{cmd} is not a valid tictactoe subcommand\n"
               f"Please use %help for more info")
        await ctx.send(msg)


