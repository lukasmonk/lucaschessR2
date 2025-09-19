from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class SmotheredMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "smotheredMate"
        self.is_mate = True

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

        # Posición final
        position_before: Position.Position = move.position_before
        position: Position.Position = position_before.copia()
        li_pv = rm.pv.split(" ")
        for pos, pv in enumerate(li_pv):
            position.play_pv(pv)

        last_pv = li_pv[-1]
        cr_knight = last_pv[2:4]
        pz_attack = position.get_pz(cr_knight)

        # Condición 1: La pieza que da mate debe ser un caballo.
        if pz_attack != valid_knight:
            return False

        # Condición 2: se busca al rey enemigo y se comprueba que todas las casillas adyacentes corresponden a una pieza
        # de su bando, no pueden estar vacias.
        pos_cr_king = position.get_pos_king(not is_white)
        li_sq = self.squares_round(pos_cr_king)
        valid = "pnbrq" if is_white else "PNBRQ"
        for sq in li_sq:
            pz = position.get_pz(sq)
            if pz and pz not in valid:
                return False

        return True
