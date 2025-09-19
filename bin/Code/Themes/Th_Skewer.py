from Code.Base import Move, Position
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class Skewer(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "skewer"

    def is_theme(self, move: Move.Move) -> bool:
        mrm: EngineResponse.MultiEngineResponse
        rm: EngineResponse.EngineResponse
        pos_rm: int
        mrm, pos_rm = move.analysis
        rm = mrm.li_rm[pos_rm]

        # The situation is not lost
        if self.is_lost(rm):
            return False

        # It is a top move in analysis
        if not self.is_best_move(mrm, rm, pos_rm):
            return False

        # La pieza es una de largo alcance
        position: Position.Position = move.position
        pz: str = position.get_pz(move.to_sq)
        if pz.lower() not in "qrb":
            return False

        # Al menos tres movimientos en el análisis
        pv = rm.pv
        li_pv = pv.split(" ")
        if len(li_pv) < 3:
            return False

        # Ataca a una pieza de mayor valor, que se aparta
        response = li_pv[1]
        cr_response = response[2:4]
        cr_response_from = response[:2]
        if move.to_sq == cr_response:
            # Si recaptura
            return False

        line_attacked_sq_pz = self.line_attacked_sq_pz(position, move.to_sq, cr_response_from)
        if len(line_attacked_sq_pz) < 2:
            return False

        # que no haya otras piezas en medio
        if line_attacked_sq_pz[0][0] != cr_response_from:
            return False

        # que se capture la pieza que está detrás
        sq_detras = line_attacked_sq_pz[1][0]

        if li_pv[2] != move.to_sq + sq_detras:
            return False

        # Que haya una diferencia positiva de material
        if self.dif_material(move.position_before, rm.pv) <= 0:
            return False

        return True
