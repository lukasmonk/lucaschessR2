from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QPropertyAnimation
from PySide2.QtWidgets import QProgressBar

import Code
from Code.Analysis import AnalysisEval
from Code.Base import Game
from Code.QT import FormLayout, Iconos


class AnalysisBar(QProgressBar):
    animation: QPropertyAnimation

    def __init__(self, w_parent, board):
        QtWidgets.QProgressBar.__init__(self, w_parent)

        self.w_parent = w_parent
        self.board = board
        self.engine_manager = None
        self.setOrientation(QtCore.Qt.Vertical)
        self.aeval = AnalysisEval.AnalysisEval()
        self.max_range = 10000
        self.setRange(0, 10000)
        self.setValue(5000)
        self.setTextVisible(False)
        b, w = Code.dic_colors["BLACK_ANALYSIS_BAR"], Code.dic_colors["WHITE_ANALYSIS_BAR"]
        # style = """QProgressBar{background-color :%s;border : 1px solid %s; border-radius: 5px;}
        #            QProgressBar::chunk {background-color: %s; border-bottom-right-radius: 5px;
        # border-bottom-left-radius: 5px;}""" % (b, b, w)
        style = """QProgressBar{background-color :%s;border : 1px solid %s;}  
                   QProgressBar::chunk {background-color: %s;}""" % (b, b, w)
        self.setStyleSheet(style)
        self.timer = None
        self.interval = Code.configuration.x_analyzer_mstime_refresh_ab

        self.cache = {}
        self.xpv = None
        self.game = None

        self.animation = QPropertyAnimation(targetObject=self, propertyName=b"value")

        # self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)

    def activate(self, ok):
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
            if self.engine_manager:
                self.engine_manager.terminar()
            if self.timer:
                self.timer.stop()
                self.timer = None

    def set_game(self, game):
        self.timer.stop()
        self.game = game
        self.xpv = game.xpv()
        if self.xpv in self.cache:
            ev_cache, rm_cache, tooltip_cache = self.cache[self.xpv]
            close = False
            if 0 < Code.configuration.x_analyzer_depth_ab <= rm_cache.depth:
                close = True
            if 0 < Code.configuration.x_analyzer_mstime_ab <= rm_cache.time:
                close = True
            if close:
                # Si ya está calculado y está fuera de límites se actualiza pero no se lanza el motor
                self.update_value(ev_cache)
                self.setToolTip(tooltip_cache)
                return

        self.timer.start(self.interval)

        self.engine_manager.ac_final(0)
        self.engine_manager.ac_inicio(game)

    def control_state(self):
        if self.engine_manager:
            mrm = self.engine_manager.ac_estado()
            if mrm:
                rm = mrm.rmBest()
                depth = rm.depth
                cp = rm.centipawns_abs()
                tooltip = None
                if not rm.is_white:
                    cp = -cp
                cp = max(cp, -self.max_range)
                cp = min(cp, self.max_range)
                ev = int(self.aeval.lv(cp) * 100)
                if self.xpv in self.cache:
                    ev_cache, rm_cache, tooltip_cache = self.cache[self.xpv]
                    if rm_cache.depth > depth:
                        ev = ev_cache
                        rm = rm_cache
                        tooltip = tooltip_cache
                self.update_value(ev)

                if tooltip is None:
                    pgn = Game.pv_pgn(self.game.last_position.fen(), rm.pv)
                    k = cp / 100.0
                    main = f"{k:+.02f} (^{rm.depth})"
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

                self.cache[self.xpv] = ev, rm, tooltip

                close = False
                if 0 < Code.configuration.x_analyzer_depth_ab <= rm.depth:
                    close = True
                if 0 < Code.configuration.x_analyzer_mstime_ab <= rm.time:
                    close = True
                if close:
                    self.engine_manager.ac_final(0)
                    self.timer.stop()

    def configure(self):
        form = FormLayout.FormLayout(self, _("Limits in the Analysis Bar (0=no limit)"), Iconos.Configurar())
        form.separador()
        form.editbox(_("Depth"), ancho=50, tipo=int, decimales=0, init_value=Code.configuration.x_analyzer_depth_ab)
        form.separador()

        form.separador()
        form.float(_("Time in seconds"), Code.configuration.x_analyzer_mstime_ab / 1000.0)
        form.separador()

        resultado = form.run()
        if resultado is None:
            return

        Code.configuration.x_analyzer_depth_ab, Code.configuration.x_analyzer_mstime_ab = resultado[1]
        Code.configuration.graba()

        self.set_game(self.game)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.configure()
        super().mousePressEvent(event)

    # def update_value(self, value):
    #     desde = self.value()
    #     hasta = value
    #     inc = +1 if hasta > desde else -1
    #     while desde != hasta:
    #         desde += inc
    #         self.setValue(desde)
    #         self.update()
    #     self.setValue(hasta)
    #     self.update()

    def update_value(self, value):
        self.animation.stop()
        desde = self.value()
        hasta = value
        tm = abs(desde - hasta) * 1000 // 10000
        if tm == 0:
            return
        self.animation.setDuration(tm)
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()
