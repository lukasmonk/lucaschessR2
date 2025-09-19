from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class AdvancedPawn(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "advancedPawn"

    def is_theme(self, move: Move.Move) -> bool:
        position_before = move.position_before
        mrm: EngineResponse.MultiEngineResponse
        pos_rm: int
        mrm, pos_rm = move.analysis
        rm: EngineResponse.EngineResponse = mrm.li_rm[pos_rm]

        # It is a top move in analysis
        if not self.is_best_move(mrm, rm, pos_rm):
            return False

        # The situation is not lost
        if self.is_lost(rm):
            return False

        # It is a pawn
        piece = position_before.get_pz(rm.from_sq)
        if piece.lower() != "p":
            return False

        # Advance to rows 5/6 3/4
        row_dest = int(rm.to_sq[1])
        if position_before.is_white:
            if row_dest not in (5, 6):
                return False
        else:
            if row_dest not in (3, 4):
                return False

        # Not captures
        if rm.from_sq[0] != rm.to_sq[0]:
            return False

        # It is supported by other pawn, with other squares not occupied
        if not self.support_pawn(position_before, rm.to_sq):
            return False

        return True

    @staticmethod
    def support_pawn(position_before: Position.Position, to_sq: str):
        row_dest = int(to_sq[1])
        rng = range(2, row_dest) if position_before.is_white else range(7, row_dest, -1)
        pawn = "P" if position_before.is_white else "p"

        col = to_sq[0]

        def support_col(col_seek):
            ok = False
            for row in rng:
                pz = position_before.get_pz(f"{col_seek}{row}")
                if pz:
                    if pz != pawn:
                        return False
                    else:
                        ok = True
            return ok

        if col > "a":
            if support_col(chr(ord(col) - 1)):
                return True
        if col < "h":
            if support_col(chr(ord(col) + 1)):
                return True
        return False
