from Code.Base import Move
from Code.Themes import CheckTheme


class DoubleCheck(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "doubleCheck"

    def is_theme(self, move: Move.Move) -> bool:
        if not move.is_check:
            return False

        is_white = move.is_white()

        # Buscamos la posicion del rey enemigo
        cr_king = move.position.get_pos_king(not is_white)

        # Buscamos los atacantes del rey enemigo, si hay mas de uno
        if len(self.square_attacked(move.position, cr_king, is_white)) > 1:
            return True

        return False
