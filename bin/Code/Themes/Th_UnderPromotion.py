from Code.Base import Move
from Code.Themes import CheckTheme
from Code.Engines import EngineResponse


class UnderPromotion(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "underPromotion"

    def is_theme(self, move: Move.Move) -> bool:
        if bool(move.promotion) and move.promotion.lower() != "q":
            return True

        mrm: EngineResponse.MultiEngineResponse
        pos_rm: int
        mrm, pos_rm = move.analysis
        rm: EngineResponse.EngineResponse = mrm.li_rm[pos_rm]
        if rm.promotion and rm.promotion.lower() != "q":
            return True

        return False

