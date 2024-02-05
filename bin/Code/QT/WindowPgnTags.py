from PySide2 import QtGui

import Code
from Code.Base import Position
from Code.Base.Constantes import STANDARD_TAGS
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTVarios, QTUtil2
from Code.Translations import TrListas


class WTagsPGN(LCDialog.LCDialog):
    def __init__(self, wowner, li_pgn, is_fen_possible):
        titulo = _("Edit PGN labels")
        icono = Iconos.PGN()
        extparam = "editlabels"
        self.listandard = STANDARD_TAGS
        self.is_fen_possible = is_fen_possible

        LCDialog.LCDialog.__init__(self, wowner, titulo, icono, extparam)
        self.procesador = Code.procesador
        self.creaLista(li_pgn)

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

        self.grid = Grid.Grid(self, o_columns, is_editable=True)
        n = self.grid.anchoColumnas()
        self.grid.setFixedWidth(n + 20)
        self.register_grid(self.grid)

        # Layout
        layout = Colocacion.V().control(tbWork).control(self.grid).margen(3)
        self.setLayout(layout)

        self.restore_video()

    def creaLista(self, li_pgn):
        st = {eti for eti, val in li_pgn}

        li = [[k, v] for k, v in li_pgn]
        for eti in self.listandard:
            if not (eti in st):
                li.append([eti, ""])
        while len(li) < 30:
            li.append(["", ""])
        self.li_pgn = li

    def aceptar(self):
        self.save_video()
        self.accept()

    def closeEvent(self, event):
        self.save_video()

    def cancelar(self):
        self.save_video()
        self.reject()

    def grid_num_datos(self, grid):
        return len(self.li_pgn)

    def grid_setvalue(self, grid, row, o_column, valor):
        col = 0 if o_column.key == "ETIQUETA" else 1
        if row < len(self.li_pgn):
            valor = valor.strip()

            if col == 0 and valor.upper() == "FEN":
                if self.is_fen_possible:
                    valor = "FEN"
                else:
                    return

            self.li_pgn[row][col] = valor

            if self.li_pgn[row][0] == "FEN":
                fen = self.li_pgn[row][1]
                if fen:
                    cp = Position.Position()
                    if not cp.is_valid_fen(fen):
                        QTUtil2.message_error(self, _("This FEN is invalid"))
                        self.li_pgn[row][1] = ""
                    else:
                        cp.read_fen(fen)
                        if cp.is_initial():
                            self.li_pgn[row][1] = ""

    def grid_dato(self, grid, row, o_column):
        if o_column.key == "ETIQUETA":
            lb = self.li_pgn[row][0]
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
        if row < len(self.li_pgn):
            return self.li_pgn[row][1]

    def grid_remove(self):
        row = self.grid.recno()
        if row < len(self.li_pgn):
            self.li_pgn[row][1] = ""
            self.grid.refresh()

    def arriba(self):
        recno = self.grid.recno()
        if recno:
            self.li_pgn[recno], self.li_pgn[recno - 1] = self.li_pgn[recno - 1], self.li_pgn[recno]
            self.grid.goto(recno - 1, 0)
            self.grid.refresh()

    def abajo(self):
        n0 = self.grid.recno()
        if n0 < len(self.li_pgn) - 1:
            n1 = n0 + 1
            self.li_pgn[n0], self.li_pgn[n1] = self.li_pgn[n1], self.li_pgn[n0]
            self.grid.goto(n1, 0)
            self.grid.refresh()


def edit_tags_pgn(wowner, li_pgn, is_fen_possible):
    w = WTagsPGN(wowner, li_pgn, is_fen_possible)
    if w.exec_():
        li = []
        st_eti = set()
        for eti, valor in w.li_pgn:
            eti = eti.strip()
            valor = str(valor).strip()
            if eti in st_eti:
                continue
            if (len(eti) > 0) and (len(valor) > 0):
                li.append([eti, valor])
                st_eti.add(eti)
        return li
    else:
        return None


def menu_pgn_labels(wowner, game) -> bool:
    pos_cursor = QtGui.QCursor.pos()
    menu = QTVarios.LCMenu(wowner)
    f = Controles.TipoLetra(puntos=10, peso=75)
    menu.ponFuente(f)

    is_opening = False
    is_eco = False
    for key, valor in game.li_tags:
        trad = TrListas.pgnLabel(key)
        if trad != key:
            key = trad
        menu.opcion(key, "%s : %s" % (key, valor), Iconos.PuntoAzul())
        if key.upper() == "OPENING":
            is_opening = True
        if key.upper() == "ECO":
            is_eco = True

    menu.separador()
    menu.opcion("pgn", _("Edit PGN labels"), Iconos.PGN())

    opening = None
    if not is_opening or not is_eco:
        opening = game.opening
        if opening:
            if not is_opening:
                ape = _("Opening")
                nom = opening.tr_name
                label = nom if ape.upper() in nom.upper() else ("%s : %s" % (ape, nom))

                if not is_eco:
                    label += f" ({opening.eco})"
                    key = "add_opening_eco"
                else:
                    key = "add_opening"
            else:
                key = "add_eco"
                label = f"ECO: {opening.eco}"

            menu.separador()
            menu.opcion(key, label, Iconos.Mas())

    resp = menu.lanza()
    if resp:
        if resp.startswith("add_"):
            if "opening" in resp:
                game.set_tag("Opening", opening.tr_name)
            if "eco" in resp:
                game.set_tag("ECO", opening.eco)
            QtGui.QCursor.setPos(pos_cursor)
            return menu_pgn_labels(wowner, game)
        else:
            return True

    return False
