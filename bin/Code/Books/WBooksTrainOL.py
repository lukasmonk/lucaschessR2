import FasterCode

import Code
from Code import Util
from Code.Base import Position
from Code.Base.Constantes import (WHITE, BLACK, FEN_INITIAL, FIRST_BEST_MOVE, ALL_MOVES)
from Code.Books import Books, WBooks, Polyglot
from Code.QT import Colocacion
from Code.QT import Columnas, Grid
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Voyager import Voyager


class BooksTrainOL(object):
    def __init__(self):
        self.lines = []
        self.side = WHITE
        self.start_fen = ""
        self.book_w = None
        self.mode_w = FIRST_BEST_MOVE
        self.book_b = None
        self.mode_b = ALL_MOVES
        self.limit_depth = 0
        self.limit_lines = 0
        self.li_trainings = []
        self.dic_fenm2 = {}

    def dic(self):
        return {
            "SIDE": self.side,
            "START_FEN": self.start_fen,
            "BOOK_WHITE": self.book_w,
            "MODE_WHITE": self.mode_w,
            "BOOK_BLACK": self.book_b,
            "MODE_BLACK": self.mode_b,
            "MAX_DEPTH": self.limit_depth,
            "MAX_LINES": self.limit_lines
        }

    def read_dic(self, dic_read):
        self.side = dic_read.get("SIDE", self.side)
        self.start_fen = dic_read.get("START_FEN", self.start_fen)
        self.book_w = dic_read.get("BOOK_WHITE", self.book_w)
        self.mode_w = dic_read.get("MODE_WHITE", self.mode_w)
        self.book_b = dic_read.get("BOOK_BLACK", self.book_b)
        self.mode_b = dic_read.get("MODE_BLACK", self.mode_b)
        self.limit_depth = dic_read.get("MAX_DEPTH", self.limit_depth)
        self.limit_lines = dic_read.get("MAX_LINES", self.limit_lines)

    def read_config(self):
        dic = Code.configuration.read_variables("BOOKSTRAININGLO")
        if dic:
            self.read_dic(dic)

    def write_config(self):
        Code.configuration.write_variables("BOOKSTRAININGLO", self.dic())

    def copy_other(self, reg):
        dic_other = reg.dic()
        self.read_dic(dic_other)

    def current_training(self) -> dict:
        if not self.li_trainings or self.li_trainings[-1]["DATE_END"]:
            dic_training = {
                "DATE_INIT": Util.today(),
                "POS": 0,
                "ERRORS": 0,
                "HINTS": 0,
                "DATE_EMD": None,
                "TIME_USED": 0
            }
        else:
            dic_training = self.li_trainings[-1]
        return dic_training

    def set_last_training(self, pos, errors, hints, time_used):
        dic_training = self.current_training()
        dic_training["POS"] = pos
        dic_training["ERRORS"] = errors
        dic_training["HINTS"] = hints
        dic_training["TIME_USED"] = time_used
        if pos >= len(self.lines):
            dic_training["DATE_END"] = Util.today()
        else:
            dic_training["DATE_END"] = None
        if not self.li_trainings or self.li_trainings[-1]["DATE_END"]:
            self.li_trainings.append(dic_training)
        else:
            self.li_trainings[-1] = dic_training


class WBooksTrainOL(LCDialog.LCDialog):
    def __init__(self, owner, dbli_books_train):

        titulo = _("Train the opening lines of a book")
        LCDialog.LCDialog.__init__(self, owner, titulo, Iconos.Opening(), "book_openings_ol1")

        self.dbli_books_train = dbli_books_train
        self.dic_modes = Polyglot.dic_modes()

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("SIDE", _("Side"), 50, align_center=True)
        o_columns.nueva("BOOK_WHITE", _("White book"), 120, align_center=True)
        o_columns.nueva("MODE_WHITE", _("Mode"), 120, align_center=True)
        o_columns.nueva("BOOK_BLACK", _("Black book"), 120, align_center=True)
        o_columns.nueva("MODE_BLACK", _("Mode"), 120, align_center=True)
        o_columns.nueva("LIMIT_DEPTH", _("Max depth"), 80, align_center=True)
        o_columns.nueva("LIMIT_LINES", _("Max lines"), 100, align_center=True)
        o_columns.nueva("NUM_LINES", _("Lines"), 60, align_center=True)
        o_columns.nueva("NUM_TRAININGS", _("Trainings"), 60, align_center=True)
        o_columns.nueva("START_FEN", _("Start position"), 100, align_center=True)
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)

        self.tb = QTVarios.LCTB(self)
        self.tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        self.tb.new(_("Train"), Iconos.Empezar(), self.train)
        self.tb.new(_("New"), Iconos.Nuevo(), self.nuevo)
        self.tb.new(_("Copy"), Iconos.Copiar(), self.copy)
        self.tb.new(_("Remove"), Iconos.Borrar(), self.borrar)
        self.tb.new(_("Up"), Iconos.Arriba(), self.tw_up)
        self.tb.new(_("Down"), Iconos.Abajo(), self.tw_down)
        self.tb.new(_("History"), Iconos.Historial(), self.historial)

        ly_tb = Colocacion.H().control(self.tb).margen(0)
        ly = Colocacion.V().otro(ly_tb).control(self.grid).margen(3)
        self.setLayout(ly)

        self.register_grid(self.grid)
        self.restore_video()

        self.grid.gotop()

        self.train_rowid = None

    def grid_doble_click(self, grid, row, column):
        self.train()

    def grid_num_datos(self, grid):
        return len(self.dbli_books_train)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        reg: BooksTrainOL = self.dbli_books_train[row]
        if col == "SIDE":
            return _("White") if reg.side == WHITE else _("Black")
        if col == "BOOK_WHITE":
            return reg.book_w["name"]
        if col == "BOOK_BLACK":
            return reg.book_b["name"]
        if col in ("MODE_WHITE", "MODE_BLACK"):
            mode = reg.mode_w if col == "MODE_WHITE" else reg.mode_b
            return self.dic_modes[mode]
        if col == "LIMIT_DEPTH":
            return str(reg.limit_depth) if reg.limit_depth else ""
        if col == "LIMIT_LINES":
            return str(reg.limit_lines) if reg.limit_lines else ""
        if col == "NUM_LINES":
            return str(len(reg.lines))
        if col == "NUM_TRAININGS":
            return str(len(reg.li_trainings))
        if col == "START_FEN":
            return reg.start_fen

    def terminar(self):
        self.save_video()
        self.accept()

    def closeEvent(self, event):
        self.save_video()
        self.reject()

    def edit(self, pos):
        reg = BooksTrainOL()
        if pos == -1:
            reg.read_config()
        else:
            reg.copy_other(self.dbli_books_train[pos])
        w = WGenBooksTrainOL(self, reg)
        if w.exec_():
            self.dbli_books_train.append(reg, True)
            self.grid.refresh()
            self.grid.gotop()

    def nuevo(self):
        self.edit(-1)

    def copy(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            self.edit(li[0])

    def borrar(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                li.sort(reverse=True)
                for pos in li:
                    del self.dbli_books_train[pos]
                self.dbli_books_train.pack()
        self.grid.refresh()

    def historial(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            w = WBooksTrainOLHistory(self, li[0])
            w.exec_()

    def tw_up(self):
        recno = self.grid.recno()
        if 0 < recno < len(self.dbli_books_train):
            r0 = recno
            r1 = recno - 1
            reg0 = self.dbli_books_train[r0]
            reg1 = self.dbli_books_train[r1]
            self.dbli_books_train[r0] = reg1
            self.dbli_books_train[r1] = reg0
            self.grid.refresh()
            self.grid.goto(r1, 0)

    def tw_down(self):
        recno = self.grid.recno()
        if 0 <= recno < len(self.dbli_books_train) - 1:
            r0 = recno
            r1 = recno + 1
            reg0 = self.dbli_books_train[r0]
            reg1 = self.dbli_books_train[r1]
            self.dbli_books_train[r0] = reg1
            self.dbli_books_train[r1] = reg0
            self.grid.refresh()
            self.grid.goto(r1, 0)

    def train(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            self.train_rowid = self.dbli_books_train.rowid(li[0])
            self.terminar()


class WGenBooksTrainOL(LCDialog.LCDialog):
    def __init__(self, w_parent, reg: BooksTrainOL):
        titulo = _("Train the opening lines of a book")
        icono = Iconos.Opening()

        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, "bookstrainol")

        self.reg = reg

        self.list_books = Books.ListBooks()
        dic_data = self.reg.dic()

        flb = Controles.FontType(puntos=10)

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new(_("Accept"), Iconos.Aceptar(), self.aceptar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancelar)
        tb.new(_("Books"), Iconos.Book(), self.register_books)

        # Side
        side = dic_data.get("SIDE", WHITE)
        self.rb_white = Controles.RB(self, _("White"))
        self.rb_white.setChecked(side == WHITE)
        self.rb_black = Controles.RB(self, _("Black"))
        self.rb_black.setChecked(side == BLACK)

        hbox = Colocacion.H().relleno().control(self.rb_white).espacio(30).control(self.rb_black).relleno()
        gb_side = Controles.GB(self, _("Side you play with"), hbox).set_font(flb)

        # Start position
        self.bt_position = Controles.PB(self, "", self.change_start_position).ponPlano(False)
        bt_position_remove = Controles.PB(self, "", self.remove_start_position).ponIcono(Iconos.Motor_No())
        bt_position_paste = Controles.PB(self, "", self.paste_start_position).ponIcono(Iconos.Pegar16()).ponToolTip(
            _("Paste FEN position"))
        hbox = (
            Colocacion.H()
            .relleno()
            .control(bt_position_remove)
            .control(self.bt_position)
            .control(bt_position_paste)
            .relleno()
        )
        gb_start_position = Controles.GB(self, _("Start position"), hbox).set_font(flb)

        # Books
        li_books = [(x.name, x) for x in self.list_books.lista]
        li_modes = [(name, key) for key, name in Polyglot.dic_modes().items()]

        def book_obj(key):
            dic_book: dict = dic_data.get(key)
            if dic_book:
                path = dic_book["path"]
                for name, book in li_books:
                    if path == book.path:
                        return book
            return None

        self.cb_white = Controles.CB(self, li_books, book_obj("BOOK_WHITE"))
        self.cb_mode_white = Controles.CB(self, li_modes, dic_data.get("MODE_WHITE"))

        lybook = Colocacion.H().relleno().control(self.cb_white).control(self.cb_mode_white).relleno()

        gb_white = Controles.GB(self, _("White book"), lybook).set_font(flb)

        # Black
        self.cb_black = Controles.CB(self, li_books, book_obj("BOOK_BLACK"))
        self.cb_mode_black = Controles.CB(self, li_modes, dic_data.get("MODE_BLACK"))

        lybook = Colocacion.H().relleno().control(self.cb_black).control(self.cb_mode_black).relleno()

        gb_black = Controles.GB(self, _("Black book"), lybook).set_font(flb)

        layout_books = Colocacion.H().control(gb_white).control(gb_black)

        # Limits
        lb_limit_depth = Controles.LB2P(self, _("Max depth"))
        self.sb_limit_depth = Controles.SB(self, dic_data.get("MAX_DEPTH", 0), 0, 999)
        lb_limit_lines = Controles.LB2P(self, _("Max lines to parse"))
        self.sb_limit_lines = Controles.SB(self, dic_data.get("MAX_LINES", 0), 0, 99999)
        ly = Colocacion.G()
        ly.controld(lb_limit_depth, 0, 0)
        ly.control(self.sb_limit_depth, 0, 1)
        ly.controld(lb_limit_lines, 0, 2)
        ly.control(self.sb_limit_lines, 0, 3)

        no_limits = _("0=no limit")

        lb_info1 = Controles.LB(self, no_limits).set_font_type(puntos=8)
        lb_info2 = Controles.LB(self, no_limits).set_font_type(puntos=8)
        ly.control(lb_info1, 1, 1)
        ly.control(lb_info2, 1, 3)

        gb_limits = Controles.GB(self, _("Limits"), ly).set_font(flb)

        for gb in (gb_side, gb_white, gb_black, gb_limits, gb_start_position):
            Code.configuration.set_property(gb, "1")

        vlayout = Colocacion.V()
        vlayout.control(gb_side).espacio(5)
        vlayout.otro(layout_books).espacio(5)
        vlayout.control(gb_limits).espacio(5)
        vlayout.control(gb_start_position).espacio(5)
        vlayout.margen(20)

        layout = Colocacion.V().control(tb).otro(vlayout).margen(3)

        self.setLayout(layout)

        self.restore_video()
        self.show_position()

    def write_data(self):
        self.reg.side = self.rb_white.isChecked()
        self.reg.book_w = self.cb_white.valor().to_dic()
        self.reg.book_b = self.cb_black.valor().to_dic()
        self.reg.mode_w = self.cb_mode_white.valor()
        self.reg.mode_b = self.cb_mode_black.valor()
        self.reg.limit_depth = self.sb_limit_depth.valor()
        self.reg.limit_lines = self.sb_limit_lines.valor()

        self.reg.write_config()

        return self.gen_lines()

    def aceptar(self):
        if self.write_data():
            self.save_video()
            self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def register_books(self):
        WBooks.registered_books(self)
        self.list_books = Books.ListBooks()
        self.list_books.save()
        li = [(x.name, x) for x in self.list_books.lista]
        self.cb_white.rehacer(li, self.cb_white.valor())
        self.cb_black.rehacer(li, self.cb_black.valor())

    def gen_lines(self):
        path_book_w = self.reg.book_w["path"]
        path_book_b = self.reg.book_b["path"]

        mens_work = _("Working...")
        mens_depth = _("Depth")
        mens_lines = _("Lines")
        um = QTUtil2.waiting_message.start(self, mens_work, with_cancel=True)
        um.end_with_canceled = False

        def dispatch(xdepth, xlines):
            if xlines:
                um.label(f"{mens_work}<br>{mens_depth}: {xdepth:d}<br>{mens_lines}: {xlines:d}")
            if um.cancelado():
                um.end_with_canceled = True
                return False
            return True

        lines = Polyglot.gen_lines(path_book_w, path_book_b, self.reg.mode_w, self.reg.mode_b,
                                   self.reg.limit_lines, self.reg.limit_depth, self.reg.start_fen, dispatch)
        um.final()

        if um.end_with_canceled:
            return False

        # Must be end with the side move
        odd = self.reg.side == WHITE
        if " b " in self.reg.start_fen:
            odd = not odd
        for line in lines:
            is_odd = len(line) % 2 == 1
            if is_odd != odd:
                line.li_pv = line.li_pv[:len(line) - 1]
        lines_pv = [" ".join(line.li_pv) for line in lines if len(line)]
        lines_pv.sort()
        if len(lines_pv) == 0:
            QTUtil2.message_error(self, _("There is no lines"))
            return False

        um = QTUtil2.working(self)
        lines_resp = []
        for pos in range(len(lines_pv) - 1):
            pv = lines_pv[pos]
            pv_next = lines_pv[pos + 1]
            if not pv_next.startswith(pv):
                lines_resp.append(pv)
        lines_resp.append(lines_pv[-1])
        lines_resp = list(set(lines_resp))
        lines_resp.sort()

        dic_fenm2 = {}
        start_fen = self.reg.start_fen
        p = Position.Position()
        for line in lines_resp:
            li_pv = line.split(" ")
            if start_fen:
                FasterCode.set_fen(start_fen)
            else:
                FasterCode.set_init_fen()
            for pv in li_pv:
                fen = FasterCode.get_fen()
                p.read_fen(fen)
                fenm2 = p.fenm2()  # necesario pasar por Position, por coherencia en búsquedas con los legal
                if fenm2 not in dic_fenm2:
                    dic_fenm2[fenm2] = set()
                dic_fenm2[fenm2].add(pv)
                FasterCode.make_move(pv)

        self.reg.lines = lines_resp
        self.reg.dic_fenm2 = dic_fenm2

        um.final()

        return True

    def change_start_position(self):
        cp = Position.Position()
        cp.read_fen(self.reg.start_fen)
        position, is_white_bottom = Voyager.voyager_position(self, cp)
        if position is not None:
            self.reg.start_fen = position.fen()
            self.show_position()

    def show_position(self):
        if self.reg.start_fen in ("", FEN_INITIAL):
            self.reg.start_fen = ""
            label = " " * 15 + _("Change") + " " * 15
        else:
            label = " " * 5 + self.reg.start_fen + " " * 5
        self.bt_position.set_text(label)

    def remove_start_position(self):
        self.reg.start_fen = ""
        self.show_position()

    def paste_start_position(self):
        texto = QTUtil.get_txt_clipboard()
        if texto:
            cp = Position.Position()
            try:
                cp.read_fen(texto.strip())
                self.reg.start_fen = cp.fen()
                self.show_position()
            except:
                pass


class WBooksTrainOLHistory(LCDialog.LCDialog):
    def __init__(self, w_parent: WBooksTrainOL, pos_reg):
        titulo = _("History")
        icono = Iconos.Historial()

        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, "bookstrainol_history")

        self.dbli_books_train = w_parent.dbli_books_train
        self.reg: BooksTrainOL = self.dbli_books_train[pos_reg]
        self.pos_reg = pos_reg
        self.w_parent: WBooksTrainOL = w_parent

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("DATE_INIT", _("Start date"), 120, align_center=True)
        o_columns.nueva("POS", _("Current"), 80, align_center=True)
        o_columns.nueva("ERRORS", _("Errors"), 80, align_center=True)
        o_columns.nueva("HINTS", _("Hints"), 80, align_center=True)
        o_columns.nueva("DATE_END", _("End date"), 120, align_center=True)
        o_columns.nueva("TIME_USED", _("Time used"), 120, align_center=True)
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)

        self.tb = QTVarios.LCTB(self)
        self.tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        self.tb.new(_("Remove"), Iconos.Borrar(), self.borrar)

        # Colocamos
        ly_tb = Colocacion.H().control(self.tb).margen(0)
        ly = Colocacion.V().otro(ly_tb).control(self.grid).margen(3)

        self.setLayout(ly)

        self.register_grid(self.grid)
        self.restore_video()

        self.grid.gotop()

    def grid_doble_click(self, grid, row, column):
        self.empezar()

    def grid_num_datos(self, grid):
        return len(self.reg.li_trainings)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        dic: dict = self.reg.li_trainings[row]
        if col == "DATE_INIT":
            return Util.localDateT(dic["DATE_INIT"])
        if col == "POS":
            return f'{dic["POS"]:d}/{len(self.reg.lines):d}'
        if col == "ERRORS":
            return str(dic["ERRORS"])
        if col == "HINTS":
            return str(dic["HINTS"])
        if col == "DATE_END":
            date = dic["DATE_END"]
            return Util.localDateT(date) if date else ""
        if col == "TIME_USED":
            t = int(dic["TIME_USED"])
            h = t // 3600
            m = (t - h * 3600) // 60
            s = t - h * 3600 - m * 60
            return f"{h:02d}:{m:02d}:{s:02d}"

    def terminar(self):
        self.save_video()
        self.accept()

    def borrar(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                li.sort(reverse=True)
                for pos in li:
                    del self.reg.li_trainings[pos]
                self.dbli_books_train[self.pos_reg] = self.reg
                self.w_parent.grid.refresh()
        self.grid.gotop()
        self.grid.refresh()
