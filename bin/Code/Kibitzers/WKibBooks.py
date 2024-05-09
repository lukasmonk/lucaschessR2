from PySide2 import QtCore

from Code.Books import Books
from Code.Kibitzers import WKibCommon
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos


class WPolyglot(WKibCommon.WKibCommon):
    def __init__(self, cpu):
        WKibCommon.WKibCommon.__init__(self, cpu, Iconos.Book())

        self.book = Books.Book("P", cpu.kibitzer.name, cpu.kibitzer.path_exe, True)
        self.book.polyglot()

        o_columns = Columnas.ListaColumnas()
        delegado = Delegados.EtiquetaPOS(True, siLineas=False) if self.with_figurines else None
        o_columns.nueva("MOVE", _("Move"), 80, align_center=True, edicion=delegado)
        o_columns.nueva("PORC", "%", 60, align_center=True)
        o_columns.nueva("WEIGHT", _("Weight"), 80, align_right=True)
        self.grid = Grid.Grid(self, o_columns, dicVideo=self.dicVideo, siSelecFilas=True, altoFila=self.cpu.configuration.x_pgn_rowheight)
        f = Controles.FontType(puntos=self.cpu.configuration.x_pgn_fontpoints)
        self.grid.set_font(f)

        li_acciones = (
            (_("Quit"), Iconos.Kibitzer_Close(), self.terminar),
            (_("Continue"), Iconos.Kibitzer_Play(), self.play),
            (_("Pause"), Iconos.Kibitzer_Pause(), self.pause),
            (_("Takeback"), Iconos.Kibitzer_Back(), self.takeback),
            (_("Manual position"), Iconos.Kibitzer_Voyager(), self.set_position),
            (_("Show/hide board"), Iconos.Kibitzer_Board(), self.config_board),
            ("%s: %s" % (_("Enable"), _("window on top")), Iconos.Kibitzer_Up(), self.windowTop),
            ("%s: %s" % (_("Disable"), _("window on top")), Iconos.Kibitzer_Down(), self.windowBottom),
        )
        self.tb = Controles.TBrutina(self, li_acciones, with_text=False, icon_size=24)
        self.tb.set_action_visible(self.play, False)

        ly1 = Colocacion.H().control(self.board).control(self.grid)
        layout = Colocacion.V().control(self.tb).espacio(-8).otro(ly1).margen(3)
        self.setLayout(layout)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.cpu.check_input)
        self.timer.start(500)

        self.restore_video(self.dicVideo)
        self.ponFlags()

    def grid_doble_click(self, grid, row, o_column):
        if 0 <= row < len(self.li_moves):
            alm = self.li_moves[row]
            mov = alm.from_sq + alm.to_sq + alm.promotion
            self.game.read_pv(mov)
            self.reset()

    def grid_cambiado_registro(self, grid, row, o_column):
        self.ponFlecha(row)

    def ponFlecha(self, row):
        if -1 < row < len(self.li_moves):
            alm = self.li_moves[row]
            self.board.put_arrow_sc(alm.from_sq, alm.to_sq)

    def grid_num_datos(self, grid):
        return len(self.li_moves)

    def grid_dato(self, grid, row, o_column):
        alm = self.li_moves[row]

        # alm = Util.Record()
        # alm.from_sq, alm.to_sq, alm.promotion = pv[:2], pv[2:4], pv[4:]
        # alm.pgn = position.pgn_translated(alm.from_sq, alm.to_sq, alm.promotion)
        # alm.pgnRaw = position.pgn(alm.from_sq, alm.to_sq, alm.promotion)
        # alm.porc = "%0.02f%%" % (w * 100.0 / total,) if total else ""
        # alm.weight = w

        key = o_column.key
        if key == "MOVE":
            if self.with_figurines:
                is_white = self.game.last_position.is_white
                return alm.pgnRaw, is_white, None, None, None, None, False, True
            else:
                return alm.pgn
        elif key == "PORC":
            return alm.porc
        elif key == "WEIGHT":
            return "%d" % alm.weight

    def whether_to_analyse(self):
        siW = self.game.last_position.is_white
        if not self.siPlay or (siW and (not self.is_white)) or ((not siW) and (not self.is_black)):
            return False
        return True

    def orden_game(self, game):
        self.game = game
        if self.siPlay:
            position = game.last_position
            self.siW = position.is_white
            self.board.set_position(position)
            self.board.activate_side(self.siW)
            self.li_moves = self.book.alm_list_moves(position.fen())
            self.grid.gotop()
            self.grid.refresh()
            self.ponFlecha(0)
