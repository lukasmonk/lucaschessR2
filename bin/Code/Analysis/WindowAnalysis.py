import time

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code import XRun
from Code.Analysis import WindowAnalysisParam, Analysis
from Code.Base import Game
from Code.Base import Move
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class OneAnalysis(QtWidgets.QWidget):
    def __init__(self, owner, tab_analysis):
        super(OneAnalysis, self).__init__(owner)

        self.tab_analysis = tab_analysis
        self.owner = owner

        self.time_engine = tab_analysis.time_engine()
        self.time_label = tab_analysis.time_label()

        self.board = owner.board

        self.lb_engine_m = Controles.LB(self, self.time_engine).align_center().set_font_type(puntos=9, peso=75)
        self.lb_tiempo_m = Controles.LB(self, self.time_label).align_center().set_font_type(puntos=9, peso=75)
        self.dic_fonts = {True: "blue", False: "grey"}

        self.bt_cancelar = Controles.PB(self, "", self.cancelar).ponIcono(Iconos.X())

        self.lbPuntuacion = owner.lbPuntuacion
        self.lb_engine = owner.lb_engine
        self.lb_time = owner.lb_time
        self.lbPGN = owner.lbPGN

        self.list_rm_name = tab_analysis.list_rm_name  # rm, name, centipawns
        self.siTiempoActivo = False

        self.colorNegativo = QTUtil.qtColorRGB(255, 0, 0)
        self.colorImpares = QTUtil.qtColorRGB(231, 244, 254)

        configuration = Code.configuration

        self.with_figurines = configuration.x_pgn_withfigurines
        with_col = (configuration.x_pgn_width - 52 - 24) // 2
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva(
            "JUGADAS",
            "%d %s" % (len(self.list_rm_name), _("Movements")),
            with_col,
            align_center=True,
            edicion=Delegados.EtiquetaPGN(tab_analysis.move.is_white() if self.with_figurines else None),
        )
        self.wrm = Grid.Grid(self, o_columns, siLineas=False)
        n_with = self.wrm.anchoColumnas() + 20
        self.wrm.setFixedWidth(n_with)
        self.wrm.goto(self.tab_analysis.pos_selected, 0)

        # Layout
        ly2 = Colocacion.H().relleno().control(self.lb_tiempo_m).relleno().control(self.bt_cancelar)
        layout = Colocacion.V().control(self.lb_engine_m).otro(ly2).control(self.wrm).margen(3)

        self.setLayout(layout)

        self.wrm.setFocus()

    def activa(self, siActivar):
        color = self.dic_fonts[siActivar]
        # self.lb_engine_m.set_foreground(color)
        self.lb_tiempo_m.set_foreground(color)
        self.bt_cancelar.setVisible(not siActivar)
        self.siTiempoActivo = False

        if siActivar:
            self.lb_engine.set_text(self.time_engine)
            self.lb_time.set_text(self.time_label)

    def cancelar(self):
        self.owner.remove_analysis(self.tab_analysis)

    def cambiadoRM(self, row):
        self.tab_analysis.set_pos_rm_active(row)
        self.lbPuntuacion.set_text(self.tab_analysis.score_active_depth())
        self.ponBoard()

    def change_pos_active(self, pos):
        self.tab_analysis.set_pos_mov_active(pos)
        self.ponBoard()

    def ponBoard(self):
        position, from_sq, to_sq = self.tab_analysis.active_position()
        self.board.set_position(position)
        self.board.activate_side(position.is_white)
        if from_sq:
            self.board.put_arrow_sc(from_sq, to_sq)
        self.lbPGN.set_text(self.tab_analysis.pgn_active())
        QTUtil.refresh_gui()

    def grid_num_datos(self, grid):
        return len(self.list_rm_name)

    def grid_left_button(self, grid, row, column):
        self.cambiadoRM(row)
        self.owner.activate_analysis(self.tab_analysis)

    def grid_right_button(self, grid, row, column, modificadores):
        self.cambiadoRM(row)

    def grid_bold(self, grid, row, column):
        return self.tab_analysis.is_selected(row)

    def grid_dato(self, grid, row, o_column):
        # pgn, color, txt_analysis, indicadorInicial, li_nags
        txt = self.list_rm_name[row][1]
        if "(" in txt:
            pgn, resto = txt.split("(")
            txt_analysis = resto[:-1]
        else:
            pgn = txt
            txt_analysis = ""
        return pgn, None, txt_analysis, None, None

    def grid_color_texto(self, grid, row, o_column):
        rm = self.list_rm_name[row][0]
        return None if rm.centipawns_abs() >= 0 else self.colorNegativo

    def grid_color_fondo(self, grid, row, o_column):
        if row % 2 == 1:
            return self.colorImpares
        else:
            return None

    def situate(self, recno):
        if 0 <= recno < len(self.list_rm_name):
            self.wrm.goto(recno, 0)
            self.cambiadoRM(recno)
            self.owner.activate_analysis(self.tab_analysis)

    def abajo(self):
        self.situate(self.wrm.recno() + 1)

    def primero(self):
        self.situate(0)

    def arriba(self):
        self.situate(self.wrm.recno() - 1)

    def ultimo(self):
        self.situate(len(self.list_rm_name) - 1)

    def process_toolbar(self, accion):
        accion = accion[5:]
        if accion in ("Adelante", "Atras", "Inicio", "Final"):
            self.tab_analysis.change_mov_active(accion)
            self.ponBoard()
        elif accion == "Libre":
            self.tab_analysis.external_analysis(self.owner, self.owner.is_white)
        elif accion == "Tiempo":
            self.lanzaTiempo()
        elif accion == "Grabar":
            self.grabar()
        elif accion == "GrabarTodos":
            self.grabarTodos()
        elif accion == "Jugar":
            self.jugarPosicion()
        elif accion == "FEN":
            QTUtil.ponPortapapeles(self.tab_analysis.fen_active())
            QTVarios.fen_is_in_clipboard(self)

    def jugarPosicion(self):
        position, from_sq, to_sq = self.tab_analysis.active_position()
        game = Game.Game(first_position=position)
        dic_sended = {"ISWHITE": position.is_white, "GAME": game.save()}

        fichero = Code.configuration.ficheroTemporal("pk")
        Util.save_pickle(fichero, dic_sended)

        XRun.run_lucas("-play", fichero)

    def lanzaTiempo(self):
        self.siTiempoActivo = not self.siTiempoActivo
        if self.siTiempoActivo:
            self.tab_analysis.change_mov_active("Inicio")
            self.ponBoard()
            QtCore.QTimer.singleShot(Code.configuration.x_interval_replay, self.siguienteTiempo)

    def siguienteTiempo(self):
        if self.siTiempoActivo:
            self.tab_analysis.change_mov_active("Adelante")
            self.ponBoard()
            if self.tab_analysis.is_final_position():
                self.siTiempoActivo = False
            else:
                if Code.configuration.x_beep_replay:
                    Code.runSound.playBeep()
                QtCore.QTimer.singleShot(Code.configuration.x_interval_replay, self.siguienteTiempo)

    def grabar(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(True, _("All moves"), Iconos.PuntoVerde())
        menu.separador()
        menu.opcion(False, _("Only the first move"), Iconos.PuntoRojo())
        is_complete = menu.lanza()
        if is_complete is None:
            return
        self.tab_analysis.save_base(self.tab_analysis.game, self.tab_analysis.rm, is_complete)
        self.tab_analysis.put_view_manager()

    def grabarTodos(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(True, _("All moves in each variation"), Iconos.PuntoVerde())
        menu.separador()
        menu.opcion(False, _("Only the first move of each variation"), Iconos.PuntoRojo())
        is_complete = menu.lanza()
        if is_complete is None:
            return
        for pos, tp in enumerate(self.tab_analysis.list_rm_name):
            rm = tp[0]
            game = Game.Game(self.tab_analysis.move.position_before)
            game.read_pv(rm.pv)
            self.tab_analysis.save_base(game, rm, is_complete)
        self.tab_analysis.put_view_manager()


class WAnalisis(LCDialog.LCDialog):
    def __init__(self, tb_analysis, ventana, is_white, must_save, tab_analysis_init, subanalysis=False):
        titulo = _("Subanalysis") if subanalysis else _("Analysis")
        icono = Iconos.Analizar()

        self.subanalysis = subanalysis

        if subanalysis:
            st_subanalisis = set()
            for window in QtWidgets.QApplication.topLevelWidgets():
                if hasattr(window, "key_video"):
                    if window.key_video.startswith("subanalysis"):
                        st_subanalisis.add(int(window.key_video[11:]))
            num = 1
            for x in range(1, 100):
                if x not in st_subanalisis:
                    num = x
                    break
            extparam = "subanalysis%d" % num
        else:
            extparam = "analysis"

        LCDialog.LCDialog.__init__(self, ventana, titulo, icono, extparam)

        self.tb_analysis = tb_analysis
        self.muestraActual = None
        self.timer = None

        configuration = Code.configuration

        config_board = configuration.config_board(
            "SUBANALYSIS" if subanalysis else "ANALISIS", 32 if subanalysis else 48
        )
        self.must_save = must_save
        self.is_white = is_white

        tb_work = QTVarios.LCTB(self, icon_size=24)
        tb_work.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb_work.new(_("New"), Iconos.NuevoMas(), self.crear)

        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_side_bottom(is_white)
        self.board.set_dispatcher(self.player_has_moved)

        self.board.allow_eboard = False

        self.lb_engine = Controles.LB(self).align_center()
        self.lb_time = Controles.LB(self).align_center()
        self.lbPuntuacion = Controles.LB(self).align_center()
        self.lbPGN = Controles.LB(self)
        configuration.set_property(self.lbPGN, "pgn")
        self.lbPGN.set_wrap().set_font_type(puntos=configuration.x_pgn_fontpoints)
        self.lbPGN.setAlignment(QtCore.Qt.AlignTop)
        self.lbPGN.setOpenExternalLinks(False)
        self.lbPGN.linkActivated.connect(self.change_mov_active)

        scroll = QtWidgets.QScrollArea()
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QtWidgets.QFrame.NoFrame)

        ly = Colocacion.V().control(self.lbPGN).margen(3)
        w = QtWidgets.QWidget()
        w.setLayout(ly)
        scroll.setWidget(w)

        self.setStyleSheet("QStatusBar::item { border-style: outset; border: 1px solid LightSlateGray ;}")

        li_mas_acciones = (("FEN:%s" % _("Copy to clipboard"), "MoverFEN", Iconos.Clipboard()),)
        lytb, self.tb = QTVarios.ly_mini_buttons(
            self,
            "",
            siLibre=True,
            must_save=must_save,
            siGrabarTodos=must_save,
            siJugar=True,
            liMasAcciones=li_mas_acciones,
            icon_size=24,
        )

        ly_tabl = Colocacion.H().relleno().control(self.board).relleno()

        ly_motor = Colocacion.H().control(self.lbPuntuacion).relleno().control(self.lb_engine).control(self.lb_time)

        lyV = Colocacion.V()
        lyV.control(tb_work)
        lyV.otro(ly_tabl)
        lyV.otro(lytb).espacio(20)
        lyV.otro(ly_motor)
        lyV.control(scroll)
        lyV.relleno()

        wm = OneAnalysis(self, tab_analysis_init)
        tab_analysis_init.wmu = wm

        # Layout
        self.ly = Colocacion.H().margen(10)
        self.ly.otro(lyV)
        self.ly.control(wm)

        lyM = Colocacion.H().margen(0).otro(self.ly).relleno()

        layout = Colocacion.V()
        layout.otro(lyM)
        layout.margen(3)
        layout.setSpacing(1)
        self.setLayout(layout)

        self.restore_video(siTam=False)
        wm.cambiadoRM(tab_analysis_init.pos_selected)
        self.activate_analysis(tab_analysis_init)

    def change_mov_active(self, pos):
        pos = int(pos)
        self.muestraActual.wmu.change_pos_active(pos)

    def keyPressEvent(self, event):
        self.key_pressed(event.key())

    def key_pressed(self, k):
        if k == QtCore.Qt.Key_Down:
            self.muestraActual.wmu.abajo()
        elif k == QtCore.Qt.Key_Up:
            self.muestraActual.wmu.arriba()
        elif k == QtCore.Qt.Key_Left:
            self.muestraActual.wmu.process_toolbar("MoverAtras")
        elif k == QtCore.Qt.Key_Right:
            self.muestraActual.wmu.process_toolbar("MoverAdelante")
        elif k == QtCore.Qt.Key_Home:
            self.muestraActual.wmu.process_toolbar("MoverInicio")
        elif k == QtCore.Qt.Key_End:
            self.muestraActual.wmu.process_toolbar("MoverFinal")
        elif k == QtCore.Qt.Key_PageUp:
            self.muestraActual.wmu.primero()
        elif k == QtCore.Qt.Key_PageDown:
            self.muestraActual.wmu.ultimo()
        elif k in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.muestraActual.wmu.process_toolbar("MoverLibre")
        elif k == QtCore.Qt.Key_Escape:
            self.terminar()

    def boardWheelEvent(self, board, forward):
        forward = Code.configuration.wheel_board(forward)
        self.key_pressed(QtCore.Qt.Key.Key_Left if forward else QtCore.Qt.Key.Key_Right)

    def toolbar_rightmouse(self):
        QTVarios.change_interval(self, Code.configuration)

    def closeEvent(self, event):  # Cierre con X
        self.terminar(False)

    def terminar(self, siAccept=True):
        for window in QtWidgets.QApplication.topLevelWidgets():
            if hasattr(window, "key_video") and window.key_video.startswith("subanalysis"):
                try:
                    window.save_video()
                except:
                    pass

        for una in self.tb_analysis.li_tabs_analysis:
            una.wmu.siTiempoActivo = False
        self.save_video()
        if siAccept:
            self.accept()
        else:
            self.reject()

    def activate_analysis(self, tab_analysis):
        self.muestraActual = tab_analysis
        for una in self.tb_analysis.li_tabs_analysis:
            if hasattr(una, "wmu"):
                una.wmu.activa(una == tab_analysis)

    def create_analysis(self, tab_analysis):
        wm = OneAnalysis(self, tab_analysis)
        self.ly.control(wm)
        wm.show()

        tab_analysis.set_wmu(wm)

        self.activate_analysis(tab_analysis)

        wm.grid_left_button(wm.wrm, tab_analysis.pos_rm_active, 0)

        return wm

    def remove_analysis(self, tab_analysis):
        tab_analysis.desactiva()
        self.adjustSize()
        QTUtil.refresh_gui()

    def process_toolbar(self):
        key = self.sender().key
        if key == "terminar":
            self.terminar()
            self.accept()
        elif key == "crear":
            self.crear()
        else:
            self.muestraActual.wmu.process_toolbar(key)

    def start_clock(self, funcion):
        if self.tiomer is None:
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(funcion)
        self.timer.start(1000)

    def stop_clock(self):
        if self.timer:
            self.timer.stop()
            self.timer = None

    def crear(self):
        alm = WindowAnalysisParam.analysis_parameters(self, False, all_engines=True)
        if alm:
            tab_analysis = self.tb_analysis.create_show(self, alm)
            self.create_analysis(tab_analysis)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        game = self.muestraActual.wmu.tab_analysis.get_game()
        if not promotion and game.last_position.pawn_can_promote(from_sq, to_sq):
            promotion = self.board.peonCoronando(game.last_position.is_white)
            if promotion is None:
                return False

        ok, error, move = Move.get_game_move(game, game.last_position, from_sq, to_sq, promotion)
        if ok:
            game.add_move(move)
            xanalyzer = Code.procesador.XAnalyzer()
            si_cancelar = xanalyzer.mstime_engine > 1000 or xanalyzer.depth_engine > 8
            mens = _("Analyzing the move....")
            me = QTUtil2.waiting_message.start(
                self, mens, with_cancel=si_cancelar, tit_cancel=_("Stop thinking"), opacity=1.0
            )

            if si_cancelar:
                ya_cancelado = [False]
                tm_ini = time.time()

                def test_me(rm):
                    if ya_cancelado[0]:
                        return False
                    if me.cancelado():
                        stop = not ya_cancelado[0]
                    else:
                        tm = time.time() - tm_ini
                        me.label('%s\n%s: %d %s: %.01f"' % (mens, _("Depth"), rm.depth, _("Time"), tm))
                        stop = xanalyzer.mstime_engine and tm * 1000 > xanalyzer.mstime_engine
                    if stop:
                        xanalyzer.stop()
                        ya_cancelado[0] = True
                        return False
                    return True

                xanalyzer.set_gui_dispatch(test_me)
            mrm, pos = xanalyzer.analyzes_move_game(
                game, len(game) - 1, xanalyzer.mstime_engine, xanalyzer.depth_engine, window=self
            )
            move.analysis = mrm, pos
            me.final()
            xanalyzer.set_gui_dispatch(None)

            Analysis.show_analysis(
                Code.procesador,
                xanalyzer,
                move,
                self.board.is_white_bottom,
                len(game) - 1,
                main_window=self,
                must_save=False,
                subanalysis=True,
            )

        return False
