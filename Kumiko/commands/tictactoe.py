from ..bot_config import bot, commands

class TicTacToe:
    '''
    A class to represent the state of a tic tac toe game
    
    Attributes
    ----------
    num_to_chr : dict[int:chr] (class attribute)
        Dict used to convert the internal int representation of a cell 
        of the board to its chr representation.
    X_id : int|None
        The discord id of player X. Set to None if they don't exist.
    O_id : int|None
        The discord id of player O. Set to None if they don't exist.
    board : list[list[int]]
        The 3x3 tic-tac-toe board.
    filled : int|None
        The number of cells in the board filled so far.
        Set to None if the game hasn't started yet.
    '''
    #Convert int rep to str rep on the board
    num_to_chr = {-1:' ', 0:'X', 1:'O'}

    def __init__(self, x:int|None=None, o:int|None=None):
        '''
        Initialize a game with discord ids for the players.

        Parameters
        ----------
        x : int|None = None
            The discord id of player X. Set to None if they don't exist
        o : int|None = None
            The discord id of player Y. Set to None if they don't exist
        '''
        self.X_id:int|None = x
        self.O_id:int|None = o
        self.board:list[list[int]] = [[-1 for c in range(3)] for r in range(3)]
        self.filled:int|None = None
    
    def add_player(self, id:int) -> int:
        '''
        Adds a player to the game

        Parameters
        ----------
        id : int
            The discord id of the user being added

        Returns
        -------
        0 if the player was added successfully
        1 if the game is already full
        '''
        if self.is_empty():
            raise Exception("`TicTacToe.add_player()` on an empty TicTacToe")
        if self.is_full():
            return 1
        if self.X_id == None:
            self.X_id = id
        else:
            self.O_id = id
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
        if self.X_id != id and self.O_id != id:
            return 1
        if self.X_id == id:
            self.X_id = None
        if self.O_id == id:
            self.O_id = None
        return 0

    def swap_players(self) -> None:
        '''Swap Player X and Player O'''
        self.X_id,self.O_id = self.O_id,self.X_id
    
    def is_empty(self) -> bool:
        '''Checks whether there are no players'''
        return self.X_id == None and self.O_id == None
    
    def is_full(self) -> bool:
        '''Checks whether there are two players'''
        return self.X_id != None and self.O_id != None
    
    def is_started(self) -> bool:
        '''Checks whether the game has started'''
        return self.filled != None
        
    def win_check(self, player:int) -> bool:
        '''
        Checks if the specified player has won the game.

        Parameters
        ----------
        player : int
            The specified player. 0 for X and 1 for O

        Returns
        -------
        True if player has a line on the board, False otherwise
        '''
        if player not in {0,1}:
            raise Exception("TicTacToe.win_check() has an invalid player passed")
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
    
    def is_done(self) -> int|None:
        '''
        Checks if a game is done and returns the status

        Returns
        -------
        -1   - if it is a tie
         0   - if X won
         1   - if O won
        None - if it hasn't ended yet
        '''
        if self.win_check(0):
            return 0
        if self.win_check(1):
            return 1
        if self.filled == 9:
            return -1
        return None
    
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
        if self.board[r][c] != -1:
            return 1
        #Use the parity of self.filled to determine the player
        self.board[r][c] = self.filled%2
        self.filled += 1
        return 0
    
    def start(self) -> None:
        '''Starts the game'''
        self.filled = 0

    def restart(self) -> None:
        '''Resets the state of the game while keeping the players in'''
        self.board = [[0 for c in range(3)] for r in range(3)]
        self.filled = None

    def stringify_board(self) -> str:
        '''Returns a string representation of the board state'''
        if not self.is_started():
            raise Exception('Game hasn\'t started yet')
        b = [[self.num_to_chr[c] for c in r] for r in self.board]   #Convert to string rep
        s = (f' {b[0][0]} | {b[0][1]} | {b[0][2]} \n'
             '---+---+---\n'
             f' {b[1][0]} | {b[1][1]} | {b[1][2]} \n'
             '---+---+---\n'
             f' {b[2][0]} | {b[2][1]} | {b[2][2]} \n')
        return s
    
    def __str__(self) -> str:
        '''Returns a string representation of the game state'''
        if self.X_id == None:
            s  = 'There is currently no Player X\n'
        else:
            s  = f'Player X has discord id {self.X_id}\n'
        if self.O_id == None:
            s += 'There is currently no Player O\n'
        else:
            s += f'Player O has discord id {self.O_id}\n'
        
        if not self.is_started():
            s += 'The game hasn\'t started yet'
            return s

        s += f'{self.filled} cells have been filled so far\n'
        s += f'```\n{self.stringify_board()}```\n'
        return s



#lobbies[i] = game state of lobby `i``
lobbies:dict[int:TicTacToe] = {}
#user_to_lobby[k] = lobby number of discord user with id `k`
user_to_lobby:dict[int:int] = {}

def MEX(d:dict|set) -> int:
    '''Returns the MEX of a dict or set'''
    ans = 0
    while ans in d:
        ans += 1
    return ans

def is_in_lobby(user_id:int) -> bool:
    '''Checks if `user_id` is in a lobby'''
    return user_id in user_to_lobby

def tictactoe_create(user_id:int, turn:int) -> int:
    '''
    Create a lobby for `user_id` such that they are player `turn`.

    Parameters
    ----------
    user_id : int
        The discord id of the user who is creating a new lobby.
    turn : int
        The turn of the user creating the new lobby.
        0 if they are X and 1 if they are O.
    
    Returns
    -------
    0 if the lobby was successfully generated
    1 if the user is already in a lobby
    '''
    if is_in_lobby(user_id):
        return 1
    
    lobby_id = MEX(lobbies)
    if turn == 0:
        game_state = TicTacToe(x=user_id)
    else:
        game_state = TicTacToe(o=user_id)
    
    lobbies[lobby_id] = game_state
    user_to_lobby[user_id] = lobby_id

    return 0

def tictactoe_join(user_id:int, lobby_id:int) -> int:
    '''
    Let `user_id` join the lobby `lobby_id`

    Parameters
    ----------
    user_id : int
        The discord id of the user who is joining the lobby
    lobby_id : int
        The lobby id of the lobby being joined
    
    Returns
    -------
    0 if the user joined the lobby successfully
    1 if the user is already in a lobby
    2 if the lobby does not exist
    3 if the lobby is already full
    '''
    if is_in_lobby(user_id):
        return 1
    if lobby_id not in lobbies:
        return 2

    game_state = lobbies[lobby_id]
    if game_state.is_full():
        return 3
    game_state.add_player(user_id)
    return 0

def tictactoe_start(user_id:int) -> int:
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
    if not is_in_lobby(user_id):
        return 1
    lobby_id = user_to_lobby[user_id]
    game_state = lobbies[lobby_id]
    if not game_state.is_full():
        return 2
    if game_state.is_started():
        return 3
    game_state.start()
    return 0

def tictactoe_leave(user_id:int) -> int:
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
    if not is_in_lobby(user_id):
        return 0
    
    lobby_id = user_to_lobby[user_id]
    game_state = lobbies[lobby_id]

    if game_state.is_started():
        game_state.restart()
        game_state.remove_player(user_id)
        return 1
    
    game_state.remove_player(user_id)
    if game_state.is_empty():
        return 2
    else:
        return 3

def tictactoe_swap(user_id:int) -> int:
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
    if not is_in_lobby(user_id):
        return 1
    
    lobby_id = user_to_lobby[user_id]
    game_state = lobbies[lobby_id]

    if game_state.is_started():
        return 2
    
    game_state.swap_players()
    return 0

@bot.command()
async def tictactoe(ctx:commands.Context, cmd:str, *args) -> None:
    if cmd == 'create':
        pass   #TODO
    if cmd == 'join':
        pass   #TODO
    if cmd == 'start':
        pass   #TODO
    if cmd == 'leave':
        pass   #TODO
