import FasterCode

from Code.Base import Move, Position
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class Pin(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "pin"

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

        position: Position.Position = move.position
        pz: str = position.get_pz(move.to_sq)
        if pz.lower() not in "qrbn":
            return False

        if self.first_case(move):
            return True

        if self.second_case(move):
            return True

        return False

    def first_case(self, move: Move.Move) -> bool:
        # Se mueve una pieza que no se puede capturar por un pin absoluto o por pérdida de material

        position: Position.Position = move.position.copia()
        is_white = move.is_white()
        sq_pz_moved = move.to_sq
        li_sq_pz = self.square_attacked(position, sq_pz_moved, not is_white)
        if len(li_sq_pz) != 1:
            return False
        sq_pinned, pz_attacker = li_sq_pz[0]
        if pz_attacker.lower() == "k":
            return False

        # Todos los movimientos posibles de las piezas rivales, no hay ninguno que sea la captura de esa pieza
        pin_absolute = True
        exmoves = position.get_exmoves()
        for exmove in exmoves:
            if exmove.xto() == sq_pz_moved:
                pin_absolute = False
                break
        if pin_absolute:
            return True

        # Si se puede capturar
        # miramos todas nuestras piezas que atacan sq_pinned
        li_attacked_sq_pz = self.square_attacked(position, sq_pz_moved, is_white)

        pos_pinned = FasterCode.a1_pos(sq_pinned)
        for sq, pz in li_attacked_sq_pz:
            # por si acaso la otra pieza (pz_moved) también ataca
            if sq == sq_pz_moved:
                continue

            posible_lines = self.lines_pz(pz, sq)

            pos_other: int
            for line in posible_lines:
                if pos_pinned in line:
                    for pos_other in line:
                        sq_other = FasterCode.pos_a1(pos_other)
                        pz_other = position.get_pz(sq_other)
                        # Si hay una pieza
                        if pz_other:
                            is_white_other = pz_other.isupper()
                            if is_white != is_white_other:
                                position_new = move.position.copia()
                                material_before = position_new.valor_material_side(is_white)
                                position_new.play(sq_pinned, sq_pz_moved, "")
                                position_new.play(sq, sq_other, "")
                                material_after = position_new.valor_material_side(is_white)
                                if material_after > material_before:
                                    return True
                        break

                    break

        return False

    def second_case(self, move: Move.Move) -> bool:
        # Se mueve una pieza que ataca una pieza que no se puede mover porque detrás está el rey o otra pieza valiosa
        position: Position.Position = move.position.copia()
        is_white = move.is_white()
        sq_pz_moved = move.to_sq
        pz_moved = position.get_pz(sq_pz_moved)

        # Solo piezas de largo recorrido
        if pz_moved.lower() not in ("q", "r", "b"):
            return False

        if move.is_check:
            return False

        # Si tiene al rey en rayos x
        line_sq_pz = self.xrays_king(position, pz_moved, sq_pz_moved, is_white)
        if line_sq_pz:
            # Hay solo una pieza en medio del rival no protegida

            def is_other_side(xpz):
                return xpz.islower() if is_white else xpz.isupper()

            # Sólo una pieza contraria en medio
            sq_other = pz_other = None
            # la ultima es el rey
            for sq, pz in line_sq_pz[:-1]:
                if pz is None:
                    continue

                if is_other_side(pz):
                    if sq_other:
                        sq_other = None
                        break
                    sq_other, pz_other = sq, pz
                else:
                    sq_other = pz_other = None
                    break

            if sq_other:
                # nos atacan?
                li_sq_pz_attacked = self.square_attacked(position, sq_pz_moved, not is_white)
                if len(li_sq_pz_attacked) == 0:
                    return self.pz_value(pz_other) >= self.pz_value(pz_moved)

                # Estamos atacados y también defendidos y los atacantes tienen mayor valor que nuestra pieza
                li_sq_pz_defended = self.square_defended(position, sq_pz_moved, is_white)
                if len(li_sq_pz_defended) > 0:
                    for sq_attack, pz_attack in li_sq_pz_attacked:
                        if self.pz_value(pz_attack) <= self.pz_value(pz_moved):
                            return False
                    return True

        return False
