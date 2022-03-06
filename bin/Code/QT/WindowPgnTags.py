from Code.Translations import TrListas
from Code.Base import Position
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTVarios, QTUtil2
from Code.Base.Constantes import STANDARD_TAGS
from Code.QT import LCDialog


class WTagsPGN(LCDialog.LCDialog):
    def __init__(self, procesador, liPGN, is_fen_possible):
        titulo = _("Edit PGN labels")
        icono = Iconos.PGN()
        extparam = "editlabels"
        self.listandard = STANDARD_TAGS
        self.is_fen_possible = is_fen_possible

        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, extparam)
        self.procesador = procesador
        self.creaLista(liPGN)

        # Toolbar
        liAccionesWork = (
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Up"), Iconos.Arriba(), self.arriba),
            None,
            (_("Down"), Iconos.Abajo(), self.abajo),
            None,
        )
        tbWork = QTVarios.LCTB(self, liAccionesWork, icon_size=24)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ETIQUETA", _("Label"), 150, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("VALOR", _("Value"), 400, edicion=Delegados.LineaTextoUTF8())

        self.grid = Grid.Grid(self, o_columns, siEditable=True)
        n = self.grid.anchoColumnas()
        self.grid.setFixedWidth(n + 20)
        self.register_grid(self.grid)

        # Layout
        layout = Colocacion.V().control(tbWork).control(self.grid).margen(3)
        self.setLayout(layout)

        self.restore_video()

    def creaLista(self, liPGN):
        st = {eti for eti, val in liPGN}

        li = [[k, v] for k, v in liPGN]
        for eti in self.listandard:
            if not (eti in st):
                li.append([eti, ""])
        while len(li) < 30:
            li.append(["", ""])
        self.liPGN = li

    def aceptar(self):
        self.save_video()
        self.accept()

    def closeEvent(self, event):
        self.save_video()

    def cancelar(self):
        self.save_video()
        self.reject()

    def grid_num_datos(self, grid):
        return len(self.liPGN)

    def grid_setvalue(self, grid, row, o_column, valor):
        col = 0 if o_column.key == "ETIQUETA" else 1
        if row < len(self.liPGN):
            valor = valor.strip()

            if col == 0 and valor.upper() == "FEN":
                if self.is_fen_possible:
                    valor = "FEN"
                else:
                    return

            self.liPGN[row][col] = valor

            if self.liPGN[row][0] == "FEN":
                fen = self.liPGN[row][1]
                if fen:
                    cp = Position.Position()
                    if not cp.is_valid_fen(fen):
                        QTUtil2.message_error(self, _("This FEN is invalid"))
                        self.liPGN[row][1] = ""
                    else:
                        cp.read_fen(fen)
                        if cp.is_initial():
                            self.liPGN[row][1] = ""

    def grid_dato(self, grid, row, o_column):
        if o_column.key == "ETIQUETA":
            lb = self.liPGN[row][0]
            ctra = lb.upper()
            trad = TrListas.pgnLabel(lb)
            if trad != ctra:
                key = trad
            else:
                if lb:
                    key = lb  # [0].upper()+lb[1:].lower()
                else:
                    key = ""
            return key
        if row < len(self.liPGN):
            return self.liPGN[row][1]

    def arriba(self):
        recno = self.grid.recno()
        if recno:
            self.liPGN[recno], self.liPGN[recno - 1] = self.liPGN[recno - 1], self.liPGN[recno]
            self.grid.goto(recno - 1, 0)
            self.grid.refresh()

    def abajo(self):
        n0 = self.grid.recno()
        if n0 < len(self.liPGN) - 1:
            n1 = n0 + 1
            self.liPGN[n0], self.liPGN[n1] = self.liPGN[n1], self.liPGN[n0]
            self.grid.goto(n1, 0)
            self.grid.refresh()


def editTagsPGN(procesador, liPGN, is_fen_possible):
    w = WTagsPGN(procesador, liPGN, is_fen_possible)
    if w.exec_():
        li = []
        st_eti = set()
        for eti, valor in w.liPGN:
            eti = eti.strip()
            valor = valor.strip()
            if eti in st_eti:
                continue
            if (len(eti) > 0) and (len(valor) > 0):
                li.append([eti, valor])
                st_eti.add(eti)
        return li
    else:
        return None
