from ..bot_config import bot, commands
from enum import Enum

class TicTacToe:
    '''
    A class to represent the state of a tic-tac-toe game.

    Contains the tic-tac-toe board as well as a lot of helper functions to 
    make it easier to use. X always goes before O in this implementation.

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
        '''
        if player not in {'X','O'}:
            s = f'TicTacToe.win_check({player}) is an invalid function call'
            raise Exception(s)
        
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
    
    def is_done(self) -> bool:
        '''
        Checks if a game is completed.

        Returns
        -------
        True if one of the players has won, False otherwise.
        '''
        return self.win_check('X') or self.win_check('O')
    
    def get_turn(self) -> str:
        '''
        Returns whose turn it currently is

        Returns
        -------
        'X' is it is player X's turn, 'O' otherwise
        '''
        return 'X' if self.filled%2 == 0 else 'O'

    def place(self, r:int, c:int) -> int:
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
        0 if the cell was filled successfully
        1 if the cell is not available
        '''
        if self.board[r][c] != ' ':
            return 1
        #Use the parity of self.filled to determine the player
        self.board[r][c] = self.get_turn()
        self.filled += 1
        return 0
    
    def restart(self) -> None:
        '''Restarts the game state'''
        for r in range(3):
            for c in range(3):
                self.board[r][c] = ' '
        self.filled = 0

    def __str__(self):
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

    Attributes
    ----------
    tictactoe : Tictactoe
        The tic-tac-toe board.
    lobby_id : int
        The id of this lobby.
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
    
    def is_empty(self) -> bool:
        '''Checks whether there are no players'''
        return self.X_id == None and self.O_id == None

    def is_full(self) -> bool:
        '''Checks whether there are two players'''
        return self.X_id != None and self.O_id != None

    def add_player(self, id:int, name:str) -> int:
        '''
        Adds a player to the game

        Parameters
        ----------
        id : int
            The discord id of the user being added
        name : str
            The discord name of the user being added

        Returns
        -------
        0 if the player was added successfully
        1 if the game is already full
        '''
        if self.is_full():
            return 1
        if self.X_id == None:
            self.X_id = id
            self.X_name = name
        else:
            self.O_id = id
            self.O_name = name
        return 0
    
    def remove_player(self, id:int) -> int:
        '''
        Removes a player from a game

        Parameters
        ----------
        id : int
            The discord id of the user being removed

        Returns
        -------
        0 if the player was removed successfully
        1 if the player doesn't exist
        '''
        if self.O_id == id:
            self.O_id = None
            self.O_name = None
            return 0
        if self.X_id == id:
            self.X_id = None
            self.X_name = None
            return 0
        return 1

    def swap_players(self) -> None:
        '''Swap Player X and Player O'''
        if self.is_started:
            raise Exception('Tried to swap players in started game')
        self.X_id,self.O_id = self.O_id,self.X_id
        self.X_name,self.O_name = self.O_name,self.X_name
    
    def is_in(self, id:int) -> bool:
        '''
        Checks if a given user is in the lobby.

        Parameters
        ----------
        id : int
            The discord id of the user being checked.
        
        Returns
        -------
        True if the user is in the lobby, False otherwise/
        '''
        return self.X_id == id or self.O_id == id

    def start(self) -> None:
        '''
        Starts the game
        
        Returns
        -------
        0 if the game was started successfully
        1 if the lobby was not full
        '''
        if not self.is_full():
            return 1
        self.is_started = True
        return 0
    
    def reset(self) -> None:
        '''Resets the state of the game while keeping the players in'''
        self.tictactoe.restart()
        self.is_started = False
    
    def place(self, id:int, r:int, c:int) -> int:
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
        0 if the move was done successfully
        1 if the game hasn't started
        2 if it is not the player's turn
        3 if the spot is already filled
        '''
        #User is not in the lobby (should not happen)
        if not self.is_in(id):
            e = 'TicTacToeLobby.place() called with an id not in the lobby'
            raise Exception(e)
        
        if not self.is_started:
            return 1

        #O moved during X's turn
        if self.tictactoe.get_turn() == 'X' and self.O_id == id:
            return 2
        #X moved during O's turn
        if self.tictactoe.get_turn() == 'O' and self.X_id == id:
            return 2
        
        #Try to do the move
        status = self.tictactoe.place(r,c)
        if status == 1:   #Spot already filled
            return 3
        else:
            return 0
    
    def __str__(self) -> str:
        '''Returns a string representation of the game state'''
        s = f'Tic-tac-toe lobby {self.lobby_id}'
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

        s += f'```\n{self.tictactoe}```\n'
        return s

class TicTacToeBot:
    #lobbies[i] = lobby number i
    lobbies:dict[int,TicTacToeLobby] = {}
    #user_to_lobby[k] = lobby number of discord user with id `k`
    user_to_lobby:dict[int,int] = {}

    @staticmethod
    def MEX(d:dict|set) -> int:
        '''Returns the MEX of a dict or set'''
        ans = 0
        while ans in d:
            ans += 1
        return ans

    @staticmethod
    def is_in_lobby(user_id:int) -> bool:
        '''Checks if `user_id` is in a lobby'''
        return user_id in TicTacToeBot.user_to_lobby

    @staticmethod
    def lobby_create(user_id:int) -> int:
        '''
        Create a lobby for `user_id` such that they are player `turn`.

        Parameters
        ----------
        user_id : int
            The discord id of the user who is creating a new lobby.
        
        Returns
        -------
        The lobby id if the lobby was successfully generated
        -1 if the user is already in a lobby
        '''
        if TicTacToeBot.is_in_lobby(user_id):
            return -1
        lobby_id = TicTacToeBot.MEX(TicTacToeBot.lobbies)
        lobby = TicTacToeLobby(lobby_id, X_id=user_id)
        TicTacToeBot.lobbies[lobby_id] = lobby
        TicTacToeBot.user_to_lobby[user_id] = lobby_id
        return lobby_id

    @staticmethod
    def join(lobby_id:int, user_id:int) -> int:
        '''
        Let `user_id` join the lobby `lobby_id`

        Parameters
        ----------
        lobby_id : int
            The lobby id of the lobby being joined
        user_id : int
            The discord id of the user who is joining the lobby
        
        Returns
        -------
        0 if the user joined the lobby successfully
        1 if the lobby does not exist
        2 if the user is already in a lobby
        3 if the lobby is already full
        '''
        if lobby_id not in TicTacToeBot.lobbies:
            return 1
        if TicTacToeBot.is_in_lobby(user_id):
            return 2
        lobby = TicTacToeBot.lobbies[lobby_id]
        if lobby.is_full():
            return 3
        lobby.add_player(user_id)
        return 0

    @staticmethod
    def start(user_id:int) -> int:
        '''
        Starts the tic-tac-toe game that `user_id` is in

        Parameters
        ----------
        user_id : int
            The discord id of the user trying to start a game
        
        Returns
        -------
        0 if the game was started successfully
        1 if the user is not in a lobby
        2 if the user is in a non-full lobby
        3 if the user is already in a started lobby
        '''
        if not TicTacToeBot.is_in_lobby(user_id):
            return 1
        lobby_id = TicTacToeBot.user_to_lobby[user_id]
        lobby = TicTacToeBot.lobbies[lobby_id]
        if not lobby.is_full():
            return 2
        if lobby.is_started:
            return 3
        lobby.start()
        return 0

    @staticmethod
    def leave(user_id:int) -> int:
        '''
        Lets a user leave a tic-tac-toe lobby

        Parameters
        ----------
        user_id : int
            The discord id of the person leaving the lobby
        
        Returns
        -------
        0 if they are not in a lobby
        1 if they left a started lobby
        2 if they left an unstarted lobby of 1 person
        3 if they left an unstarted lobby of 2 people
        '''
        if not TicTacToeBot.is_in_lobby(user_id):
            return 0
        lobby_id = TicTacToeBot.user_to_lobby[user_id]
        lobby = TicTacToeBot.lobbies[lobby_id]

        if lobby.is_started:
            lobby.reset()
            lobby.remove_player(user_id)
            return 1
        lobby.remove_player(user_id)
        if lobby.is_empty():
            return 2
        else:
            return 3

    @staticmethod
    def swap(user_id:int) -> int:
        '''
        Swaps Player O and Player X in the lobby of `user_id`

        Parameters
        ----------
        user_id : int
            The user id of the person swapping O and X
        
        Returns
        -------
        0 if done successfully
        1 if the user is not in a lobby
        2 if the user is in a started lobby
        '''
        if not TicTacToeBot.is_in_lobby(user_id):
            return 1    
        lobby_id = TicTacToeBot.user_to_lobby[user_id]
        lobby = TicTacToeBot.lobbies[lobby_id]
        if lobby.is_started:
            return 2
        lobby.swap_players()
        return 0

    def place(user_id:int, r:int, c:int) -> int:
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
        0 if the move was done successfully
        TODO  
        '''
        return 0


@bot.command()
async def tictactoe(ctx:commands.Context, cmd:str, *args) -> None:
    '''Main command to handle the logic of %tictactoe'''
    if cmd == 'create':
        pass   #TODO
    if cmd == 'join':
        pass   #TODO
    if cmd == 'start':
        pass   #TODO
    if cmd == 'leave':
        pass   #TODO
