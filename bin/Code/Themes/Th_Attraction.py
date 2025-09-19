from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class Attraction(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "attraction"

    def is_theme(self, move: Move.Move) -> bool:
        mrm: EngineResponse.MultiEngineResponse
        rm: EngineResponse.EngineResponse
        pos_rm: int
        mrm, pos_rm = move.analysis
        rm = mrm.li_rm[pos_rm]

        # It is a top move in analysis
        if not self.is_unique_best_move(mrm, rm, pos_rm):
            return False

        if move.has_theme("deflection") or move.has_theme("decoy"):
            return False

        # Have the pv of the movement developed in order to analyse
        pv = rm.pv
        li_pv = pv.split(" ")
        if len(li_pv) < 2:
            return False

        # The situation is not lost
        if self.is_lost(rm):
            return False

        # It is a sacrifice
        position_before: Position.Position = move.position_before

        # if capture
        pz_captured = position_before.get_pz(rm.to_sq)
        pz_moved = position_before.get_pz(rm.from_sq)

        if pz_captured:
            # Que la pieza capturadora tenga un valor menor
            if self.pz_value(pz_moved) <= self.pz_value(pz_captured):
                return False

        # que haya recaptura
        a1h8_rival = li_pv[1]
        if rm.to_sq != a1h8_rival[2:4]:
            return False

        # Que haya mate o mejora de material al final
        if self.dif_material(move.position_before, rm.pv) <= 0 and rm.mate == 0:
            return False

        return True
