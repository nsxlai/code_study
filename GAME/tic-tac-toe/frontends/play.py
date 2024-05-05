# frontends/play.py

from tic_tac_toe.game.engine import TicTacToe
from tic_tac_toe.game.players import RandomComputerPlayer
from tic_tac_toe.logic.models import Mark

from console.renderers import ConsoleRenderer


if __name__ == '__main__':

    player1 = RandomComputerPlayer(Mark('X'))
    player2 = RandomComputerPlayer(Mark('O'))

    TicTacToe(player1, player2, ConsoleRenderer()).play()
