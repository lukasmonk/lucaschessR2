import FasterCode

from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class AnastasiaMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "anastasiaMate"
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

        # Solo intervienen la torre, el caballo y la reina
        valid_pzs = "RQN" if is_white else "rqn"

        position_before: Position.Position = move.position_before
        position: Position.Position = position_before.copia()
        li_pv = rm.pv.split(" ")
        for pos, pv in enumerate(li_pv[:-1]):
            if pos % 2 == 0:
                pz_attack = position.get_pz(pv[:2])
                if pz_attack not in valid_pzs:
                    return False
            position.play_pv(pv)

        last_pv = li_pv[-1]
        pz_attack = position.get_pz(last_pv[:2])

        # Condición 1: La pieza que da mate debe ser una Torre o Dama.
        if pz_attack.lower() not in ("r", "q"):
            return False

        # Condición 2: El rey debe estar en una columna lateral ('a' o 'h').
        pos_cr_king = position.get_pos_king(not is_white)
        col_king = pos_cr_king[0]
        if col_king not in ("a", "h"):
            return False

        # Condicion 3: la pieza que da mate debe estar en la misma columna.
        pos_attack = last_pv[2:4]
        col_attack = pos_attack[0]
        if col_attack != col_king:
            return False

        # Condición 4: Un caballo debe controlar la/las casilla/s de escape,
        # en la misma fila que el rey y en la columna adyacente
        col_escape = "b" if col_king == "a" else "g"
        row_king = pos_cr_king[1]
        casillas_escape = [col_escape + row_king]
        nrow_king = int(row_king)
        if nrow_king + 1 < 9:
            casillas_escape.append(col_escape + chr(48 + nrow_king + 1))
        if nrow_king - 1 > 0:
            casillas_escape.append(col_escape + chr(48 + nrow_king - 1))

        bq = "N" if is_white else "n"
        for casilla_escape in casillas_escape:
            pz = position.get_pz(casilla_escape)
            if not pz:
                li_pos = FasterCode.dict_n[FasterCode.a1_pos(casilla_escape)]
                ok = False
                for pos in li_pos:
                    a1 = FasterCode.pos_a1(pos)
                    if position.get_pz(a1) == bq:
                        ok = True
                        break
                if not ok:
                    return False

        return True
