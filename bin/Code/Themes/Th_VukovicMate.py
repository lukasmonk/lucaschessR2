from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class VukovicMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "vukovicMate"
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
        ncol_king_rival = ord(cr_king_rival[0])
        nrow_king_rival = ord(cr_king_rival[1])

        # Cuatro puntos cardinales
        valid_rook = "R" if is_white else "r"
        valid_knight = "N" if is_white else "n"
        for dc, dr in ((-1, 0), (0, -1), (+1, 0), (0, +1)):
            xcol = chr(ncol_king_rival + dc)
            xrow = chr(nrow_king_rival + dr)
            if "a" <= xcol <= "h" and "1" <= xrow <= "8":
                xcr = xcol + xrow
                if position.get_pz(xcr) == valid_rook:
                    xcol_knight = chr(ncol_king_rival + 2 * dc)
                    xrow_knight = chr(nrow_king_rival + 2 * dr)
                    if "a" <= xcol_knight <= "h" and "1" <= xrow_knight <= "8":
                        xcr_knight = xcol_knight + xrow_knight
                        if position.get_pz(xcr_knight) == valid_knight:
                            return True

        return False
