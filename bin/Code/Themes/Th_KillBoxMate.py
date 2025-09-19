from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class KillBoxMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "killBoxMate"
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

        # Posición final
        position_before: Position.Position = move.position_before
        position: Position.Position = position_before.copia()
        li_pv = rm.pv.split(" ")
        for pos, pv in enumerate(li_pv):
            position.play_pv(pv)

        # Posición rey
        cr_king_rival = position.get_pos_king(not is_white)

        # El mate es con dama o torre
        cr_mate = li_pv[-1][2:4]
        pz_mate = position.get_pz(cr_mate)
        if pz_mate.lower() not in "qr":
            return False

        # el rey y la pieza mate han de estar en casillas adyacentes
        col_king, row_king = self.cr_col_row(cr_king_rival)
        col_mate, row_mate = self.cr_col_row(cr_mate)
        df_col = col_mate - col_king
        df_row = row_mate - row_king
        # posición adyacente
        if abs(df_col) > 2 or abs(df_row) > 2:
            return False

        pz_other = "Q" if pz_mate.upper() == "R" else "R"
        if not is_white:
            pz_other = pz_other.lower()

        if df_col == 0:
            col_other1 = col_mate + 2
            col_other2 = col_mate - 2
            df = +1 if df_row < 0 else -1
            row_other1 = row_other2 = row_mate + df * 2
        else:
            row_other1 = row_mate + 2
            row_other2 = row_mate - 2
            df = +1 if df_col < 0 else -1
            col_other1 = col_other2 = col_mate + df * 2

        if 0 <= col_other1 <= 7 and 0 <= row_other1 <= 7:
            cr = self.col_row_cr(col_other1, row_other1)
            if position.get_pz(cr) == pz_other:
                return True

        if 0 <= col_other2 <= 7 and 0 <= row_other2 <= 7:
            cr = self.col_row_cr(col_other2, row_other2)
            if position.get_pz(cr) == pz_other:
                return True

        return False
