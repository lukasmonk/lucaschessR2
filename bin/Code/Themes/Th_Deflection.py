from Code.Base import Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class Deflection(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "deflection"

    def is_theme(self, move: Move.Move) -> bool:
        mrm: EngineResponse.MultiEngineResponse
        rm: EngineResponse.EngineResponse
        pos_rm: int
        mrm, pos_rm = move.analysis
        rm = mrm.li_rm[pos_rm]

        # It is a top move in analysis
        if not self.is_best_move(mrm, rm, pos_rm):
            return False

        # The situation is not lost
        if self.is_lost(rm):
            return False

        # Condicion 1: tenemos movimientos suficientes para analizar
        pv = rm.pv
        li_pv = pv.split(" ")
        if len(li_pv) < 3:
            return False

        # Condicion 2: el movimiento no es de rey y hay piezas en el bando contrario
        pz = move.position_before.get_pz(move.from_sq)
        if pz.lower() in "k":
            return False
        npz_w, npz_b = move.position.num_allpiezas_wb()
        if npz_w == 1 or npz_b == 1:
            return False

        # Condicion 3: no es una captura o es una captura con perdida de material
        pz_captured = move.position_before.get_pz(move.to_sq)
        if pz_captured:
            if self.pz_value(pz) < self.pz_value(pz_captured):
                return False
            if self.dif_material(move.position_before, " ".join(li_pv[:3])) > 0:
                return False

        #  Condicion 4: con la pieza movida, se liberan casillas defendidas
        pv_rival1 = li_pv[1]
        li_rival_defended_previous = self.squares_defended_by_piece(move.position_before, pv_rival1[:2])
        position = move.position.copia()
        position.play_pv(pv_rival1)
        li_rival_defended_after = self.squares_defended_by_piece(position, pv_rival1[2:4])
        st_rival_defended_previous = set(li_rival_defended_previous)
        st_rival_defended_after = set(li_rival_defended_after)
        st_rival_undefended = st_rival_defended_previous - st_rival_defended_after

        # Quitamos las que están defendidas por otras piezas del rival
        is_white = move.is_white()
        st_rival_undefended_final = {
            square for square in st_rival_undefended
            if not self.square_attacked(move.position, square, not is_white)
        }

        # Caso se captura una pieza en una de las casillas no defendidas o lleva a un mate o promocione
        pv_user2 = li_pv[2]
        cr_user2_to = pv_user2[2:4]
        if cr_user2_to in st_rival_undefended_final:
            if rm.mate > 0:
                return True
            pz_captured2 = position.get_pz(cr_user2_to)
            if pz_captured2 or len(pv_user2) == 5:
                dif_material = self.dif_material(move.position_before, " ".join(li_pv))
                return dif_material > 0

        return False
