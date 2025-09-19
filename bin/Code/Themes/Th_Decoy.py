from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class Decoy(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "decoy"

    def is_theme(self, move: Move.Move) -> bool:
        mrm: EngineResponse.MultiEngineResponse
        rm: EngineResponse.EngineResponse
        pos_rm: int
        mrm, pos_rm = move.analysis
        rm = mrm.li_rm[pos_rm]
        is_white = move.is_white()

        # It is a top move in analysis
        if not self.is_best_move(mrm, rm, pos_rm):
            return False

        # The situation is not lost
        if self.is_lost(rm):
            return False

        if move.has_theme("deflection"):
            return False

        # Movimientos
        pv = rm.pv
        li_pv = pv.split(" ")
        if len(li_pv) < 4:
            return False

        position: Position.Position = move.position.copia()

        # Que se capture el señuelo
        resp_rival = li_pv[1]
        if resp_rival[2:4] != move.to_sq:
            return False

        # Que haya perdida material, tras el segundo movimiento nuestro
        dif_material_inicial = position.valor_material_side(is_white) - position.valor_material_side(not is_white)
        position.play_pv(resp_rival)
        position.play_pv(li_pv[2])
        dif_material_tras_ownmove2 = position.valor_material_side(is_white) - position.valor_material_side(not is_white)
        if dif_material_inicial <= dif_material_tras_ownmove2:
            return False

        if rm.mate > 0:
            return True

        for pv in li_pv[3:5]:
            position.play_pv(pv)
        dif_material_final = position.valor_material_side(is_white) - position.valor_material_side(not is_white)

        if dif_material_final <= dif_material_inicial:
            return False

        for pv in li_pv[5:]:
            position.play_pv(pv)
        dif_material_final = position.valor_material_side(is_white) - position.valor_material_side(not is_white)

        if dif_material_final <= dif_material_inicial:
            return False

        return True
