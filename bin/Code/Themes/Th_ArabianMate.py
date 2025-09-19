from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class ArabianMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "arabianMate"
        self.is_mate = True
        self.dic_rook_knight = {
            "a1": (("a2", "b1"), "c3"),
            "a8": (("a7", "b8"), "c6"),
            "h1": (("h2", "g1"), "f3"),
            "h8": (("h7", "g8"), "f6"),
        }

    def is_theme(self, move: Move.Move) -> bool:
        mrm: EngineResponse.MultiEngineResponse
        rm: EngineResponse.EngineResponse
        pos_rm: int
        mrm, pos_rm = move.analysis
        rm = mrm.li_rm[pos_rm]
        is_white = move.is_white()

        # Ends with mate
        if rm.mate <= 0:
            return False

        valid_knight = "N" if is_white else "n"
        valid_rook = "R" if is_white else "r"

        # Posición final
        position_before: Position.Position = move.position_before
        position: Position.Position = position_before.copia()
        li_pv = rm.pv.split(" ")
        for pos, pv in enumerate(li_pv):
            position.play_pv(pv)

        last_pv = li_pv[-1]
        cr_rook = last_pv[2:4]
        pz_attack = position.get_pz(cr_rook)

        # Condición 1: La pieza que da mate debe ser una torre.
        if pz_attack != valid_rook:
            return False

        # Condición 2: se busca al rey enemigo y se verifica que
        # su posición corresponda a una de las cuatro esquinas del tablero.
        pos_cr_king = position.get_pos_king(not is_white)
        if pos_cr_king not in ("a1", "a8", "h1", "h8"):
            return False

        # Condición 3: Proximidad de la Torre: Se asegura de que la torre esté justo al lado del rey,
        # ya que esta proximidad es esencial para el patrón.
        lipos_rook, pos_knight = self.dic_rook_knight[pos_cr_king]
        if cr_rook not in lipos_rook:
            return False

        # Condición 4: El caballo debe defender a la torre, y debe atacar la casilla de escape
        if position.get_pz(pos_knight) != valid_knight:
            return False

        return True
