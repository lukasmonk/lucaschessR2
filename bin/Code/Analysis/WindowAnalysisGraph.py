from PySide2 import QtCore, QtWidgets

import Code
from Code.Analysis import Histogram
from Code.Board import Board
from Code.Nags import Nags
from Code.Openings import OpeningsStd
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2


class WAnalisisGraph(LCDialog.LCDialog):
    def __init__(self, wowner, manager, alm, show_analysis):
        titulo = _("Result of analysis")
        icono = Iconos.Estadisticas()
        extparam = "estadisticasv2"
        LCDialog.LCDialog.__init__(self, wowner, titulo, icono, extparam)
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )

        self.alm = alm
        self.procesador = manager.procesador
        self.manager = manager
        self.configuration = manager.configuration
        self.with_figurines = self.configuration.x_pgn_withfigurines
        self.show_analysis = show_analysis
        self.colorWhite = QTUtil.qtColorRGB(231, 244, 254)

        self.with_time = False
        for move in alm.lijg:
            if move.time_ms:
                self.with_time = True
                break

        def xcol():
            o_columns = Columnas.ListaColumnas()
            o_columns.nueva("NUM", _("N."), 50, align_center=True)
            o_columns.nueva(
                "MOVE",
                _("Move"),
                120,
                align_center=True,
                edicion=Delegados.EtiquetaPGN(True if self.with_figurines else None),
            )
            o_columns.nueva(
                "BEST",
                _("Best move"),
                120,
                align_center=True,
                edicion=Delegados.EtiquetaPGN(True if self.with_figurines else None),
            )
            o_columns.nueva("DIF", _("Difference"), 80, align_center=True)
            if self.with_time:
                o_columns.nueva("TIME", _("Time"), 50, align_right=True)
            o_columns.nueva("PORC", _("Accuracy"), 80, align_center=True)
            o_columns.nueva("ELO", _("Elo"), 80, align_center=True)
            return o_columns

        self.dicLiJG = {"A": self.alm.lijg, "W": self.alm.lijgW, "B": self.alm.lijgB}
        grid_all = Grid.Grid(self, xcol(), siSelecFilas=True, xid="A", siCabeceraMovible=False)
        ancho_grid = grid_all.anchoColumnas()
        self.register_grid(grid_all)
        grid_w = Grid.Grid(self, xcol(), siSelecFilas=True, xid="W", siCabeceraMovible=False)
        ancho_grid = max(grid_w.anchoColumnas(), ancho_grid)
        self.register_grid(grid_w)
        grid_b = Grid.Grid(self, xcol(), siSelecFilas=True, xid="B", siCabeceraMovible=False)
        ancho_grid = max(grid_b.anchoColumnas(), ancho_grid) + 24
        self.register_grid(grid_b)

        font = Controles.FontType(puntos=Code.configuration.x_sizefont_infolabels)

        self.emIndexes = Controles.EM(self, alm.indexesHTML).read_only().set_font(font)
        pb_save = Controles.PB(self, _("Save to game comments"), self.saveIndexes, plano=False)
        pb_save.ponIcono(Iconos.Grabar())
        ly0 = Colocacion.H().control(pb_save).relleno()
        ly = Colocacion.V().control(self.emIndexes).otro(ly0)
        w_idx = QtWidgets.QWidget()
        w_idx.setLayout(ly)

        self.em_elo = Controles.EM(self, alm.indexesHTMLelo).read_only().set_font(font)
        ly = Colocacion.V().control(self.em_elo)
        w_elo = QtWidgets.QWidget()
        w_elo.setLayout(ly)

        self.em_moves = Controles.EM(self, alm.indexesHTMLmoves).read_only().set_font(font)
        ly = Colocacion.V().control(self.em_moves)
        w_moves = QtWidgets.QWidget()
        w_moves.setLayout(ly)

        self.tab_grid = tab_grid = Controles.Tab()
        tab_grid.new_tab(grid_all, _("All moves"))
        tab_grid.new_tab(grid_w, _("White"))
        tab_grid.new_tab(grid_b, _("Black"))
        tab_grid.new_tab(w_idx, _("Indexes"))
        tab_grid.new_tab(w_elo, _("Elo"))
        tab_grid.new_tab(w_moves, _("Moves"))
        tab_grid.dispatchChange(self.tabChanged)
        self.tabActive = 0

        config_board = Code.configuration.config_board("ANALISISGRAPH", 60)
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_side_bottom(alm.is_white_bottom)

        self.rbShowValues = Controles.RB(self, _("Values"), rutina=self.cambiadoShow).activa(True)
        self.rbShowElo = Controles.RB(self, _("Elo average"), rutina=self.cambiadoShow)
        self.chbShowLostPoints = Controles.CHB(self, _("Show pawns lost"), self.getShowLostPoints()).capture_changes(
            self, self.showLostPointsChanged
        )
        ly_rb = (
            Colocacion.H()
            .espacio(40)
            .control(self.rbShowValues)
            .espacio(20)
            .control(self.rbShowElo)
            .espacio(30)
            .control(self.chbShowLostPoints)
            .relleno(1)
        )
        ly_left = Colocacion.V().control(tab_grid).otro(ly_rb).margen(0)
        ly_up = Colocacion.H().otro(ly_left).control(self.board)

        Controles.Tab().set_position("W")
        ancho = self.board.width() + ancho_grid
        self.htotal = [
            Histogram.Histogram(self, alm.hgame, grid_all, ancho, True),
            Histogram.Histogram(self, alm.hwhite, grid_w, ancho, True),
            Histogram.Histogram(self, alm.hblack, grid_b, ancho, True),
            Histogram.Histogram(self, alm.hgame, grid_all, ancho, False, alm.eloT),
            Histogram.Histogram(self, alm.hwhite, grid_w, ancho, False, alm.eloW),
            Histogram.Histogram(self, alm.hblack, grid_b, ancho, False, alm.eloB),
        ]
        lh = Colocacion.V()

        f = Controles.FontType(puntos=8)
        bt_left = Controles.PB(self, "←", rutina=self.scale_left).set_font(f)
        bt_down = Controles.PB(self, "↓", rutina=self.scale_down).set_font(f)
        bt_reset = Controles.PB(self, "=", rutina=self.scale_reset).set_font(f)
        bt_up = Controles.PB(self, "↑", rutina=self.scale_up).set_font(f)
        bt_right = Controles.PB(self, "→", rutina=self.scale_right).set_font(f)
        ly_bt = Colocacion.H().relleno().control(bt_left).control(bt_down).control(bt_reset)
        ly_bt.control(bt_up).control(bt_right).margen(0)

        for x in range(6):
            lh.control(self.htotal[x])
            if x:
                self.htotal[x].hide()
        lh.espacio(-7).otro(ly_bt)

        w_up = QtWidgets.QWidget(self)
        w_up.setLayout(ly_up.margen(3))

        w_down = QtWidgets.QWidget(self)
        w_down.setLayout(lh.margen(3))

        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(w_up)
        splitter.addWidget(w_down)
        self.register_splitter(splitter, "all")

        layout = Colocacion.V().margen(3).control(splitter)

        self.setLayout(layout)

        dic_def = {'_SIZE_': '1064,900', 'SP_all': [536, 354]}
        self.restore_video(dicDef=dic_def)

        grid_all.gotop()
        grid_b.gotop()
        grid_w.gotop()
        self.grid_left_button(grid_all, 0, None)

        self.scale_init()

    def valorShowLostPoints(self):
        # Llamada from_sq histogram
        return self.chbShowLostPoints.valor()

    def showLostPointsChanged(self):
        dic = {"SHOWLOSTPOINTS": self.valorShowLostPoints()}
        self.configuration.write_variables("ANALISIS_GRAPH", dic)
        self.cambiadoShow()

    def getShowLostPoints(self):
        dic = self.configuration.read_variables("ANALISIS_GRAPH")
        return dic.get("SHOWLOSTPOINTS", True) if dic else True

    def cambiadoShow(self):
        self.tabChanged(self.tab_grid.currentIndex())

    # def boardSizeChanged(self):
    #     th = self.board.height()
    #     self.tab_grid.setFixedHeight(th)
    #     self.emIndexes.setFixedHeight(th - 72)
    #     self.adjustSize()
    #     self.cambiadoShow()

    def tabChanged(self, ntab):
        QtWidgets.QApplication.processEvents()
        tab_vis = 0 if ntab >= 3 else ntab
        if self.rbShowElo.isChecked():
            tab_vis += 3
        for n in range(6):
            self.htotal[n].setVisible(False)
        self.htotal[tab_vis].setVisible(True)
        # self.adjustSize()
        self.tabActive = ntab

    def grid_cambiado_registro(self, grid, row, column):
        self.grid_left_button(grid, row, column)

    def saveIndexes(self):
        self.manager.game.set_first_comment(self.alm.indexesRAW)
        QTUtil2.temporary_message(self, _("Saved"), 1.8)

    def grid_left_button(self, grid, row, column):
        self.board.remove_arrows()
        move = self.dicLiJG[grid.id][row]
        self.board.set_position(move.position)
        mrm, pos = move.analysis
        rm = mrm.li_rm[pos]
        self.board.put_arrow_sc(rm.from_sq, rm.to_sq)
        rm = mrm.li_rm[0]
        self.board.creaFlechaMulti(rm.movimiento(), False)
        grid.setFocus()
        ta = self.tabActive if self.tabActive < 3 else 0
        self.htotal[ta].setPointActive(row)
        self.htotal[ta + 3].setPointActive(row)

        # dic, is_white = move.position.capturas()
        # self.capturas.pon(dic)

    def grid_doble_click(self, grid, row, column):
        move = self.dicLiJG[grid.id][row]
        mrm, pos = move.analysis
        self.show_analysis(
            self.procesador,
            self.procesador.xtutor,
            move,
            self.board.is_white_bottom,
            pos,
            main_window=self,
            must_save=False,
        )

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        nrecno = grid.recno()
        if k in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.grid_doble_click(grid, nrecno, None)
        elif k == QtCore.Qt.Key_Right:
            if nrecno + 1 < self.grid_num_datos(grid):
                grid.goto(nrecno + 1, 0)
        elif k == QtCore.Qt.Key_Left:
            if nrecno > 0:
                grid.goto(nrecno - 1, 0)
        else:
            return True  # que siga con el resto de teclas

    def grid_color_texto(self, grid, row, o_column):
        if grid.id == "A":
            move = self.alm.lijg[row]
        elif grid.id == "W":
            move = self.alm.lijgW[row]
        else:  # if grid.id == "B":
            move = self.alm.lijgB[row]
        if len(move.nag_color) == 2:
            nagc = move.nag_color[1]
            return Nags.nag_qcolor(nagc)

    def grid_alineacion(self, grid, row, o_column):
        if grid.id == "A":
            move = self.alm.lijg[row]
            return "i" if move.xsiW else "d"
        return None

    def grid_num_datos(self, grid):
        return len(self.dicLiJG[grid.id])

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        move = self.dicLiJG[grid.id][row]

        if column == "NUM":
            return " %s " % move.xnum

        elif column in ("MOVE", "BEST"):
            if self.with_figurines:
                delegado = o_column.edicion
                delegado.setWhite(move.is_white())
            mrm, pos = move.analysis
            rm0 = mrm.li_rm[pos if column == "MOVE" else 0]
            pv1 = rm0.pv.split(" ")[0]
            from_sq = pv1[:2]
            to_sq = pv1[2:4]
            promotion = pv1[4] if len(pv1) == 5 else None
            txt = rm0.abbrev_text_base()

            color = None
            if column == "MOVE":
                fenm2 = move.position.fenm2()
                nagc = move.nag_color[1]
                color = Nags.nag_color(nagc)
            else:
                fenm2 = move.position_before.get_fenm2()
            is_book = OpeningsStd.ap.is_book_fenm2(fenm2)
            book = "O" if is_book else None

            return move.position_before.pgn(from_sq, to_sq, promotion), color, txt, book, None

        elif column == "TIME":
            ms = move.time_ms
            return '%0.02f"' % (ms / 1000,) if ms else ""

        elif column == "DIF":
            mrm, pos = move.analysis
            rm0 = mrm.li_rm[0]
            rm1 = mrm.li_rm[pos]
            if rm0.mate:
                if rm1.mate:
                    return "" if rm0.mate == rm1.mate else "M↓%d" % (-rm0.mate + rm1.mate,)
                else:
                    return "M↓%d" % rm0.mate
            elif rm1.mate:
                return "⨠M"

            pts = rm0.score_abs5() - rm1.score_abs5()
            pts /= 100.0
            return "%0.2f" % pts

        elif column == "PORC":
            return "%3d%%" % move.porcentaje

        elif column == "ELO":
            return "%3d" % move.elo if move.elo else ""

    def closeEvent(self, event):
        self.save_video()

    def hscale(self, p_width, p_height):
        key = "HISTOGRAM"
        dic = Code.configuration.read_variables(key)
        scale_width = p_width * dic.get("P_WIDTH", 0.90)
        scale_height = p_height * dic.get("P_HEIGHT", 0.80)
        dic["P_WIDTH"] = scale_width
        dic["P_HEIGHT"] = scale_height
        Code.configuration.write_variables(key, dic)

        for i in range(6):
            self.htotal[i].resetMatrix()
            self.htotal[i].scale(scale_width, scale_height)

    def scale_reset(self):
        key = "HISTOGRAM"
        dic = Code.configuration.read_variables(key)
        dic["P_WIDTH"] = scale_width = 0.90
        dic["P_HEIGHT"] = scale_height = 0.80
        Code.configuration.write_variables(key, dic)

        for i in range(6):
            self.htotal[i].resetMatrix()
            self.htotal[i].scale(scale_width, scale_height)

    def scale_left(self):
        self.hscale(0.95, 1.0)

    def scale_right(self):
        self.hscale(1.05, 1.0)

    def scale_up(self):
        self.hscale(1.0, 1.05)

    def scale_down(self):
        self.hscale(1.0, 0.95)

    def scale_init(self):
        self.hscale(1.0, 1.0)


def show_graph(wowner, manager, alm, show_analysis):
    w = WAnalisisGraph(wowner, manager, alm, show_analysis)
    w.exec_()
