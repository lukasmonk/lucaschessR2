from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class BackRankMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "backRankMate"
        self.is_mate = True

    def is_theme(self, move: Move.Move) -> bool:
        mrm: EngineResponse.MultiEngineResponse
        rm: EngineResponse.EngineResponse
        pos_rm: int
        mrm, pos_rm = move.analysis
        rm = mrm.li_rm[pos_rm]

        # Ends with mate
        if rm.mate <= 0:
            return False

        is_white = move.is_white()

        # Posición final
        position_before: Position.Position = move.position_before
        position: Position.Position = position_before.copia()
        li_pv = rm.pv.split(" ")
        for pos, pv in enumerate(li_pv):
            position.play_pv(pv)

        # Posición rey
        cr_king = position.get_pos_king(not is_white)
        row_king = "8" if is_white else "1"
        if cr_king[1] != row_king:
            return False

        # El mate es con dama o torre
        cr_mate = li_pv[-1][2:4]
        pz_mate = position.get_pz(cr_mate)
        if pz_mate.lower() not in "qr":
            return False

        # No hay piezas entre la pz_mate y el rey (que no haya una descubierta)
        c_king, r_king = self.cr_col_row(cr_king)
        c_mate, r_mate = self.cr_col_row(cr_mate)
        if abs(c_king-c_mate) > 1:
            df = +1 if c_mate > c_king else -1
            for col in range(c_king+df, c_mate, df):
                cr = self.col_row_cr(col, r_king)
                if position.get_pz(cr):
                    return False

        # que esté bloqueado por sus propias piezas
        row_pzs = 6 if is_white else 1
        for df in (-1, 0, +1):
            c_pz = c_king +df
            if 0 <= c_pz <= 7:
                cr = self.col_row_cr(c_pz, row_pzs)
                pz = position.get_pz(cr)
                if pz:
                    if is_white:
                        if pz.isupper():
                            return False
                    else:
                        if pz.islower():
                            return False
                else:
                    return False

        return True



        position_before: Position.Position = move.position_before
        # pz = position_before.get_pz(rm.from_sq)
        # if pz.lower() not in ("q", "r"):
        #     return False

        # More than one move
        li_pv = rm.pv.split(" ")
        # if len(li_pv) == 1:
        #     return False

        # The opposing king is on the last row and does not move from it in any move.
        position = position_before.copia()
        row_bq = "8" if is_white else "1"

        for pv in li_pv:
            pos_king = position.get_pos_king(not is_white)
            row = pos_king[1]
            if row != row_bq:
                return False
            position.play_pv(pv)

        return True
