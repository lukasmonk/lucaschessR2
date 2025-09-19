import FasterCode

from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class HookMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "hookMate"
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

        # Solo intervienen la torre, un caballo y un peón
        valid_rook = "R" if is_white else "r"
        valid_knight = "N" if is_white else "n"
        valid_pawn = "P" if is_white else "p"

        position_before: Position.Position = move.position_before
        position: Position.Position = position_before.copia()
        li_pv = rm.pv.split(" ")
        for pos, pv in enumerate(li_pv):
            position.play_pv(pv)

        last_pv = li_pv[-1]
        cr_rook = last_pv[2:4]
        pz_attack = position.get_pz(cr_rook)

        # Condición 1: la pieza que da mate debe ser una torre.
        if pz_attack != valid_rook:
            return False

        # Condición 2: la torre está protegida por un caballo.
        li = FasterCode.li_n(FasterCode.a1_pos(cr_rook))
        li_cr_knight = []
        for pos in li:
            cr = FasterCode.pos_a1(pos)
            if position.get_pz(cr) == valid_knight:
                li_cr_knight.append(cr)
        if not li_cr_knight:
            return False

        # Condicion 3: el caballo está protegido por un peón.
        dif_row = -1 if is_white else +1
        for cr_knight in li_cr_knight:
            col, row = self.cr_col_row(cr_knight)
            if col - 1 >= 0:
                cr_pawn = self.col_row_cr(col - 1, row + dif_row)
                if position.get_pz(cr_pawn) == valid_pawn:
                    return True
            if col + 1 < 8:
                cr_pawn = self.col_row_cr(col + 1, row + dif_row)
                if position.get_pz(cr_pawn) == valid_pawn:
                    return True

        return False
