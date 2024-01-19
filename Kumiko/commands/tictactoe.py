from ..bot_config import bot, commands

num_to_chr = {-1:' ', 0:'X', 1:'O'}

class TicTacToe:
    '''A class to represent the state of a tic tac toe game'''
    def __init__(self, x:int|None, o:int|None):
        '''
        Initialize a game with discord ids for the players.

        Parameters
        ----------
        x : int|None
            The discord id of player X. Set to None if they don't exist
        o : int|None
            The discord id of player Y. Set to None if they don't exist
        '''
        self.X:int|None = x
        self.O:int|None = o
        self.board:list[list[int]] = [[-1 for c in range(3)] for r in range(3)]
        self.filled:int|None = None
    
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
    
    def draw_check(self) -> bool:
        '''Checks if the board is a draw'''
        if self.win_check(0):
            return False
        if self.win_check(1):
            return False
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == -1:
                    return False
        return True
    
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
        #TODO
        return None

#lobbies[i] = game state of lobby i
lobbies = {}


def MEX(a:set[int]) -> int:
    ans = 0
    while ans in a:
        ans += 1
    return ans

def stringify_board(board:list[list[int]]) -> str:
    '''
    Takes in a board represented by a 3x3 list of ints and returns a 
    string representation of the board
    '''
    b = [[num_to_chr[c] for c in r] for r in board]   #Convert to string rep
    s  = f' {b[0][0]} | {b[0][1]} | {b[0][2]} \n'
    s += '---+---+---\n'
    s += f' {b[1][0]} | {b[1][1]} | {b[1][2]} \n'
    s += '---+---+---\n'
    s += f' {b[2][0]} | {b[2][1]} | {b[2][2]} '
    return s

@bot.command()
async def tictactoe(ctx:commands.Context, cmd:str, *args) -> None:
    if cmd == 'create':
        id = MEX(lobbies)
        lobbies.add(id)
