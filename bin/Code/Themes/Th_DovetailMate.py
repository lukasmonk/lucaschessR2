from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class DovetailMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "dovetailMate"
        self.is_mate = True
        self.dic_alas_kq = {
            (-1, -1): ((-1, 0), (0, -1)),
            (+1, -1): ((0, -1), (+1, 0)),
            (+1, +1): ((0, +1), (+1, 0)),
            (-1, +1): ((0, +1), (-1, 0)),
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

        # Solo intervienen la torre, el caballo y la reina
        valid_queen = "Q" if is_white else "q"

        position_before: Position.Position = move.position_before
        position: Position.Position = position_before.copia()
        li_pv = rm.pv.split(" ")
        for pos, pv in enumerate(li_pv):
            position.play_pv(pv)

        last_pv = li_pv[-1]
        cr_queen = last_pv[2:4]
        pz_attack = position.get_pz(cr_queen)

        # Condición 1: La pieza que da mate debe ser una Dama.
        if pz_attack != valid_queen:
            return False

        # Condición 2: El rey debe estar en diagonal con la dama, y pegando.
        cr_king_rival = position.get_pos_king(not is_white)
        dc = ord(cr_king_rival[0]) - ord(cr_queen[0])
        dr = ord(cr_king_rival[1]) - ord(cr_queen[1])
        if abs(dc) != 1 or abs(dr) != 1:
            return False

        # Condicion 3: dos piezas rivales al lado del rey rival hacen de embudo.
        def correct_piece(x_offset: int, y_offset: int) -> bool:
            col = chr(ord(cr_king_rival[0]) + x_offset)
            row = chr(ord(cr_king_rival[1]) + y_offset)

            # Validar si está dentro del tablero
            if not ("a" <= col <= "h") or not ("1" <= row <= "8"):
                return False

            piece = position.get_pz(col + row)
            if not piece:
                return False  # Casilla vacía

            # Verifica si la pieza es enemiga
            if is_white:
                return piece.islower()
            else:
                return piece.isupper()

        (dc1, dr1), (dc2, dr2) = self.dic_alas_kq[(dc, dr)]
        if not correct_piece(dc1, dr1) or not correct_piece(dc2, dr2):
            return False

        return True
