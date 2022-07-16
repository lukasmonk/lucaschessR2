import os

import FasterCode
from PySide2 import QtCore

from Code.Base import Position
from Code.Board import Board
from Code.Polyglots import PolyglotImportExports, DBPolyglot
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTVarios
from Code.Voyager import Voyager
from Code.QT import LCDialog


class WPolyglot(LCDialog.LCDialog):
    def __init__(self, wowner, configuration, path_lcbin):
        self.title = os.path.basename(path_lcbin)[:-6]
        LCDialog.LCDialog.__init__(self, wowner, self.title, Iconos.Book(), "polyglot")

        self.configuration = configuration
        self.path_lcbin = path_lcbin

        self.owner = wowner

        self.db_entries = DBPolyglot.DBPolyglot(path_lcbin)

        self.pol_import = PolyglotImportExports.PolyglotImport(self)
        self.pol_export = PolyglotImportExports.PolyglotExport(self)

        self.li_moves = []
        self.history = []

        conf_board = configuration.config_board("WPOLYGLOT", 48)
        self.board = Board.Board(self, conf_board)
        self.board.crea()
        self.board.set_dispatcher(self.mensajero)
        self.with_figurines = configuration.x_pgn_withfigurines

        o_columnas = Columnas.ListaColumnas()
        delegado = Delegados.EtiquetaPOS(True, siLineas=False) if self.configuration.x_pgn_withfigurines else None
        o_columnas.nueva("move", _("Move"), 80, align_center=True, edicion=delegado, is_editable=False)
        o_columnas.nueva("%", "%", 60, align_right=True, is_editable=False)
        o_columnas.nueva("weight", _("Weight"), 60, align_right=True, edicion=Delegados.LineaTexto(siEntero=True))
        o_columnas.nueva("score", _("Score"), 60, align_right=True, edicion=Delegados.LineaTexto(siEntero=True))
        o_columnas.nueva("depth", _("Depth"), 60, align_right=True, edicion=Delegados.LineaTexto(siEntero=True))
        o_columnas.nueva("learn", _("Learn"), 60, align_right=True, edicion=Delegados.LineaTexto(siEntero=True))
        self.grid_moves = Grid.Grid(self, o_columnas, is_editable=True)
        self.grid_moves.setMinimumWidth(self.grid_moves.anchoColumnas() + 20)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Takeback"), Iconos.Atras(), self.takeback),
            None,
            (_("Voyager"), Iconos.Voyager32(), self.voyager),
            None,
            (_("Import"), Iconos.Import8(), self.pol_import.importar),
            None,
            (_("Create book"), Iconos.BinBook(), self.pol_export.exportar),
            None,
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        ly2 = Colocacion.V().control(self.tb).control(self.grid_moves)

        layout = Colocacion.H().control(self.board).otro(ly2)
        self.setLayout(layout)

        self.restore_video()

        self.position = None
        position = Position.Position()
        position.set_pos_initial()
        self.set_position(position, True)

    def set_position(self, position, save_history):
        self.position = position
        self.position.set_lce()

        self.li_moves = [FasterCode.BinMove(info_move) for info_move in self.position.get_exmoves()]

        li = self.db_entries.get_entries(position.fen())
        d_entries = {entry.move: entry for entry in li}

        for binmove in self.li_moves:
            mv = binmove.imove()
            if mv in d_entries:
                binmove.set_entry(d_entries[mv])
                binmove.rowid = d_entries[mv].rowid
            else:
                binmove.rowid = 0

        tt = sum(binmove.weight() for binmove in self.li_moves)
        for binmove in self.li_moves:
            binmove.porc = binmove.weight() * 100.0 / tt if tt > 0 else 0

        self.li_moves.sort(key=lambda x: x.weight(), reverse=True)
        self.board.set_position(position)
        self.board.activate_side(position.is_white)
        if save_history:
            self.history.append(self.position.fen())
        self.grid_moves.refresh()
        self.grid_moves.gotop()

    def grid_doble_click(self, grid, row, col):
        if col.key == "move":
            bin_move = self.li_moves[row]
            xfrom = bin_move.info_move.xfrom()
            xto = bin_move.info_move.xto()
            promotion = bin_move.info_move.promotion()
            self.mensajero(xfrom, xto, promotion)

    def grid_cambiado_registro(self, grid, row, o_column):
        if -1 < row < len(self.li_moves):
            bin_move = self.li_moves[row]
            self.board.put_arrow_sc(bin_move.info_move.xfrom(), bin_move.info_move.xto())

    def grid_num_datos(self, grid):
        return len(self.li_moves)

    def grid_dato(self, grid, row, o_column):
        move = self.li_moves[row]
        key = o_column.key
        if key == "move":
            san = move.info_move.san()
            if self.with_figurines:
                is_white = self.position.is_white
                return san, is_white, None, None, None, None, False, True
            else:
                return san
        elif key == "%":
            return "%.1f%%" % move.porc if move.porc > 0 else ""
        else:
            valor = move.get_field(key)
            return str(valor) if valor else ""

    def grid_setvalue(self, grid, row, column, valor):
        binmove = self.li_moves[row]
        field = column.key
        valor = int(valor) if valor else 0
        hash_key = FasterCode.hash_polyglot8(self.position.fen())

        binmove.set_field(field, valor)
        entry = binmove.get_entry()
        if entry.key == 0:
            entry.key = hash_key
            entry.move = binmove.imove()

        rowid = self.db_entries.save_entry(binmove.rowid, entry)
        binmove.rowid = entry.rowid = rowid
        if rowid == 0:
            for field in ("score", "depth", "learn"):
                binmove.set_field(field, 0)

        if field == "weight":
            tt = sum(binmove.weight() for binmove in self.li_moves)
            for binmove in self.li_moves:
                binmove.porc = binmove.weight() * 100.0 / tt if tt else 0.0
            grid.refresh()

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            row, o_col = grid.current_position()
            field = o_col.key

            binmove = self.li_moves[row]

            if field in ("move", "%", "weight"):
                binmove.set_field("weight", 0)
                for xfield in ("score", "depth", "learn"):
                    binmove.set_field(xfield, 0)
            else:
                binmove.set_field(field, 0)

            entry = binmove.get_entry()
            if entry.key == 0:
                entry.key = FasterCode.hash_polyglot8(self.position.fen())
                entry.move = binmove.imove()

            self.db_entries.save_entry(binmove.rowid, entry)
            if entry.weight == 0:
                binmove.rowid = entry.rowid = 0  # borrados

                tt = sum(binmove.weight() for binmove in self.li_moves)
                for binmove in self.li_moves:
                    binmove.porc = binmove.weight() * 100.0 / tt if tt else 0.0

            grid.refresh()

    def mensajero(self, from_sq, to_sq, promocion=""):
        FasterCode.set_fen(self.position.fen())
        if FasterCode.make_move(from_sq + to_sq + promocion):
            fen = FasterCode.get_fen()
            self.position.read_fen(fen)
            self.set_position(self.position, True)

    def terminar(self):
        self.finalizar()
        self.accept()

    def closeEvent(self, event):
        self.finalizar()

    def finalizar(self):
        self.db_entries.close()
        self.save_video()

    def takeback(self):
        if len(self.history) > 1:
            self.history = self.history[:-1]
            fen = self.history[-1]
            self.position.read_fen(fen)
            self.set_position(self.position, False)

    def voyager(self):
        position = Voyager.voyager_position(self, self.position, wownerowner=self.owner)
        if position:
            self.set_position(position, True)
