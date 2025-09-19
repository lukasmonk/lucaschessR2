import FasterCode

from Code.Base import Position, Move
from Code.Engines import EngineResponse
from Code.Themes import CheckTheme


class BodenMate(CheckTheme.CheckTheme):
    def __init__(self):
        self.theme = "bodenMate"
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

        valid_bishop = "B" if is_white else "b"

        # Posición final
        position_before: Position.Position = move.position_before
        position: Position.Position = position_before.copia()
        li_pv = rm.pv.split(" ")
        for pos, pv in enumerate(li_pv):
            position.play_pv(pv)

        last_pv = li_pv[-1]
        cr_bishop1 = last_pv[2:4]
        pz_attack = position.get_pz(cr_bishop1)

        # Condición 1: La pieza que da mate debe ser un alfil.
        if pz_attack != valid_bishop:
            return False

        # Condición 2: dos alfiles
        cr_bishop2 = None
        for a1, pz in position.squares.items():
            if pz == valid_bishop:
                if a1 != cr_bishop1:
                    cr_bishop2 = a1
                    break
        if cr_bishop2 is None:
            return False

        # Condición 3: Verificar que todas las casillas de escape del rey están cubiertas.
        # El rey está en jaque por el alfil 1, por lo que su casilla ya está controlada.
        # Ahora verificamos las 8 casillas adyacentes.

        def is_attack_diagonal(row_origen, col_origen, row_destino, col_destino):
            """Verifica si hay un ataque diagonal sin obstrucciones entre dos casillas."""
            # Comprobar si las casillas están en la misma diagonal
            if abs(row_origen - row_destino) != abs(col_origen - col_destino):
                return False

            # Determinar la dirección del recorrido
            drow = 1 if row_destino > row_origen else -1
            dcol = 1 if col_destino > col_origen else -1

            # Recorrer la diagonal para buscar piezas bloqueadoras
            row_actual, col_actual = row_origen + drow, col_origen + dcol
            while (row_actual, col_actual) != (row_destino, col_destino):
                cr = self.col_row_cr(col_actual, row_actual)
                if position.get_pz(cr) is not None:
                    return False  # Hay una pieza bloqueando el camino
                row_actual += drow
                col_actual += dcol

            return True  # El camino está despejado

        pos_cr_king = position.get_pos_king(not is_white)
        col_king, row_king = self.cr_col_row(pos_cr_king)

        col_bishop1, row_bishop1 = self.cr_col_row(cr_bishop1)
        col_bishop2, row_bishop2 = self.cr_col_row(cr_bishop2)

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue

                row_escape = row_king + dr
                col_escape = col_king + dc
                if not (0 <= row_escape < 8 and 0 <= col_escape < 8):
                    continue

                cr_escape = FasterCode.pos_a1(FasterCode.rc_pos(row_escape, col_escape))
                pz_escape = position.get_pz(cr_escape)

                if pz_escape is None:
                    # Si la casilla está vacía, debe estar atacada por uno de los dos alfiles.
                    ataque1 = is_attack_diagonal(row_bishop1, col_bishop1, row_escape, col_escape)
                    ataque2 = is_attack_diagonal(row_bishop2, col_bishop2, row_escape, col_escape)
                    if not (ataque1 or ataque2):
                        return False  # Se encontró una casilla de escape válida.
                else:
                    # Si está ocupada, debe ser por una pieza del bando defensor.
                    if (is_white and pz_escape.isupper()) or (not is_white and pz_escape.islower()):
                        return False

        # Si todas las casillas de escape están controladas o bloqueadas, es Mate de Boden.
        return True
