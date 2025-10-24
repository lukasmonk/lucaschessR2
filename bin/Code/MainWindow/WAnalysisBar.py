from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QProgressBar

import Code
from Code.Analysis import AnalysisEval
from Code.Base import Game
from Code.QT import FormLayout, Iconos, Colocacion, Controles


class AnalysisBar(QtWidgets.QWidget):

    def __init__(self, w_parent, board):
        QtWidgets.QWidget.__init__(self, w_parent)

        self.w_parent = w_parent
        self.board = board
        self.engine_manager = None
        self.timer = None
        self.activated = False
        self.value_objective = 0
        self.acercando = False
        self.aeval = AnalysisEval.AnalysisEval()
        self.interval = Code.configuration.x_analyzer_mstime_refresh_ab

        self.progressbar = QProgressBar(self)
        self.progressbar.setOrientation(QtCore.Qt.Vertical)
        self.progressbar.setRange(0, 10000)
        self.progressbar.setValue(5000)
        self.progressbar.setTextVisible(False)

        self.lb_value_up = Controles.LB(self).set_font_type(puntos=7).align_center()
        self.lb_value_down = Controles.LB(self).set_font_type(puntos=7).align_center()

        b, w = Code.dic_colors["BLACK_ANALYSIS_BAR"], Code.dic_colors["WHITE_ANALYSIS_BAR"]
        style = f"""QProgressBar{{background-color :{b};border : 1px solid {b};margin-left:4px;}}  
                   QProgressBar::chunk {{background-color: {w};}}"""
        self.setStyleSheet(style)

        self.xpv = None
        self.game = None

        self.board.set_analysis_bar(self)
        self.previous_board = None
        self.set_board_position()

        layout = Colocacion.V().control(self.lb_value_up).espacio(-6).control(self.progressbar).espacio(-6).control(self.lb_value_down).margen(0)
        self.setLayout(layout)

    def set_board_position(self):
        if Code.configuration.x_analyzer_autorotate_ab:
            new = self.board.is_white_bottom
            if self.previous_board != new:
                self.progressbar.setInvertedAppearance(not new)
                self.previous_board = new

    def activate(self, ok):
        if ok is None:
            ok = False
        self.activated = ok
        self.setVisible(ok)
        if ok:
            if self.engine_manager is None:
                self.engine_manager = Code.procesador.analyzer_clone(0, 0, 1)
                self.engine_manager.set_priority_very_low()
            if self.timer is None:
                self.timer = QtCore.QTimer()
                self.timer.timeout.connect(self.control_state)
            else:
                self.timer.stop()
            self.timer.start(self.interval)
        else:
            if self.timer:
                self.timer.stop()
                self.timer = None
            if self.engine_manager:
                self.engine_manager.terminar()
                self.engine_manager = None

    def end_think(self):
        if self.timer:
            self.timer.stop()
            if self.engine_manager:
                self.engine_manager.ac_final(0)

    def set_game(self, game):
        self.timer.stop()
        self.game = game
        self.xpv = game.xpv()

        self.timer.start(self.interval)

        self.engine_manager.ac_final(0)
        self.engine_manager.ac_inicio(game)

    def show_score(self, txt):
        self.lb_value_up.set_text(txt)
        self.lb_value_down.set_text(txt)

    def current_bestmove(self):
        rm = None
        if self.engine_manager:
            mrm = self.engine_manager.ac_estado()
            if mrm:
                rm = mrm.rm_best()
        return rm

    def control_state(self):
        if self.engine_manager:
            mrm = self.engine_manager.ac_estado()
            if mrm:

                rm = mrm.rm_best()

                cp = rm.centipawns_abs()

                tooltip = None
                if not rm.is_white:
                    cp = -cp
                ev = int(self.aeval.lv(cp) * 100)

                self.show_score(rm.abbrev_text_base1())
                self.update_value(ev)

                if tooltip is None:
                    pgn = Game.pv_pgn(self.game.last_position.fen(), rm.pv)
                    main = f"{rm.abbrev_text_base1()} (^{rm.depth})"
                    li = pgn.split(" ")
                    if len(li) > 0:
                        sli = []
                        if not rm.is_white:
                            sli.append(li[0])
                            del li[0]
                        for pos in range(0, len(li), 2):
                            txt = li[pos]
                            if pos < len(li) - 1:
                                txt += " " + li[pos + 1]
                            sli.append(txt)
                        pgn = "\n".join(sli)
                    tooltip = main + "\n" + pgn
                    self.setToolTip(tooltip)

            else:
                self.setToolTip("")
                self.show_score("")
                self.engine_manager.ac_final(0)
                self.timer.stop()

    def configure(self):
        configuration = Code.configuration
        form = FormLayout.FormLayout(self, _("Configuration"), Iconos.Configurar())
        form.separador()
        form.checkbox(_("Auto-rotate"), configuration.x_analyzer_autorotate_ab)
        form.separador()
        form.separador()
        form.apart_np(_("Limits in the Analysis Bar (0=no limit)"))
        form.editbox(_("Depth"), ancho=50, tipo=int, decimales=0, init_value=configuration.x_analyzer_depth_ab)
        form.seconds(_("Time in seconds"), configuration.x_analyzer_mstime_ab / 1000.0)
        form.separador()

        resultado = form.run()
        if resultado is None:
            return

        (configuration.x_analyzer_autorotate_ab, configuration.x_analyzer_depth_ab,
         configuration.x_analyzer_mstime_ab) = resultado[1]
        configuration.x_analyzer_mstime_ab *= 1000
        configuration.graba()

        self.set_game(self.game)
        self.set_board_position()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.configure()
        super().mousePressEvent(event)

    def update_value(self, value):
        if not self.activated:
            return
        if value > 10000:
            value = 10000
        elif value < 0:
            value = 0
        self.value_objective = value
        if not self.acercando:
            self.goto_objective()

    def goto_objective(self):
        if not self.engine_manager or not self.activated:
            self.acercando = False
            return
        value = self.progressbar.value()
        if value != self.value_objective:
            velocidad = max(abs(self.value_objective - value) // 50, 1)
            self.acercando = True
            add = +1 if self.value_objective > value else -1
            self.progressbar.setValue(value + add * velocidad)
            self.update()
            QtCore.QTimer.singleShot(2, self.goto_objective)
        else:
            self.acercando = False
