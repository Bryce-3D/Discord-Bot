from __future__ import annotations
import discord
from Kumiko.bot_config import bot, commands
from enum import Enum
from Kumiko.util import MEX,ping

class TicTacToe:
    '''
    A class to represent the state of a tic-tac-toe game.

    Attributes
    ----------
    board : list[list[int]]
        The 3x3 tic-tac-toe board. 0s represent empty cells
    P1 : str
        The symbol for player 1.
    P2 : str
        The symbol for player 2.
    filled : int
        The number of cells in the board filled so far.

    Functions
    ---------

    '''
    def __init__(self, P1:str='X', P2:str='O'):
        self.board:list[list[int]] = [
            [0 for c in range(3)] for r in range(3)
        ]
        self.P1 = P1
        self.P2 = P2
        self.filled = 0

    def _is_winner(self, player:int) -> bool:
        assert player == 1 or player == 2
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
    
    def is_game_over(self) -> bool:
        if self._is_winner(1) or self._is_winner(2):
            return True
        return self.filled == 9
    
    def place(self, r:int, c:int):
        #TODO
        return

    @property
    def turn(self) -> int:
        return 1 if self.filled%2 == 0 else 2
    


