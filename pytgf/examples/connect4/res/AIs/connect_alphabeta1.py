import connect4_alphabeta as c4ab


class ConnectAlphaBeta1(c4ab.Connect4AlphaBeta):

    @property
    def _maxDepth(self):
        return 1