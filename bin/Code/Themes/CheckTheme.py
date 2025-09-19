import FasterCode

from Code.Base import Move, Position
from Code.Base.Constantes import PZ_VALUES
from Code.Engines import EngineResponse


def dic_pawn(pos, is_white):
    li_m, li_x = FasterCode.li_p(pos, is_white)
    return [[x] for x in li_x]


dic_lines = {
    "Q": {pos: FasterCode.dict_q[pos] for pos in range(64)},
    "R": {pos: FasterCode.dict_r[pos] for pos in range(64)},
    "B": {pos: FasterCode.dict_b[pos] for pos in range(64)},
    "N": {pos: [[x] for x in FasterCode.dict_n[pos]] for pos in range(64)},
    "K": {pos: [[x] for x in FasterCode.dict_k[pos]] for pos in range(64)},
    "PW": {pos: dic_pawn(pos, True) for pos in range(64)},
    "PB": {pos: dic_pawn(pos, False) for pos in range(64)},
}


class CheckTheme:
    theme: str = ""
    is_mate: bool = False

    def check_move(self, move: Move.Move):
        if self.is_theme(move):
            move.add_theme(self.theme)
            return self.theme
        return None

    def is_theme(self, move: Move.Move) -> bool:
        pass

    @staticmethod
    def is_best_move(mrm: EngineResponse.MultiEngineResponse, rm: EngineResponse.EngineResponse, pos_rm: int) -> bool:
        if pos_rm:
            rm_best = mrm.best_rm_ordered()
            if rm_best.centipawns_abs() > rm.centipawns_abs():
                return False
        return True

    @staticmethod
    def is_unique_best_move(mrm: EngineResponse.MultiEngineResponse, rm: EngineResponse.EngineResponse,
                            pos_rm: int) -> bool:
        if pos_rm > 0:
            return False
        if len(mrm.li_rm) == 1:
            return True
        rm2 = mrm.li_rm[1]
        if (rm.centipawns_abs() - rm2.centipawns_abs()) < 200:
            return False
        return True

    @staticmethod
    def is_lost(rm: EngineResponse.EngineResponse) -> bool:
        if rm.centipawns_abs() < -100:
            return True
        return False

    @staticmethod
    def pz_value(pz) -> int:
        pz_upper = pz.upper()
        return 9999 if pz_upper == "K" else PZ_VALUES[pz.upper()]

    @staticmethod
    def cr_col_row(cr) -> tuple:
        pos = FasterCode.a1_pos(cr)
        row, col = FasterCode.pos_rc(pos)
        return col, row

    @staticmethod
    def col_row_cr(col, row) -> str:
        return FasterCode.pos_a1(FasterCode.rc_pos(row, col))

    @staticmethod
    def squares_round(cr) -> list:
        pos = FasterCode.a1_pos(cr)
        row, col = FasterCode.pos_rc(pos)
        li = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                xrow = row + dr
                xcol = col + dc
                if 0 <= xrow < 8 and 0 <= xcol < 8:
                    li.append(FasterCode.pos_a1(FasterCode.rc_pos(xrow, xcol)))
        return li

    @staticmethod
    def lines_pz(pz: str, square: str) -> list:
        pz_upper = pz.upper()
        if pz_upper == "P":
            pz_upper += "W" if pz.isupper() else "B"
        pos: int = FasterCode.a1_pos(square)
        return dic_lines[pz_upper][pos]

    def squares_controlled_by_piece(self, position: Position.Position, square: str, is_attacked: bool) -> list:
        pz: str = position.get_pz(square)
        is_white: bool = pz.isupper()

        posible_lines = self.lines_pz(pz, square)

        li_sq_controlled: list = []
        pos_other: int
        # son las propias de su bando mas las vacías. Si hay pieza corta la defensa
        for line in posible_lines:
            for pos_other in line:
                sq_other = FasterCode.pos_a1(pos_other)
                pz_other = position.get_pz(sq_other)
                # Si hay una pieza, se interrumpe la linea y se añade si es del mismo lado
                if pz_other:
                    is_white_other = pz_other.isupper()
                    if is_attacked:
                        if is_white != is_white_other:
                            li_sq_controlled.append(sq_other)
                    else:
                        if is_white == is_white_other:
                            li_sq_controlled.append(sq_other)
                    break
                li_sq_controlled.append(sq_other)

        return li_sq_controlled

    def squares_attacked_by_piece(self, position: Position.Position, square: str) -> list:
        return self.squares_controlled_by_piece(position, square, True)

    def squares_defended_by_piece(self, position: Position.Position, square: str) -> list:
        return self.squares_controlled_by_piece(position, square, False)

    def square_attacked(self, position: Position.Position, square: str, is_white_attacker: bool) -> list:
        # Lista de (square1, piece1) que atacan a la pieza que está en square
        li_attacked_sq_pz = []
        for sq, pz in position.squares.items():
            if pz and is_white_attacker == pz.isupper():
                li_attacked = self.squares_attacked_by_piece(position, sq)
                if square in li_attacked:
                    li_attacked_sq_pz.append((sq, pz))

        return li_attacked_sq_pz

    def square_defended(self, position: Position.Position, square: str, is_white: bool) -> list:
        # Lista de (square1, piece1) defendidos por la pieza que está en square
        li_defended_sq_pz = []
        for sq, pz in position.squares.items():
            if pz and is_white == pz.isupper():
                li_defended = self.squares_defended_by_piece(position, sq)
                if square in li_defended:
                    li_defended_sq_pz.append((sq, pz))

        return li_defended_sq_pz

    def xrays_king(self, position: Position.Position, pz: str, sq: str, is_white: bool) -> list:
        posible_lines = self.lines_pz(pz, sq)

        sq_other_king = position.get_pos_king(not is_white)
        pos_other_king = FasterCode.a1_pos(sq_other_king)

        for line in posible_lines:
            if pos_other_king in line:
                def pos_with_pz(pos):
                    a1 = FasterCode.pos_a1(pos)
                    return a1, position.get_pz(a1)

                return [pos_with_pz(pos) for pos in line]

        return []

    def all_lines_attacked_sq_pz(self, position:Position.Position, square: str) -> list:
        # se miran todas las lineas de ataque de la pieza en una casilla y se devuelve lineas de sq, pz
        all_lines: list = self.lines_pz(position.get_pz(square), square)

        li_sq_pz: list = []
        pos_other: int
        for line in all_lines:
            linea_sq_pz = []
            for pos_other in line:
                sq_other: str = FasterCode.pos_a1(pos_other)
                pz_other = position.get_pz(sq_other)
                if pz_other:
                    linea_sq_pz.append((sq_other, pz_other))
            if linea_sq_pz:
                li_sq_pz.append(linea_sq_pz)

        return li_sq_pz

    def line_attacked_sq_pz(self, position:Position.Position, square: str, square_other: str) -> list:
        # linea de ataque que pasa por dos casillas
        for line in self.all_lines_attacked_sq_pz(position, square):
            for sq, pz in line:
                if sq == square_other:
                    return line

        return []

    @staticmethod
    def dif_material(position:Position.Position, pv: str) -> int:
        is_white = position.is_white
        dif_material_inicial = position.valor_material_side(is_white) - position.valor_material_side(not is_white)
        work_position = position.copia()
        for a1h8 in pv.split(" "):
            work_position.play_pv(a1h8)
        dif_material_final = work_position.valor_material_side(is_white) - work_position.valor_material_side(not is_white)
        return dif_material_final-dif_material_inicial
