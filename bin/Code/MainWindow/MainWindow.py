import gettext
_ = gettext.gettext
from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.MainWindow import WInformation, WBase
from Code.QT import Colocacion
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.Translations import WorkTranslate
from Code.Board import Eboard


class MainWindow(LCDialog.LCDialog):
    signal_notify = QtCore.Signal()
    signal_routine_connected = None
    dato_notify = None

    def __init__(self, manager, owner=None, extparam=None):
        self.manager = manager

        titulo = ""
        icono = Iconos.Aplicacion64()
        extparam = extparam if extparam else "maind"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        self.base = WBase.WBase(self, manager)

        self.siCapturas = False
        self.informacionPGN = WInformation.Information(self)
        self.siInformacionPGN = False
        self.informacionPGN.hide()
        self.register_splitter(self.informacionPGN.splitter, "InformacionPGN")

        self.timer = None
        self.siTrabajando = False

        self.cursorthinking = QtGui.QCursor(
            Iconos.pmThinking() if self.manager.configuration.x_cursor_thinking else QtCore.Qt.BlankCursor
        )
        self.cursorthinking_rival = QtGui.QCursor(Iconos.pmConnected())
        self.onTop = False

        self.board = self.base.board
        self.board.dispatchSize(self.ajustaTam)
        self.board.permitidoResizeExterno(True)
        self.anchoAntesMaxim = None

        self.splitter = splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(self.base)
        splitter.addWidget(self.informacionPGN)

        ly = Colocacion.H().control(splitter).margen(0)

        self.setLayout(ly)

        ctrl1 = QtWidgets.QShortcut(self)
        ctrl1.setKey(QtGui.QKeySequence("Ctrl+1"))
        ctrl1.activated.connect(self.pressed_shortcut_Ctrl1)

        ctrlF10 = QtWidgets.QShortcut(self)
        ctrlF10.setKey(QtGui.QKeySequence("Ctrl+0"))
        ctrlF10.activated.connect(self.pressed_shortcut_Ctrl0)

        F11 = QtWidgets.QShortcut(self)
        F11.setKey(QtGui.QKeySequence("F11"))
        F11.activated.connect(self.pressed_shortcut_F11)
        self.activadoF11 = False
        self.previous_f11_maximized = False

        if QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            F12 = QtWidgets.QShortcut(self)
            F12.setKey(QtGui.QKeySequence("F12"))
            F12.activated.connect(self.pressed_shortcut_F12)
            self.trayIcon = None

        self.resizing = None

        self.cursor_pensando = False

        self.work_translate = None

    def set_notify(self, routine):
        if self.signal_routine_connected:
            self.signal_notify.disconnect(self.signal_routine_connected)
        self.signal_notify.connect(routine)
        self.signal_routine_connected = routine

    def notify(self, dato):
        self.dato_notify = dato
        self.signal_notify.emit()

    def closeEvent(self, event):  # Cierre con X
        self.final_processes()
        if not self.manager.finalX0():
            event.ignore()

    def onTopWindow(self):
        self.onTop = not self.onTop
        self.muestra()

    def activateTrayIcon(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.restauraTrayIcon()

    def restauraTrayIcon(self):
        self.showNormal()
        self.trayIcon.hide()

    def quitTrayIcon(self):
        self.trayIcon.hide()
        self.final_processes()
        self.accept()

    def pressed_shortcut_F12(self):
        if not self.trayIcon:
            restoreAction = QtWidgets.QAction(Iconos.PGN(), _("Show"), self, triggered=self.restauraTrayIcon)
            quitAction = QtWidgets.QAction(Iconos.Terminar(), _("Quit"), self, triggered=self.quitTrayIcon)
            trayIconMenu = QtWidgets.QMenu(self)
            trayIconMenu.addAction(restoreAction)
            trayIconMenu.addSeparator()
            trayIconMenu.addAction(quitAction)

            self.trayIcon = QtWidgets.QSystemTrayIcon(self)
            self.trayIcon.setContextMenu(trayIconMenu)
            self.trayIcon.setIcon(Iconos.Aplicacion64())
            self.trayIcon.activated.connect(self.activateTrayIcon)
            self.trayIcon.hide()

        if self.trayIcon:
            self.trayIcon.show()
            self.hide()

    def pressed_shortcut_F11(self):
        self.activadoF11 = not self.activadoF11
        if self.activadoF11:
            if self.siInformacionPGN:
                self.informacionPGN.save_width()
            self.showFullScreen()
        else:
            self.showNormal()
            if self.siInformacionPGN:
                self.informacionPGN.restore_width()

    def final_processes(self):
        self.board.close_visual_script()
        self.board.terminar()

        if self.work_translate:
            self.work_translate.close()

    def set_manager_active(self, manager):
        self.manager = manager
        self.base.set_manager_active(manager)

    def muestra(self):
        flags = QtCore.Qt.Dialog if self.owner else QtCore.Qt.Widget
        flags |= QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint
        if self.onTop:
            flags |= QtCore.Qt.WindowStaysOnTopHint

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | flags)
        if self.board.siMaximizado():
            self.showMaximized()
        else:
            self.xrestore_video()
            self.ajustaTam()
            self.show()

        self.set_title()

    def save_width_piece(self):
        ct = self.board.config_board
        if ct.anchoPieza() != 1000:
            dic = Code.configuration.read_variables("WIDTH_PIEZES")
            dic["WIDTH_PIEZE_MAIN"] = ct.anchoPieza()
            Code.configuration.write_variables("WIDTH_PIEZES", dic)

    def restore_width_pieze(self):
        dic = Code.configuration.read_variables("WIDTH_PIEZES")
        return dic.get("WIDTH_PIEZE_MAIN")

    def changeEvent(self, event):
        QtWidgets.QWidget.changeEvent(self, event)
        if event.type() != QtCore.QEvent.WindowStateChange:
            return

        nue = QTUtil.EstadoWindow(self.windowState())
        ant = QTUtil.EstadoWindow(event.oldState())

        if getattr(self.manager, "siPresentacion", False):
            self.manager.presentacion(False)

        if nue.fullscreen:
            self.previous_f11_maximized = ant.maximizado
            self.base.tb.hide()
            self.board.siF11 = True
            self.save_width_piece()
            self.board.maximizaTam(True)
        else:
            if ant.fullscreen:
                self.base.tb.show()
                self.board.normalTam(self.restore_width_pieze())
                self.ajustaTam()
                if self.previous_f11_maximized:
                    self.setWindowState(QtCore.Qt.WindowMaximized)
            elif nue.maximizado:
                self.save_width_piece()
                self.board.maximizaTam(False)
            elif ant.maximizado:
                self.board.normalTam(self.restore_width_pieze())
                self.ajustaTam()

    def show_variations(self, titulo):
        flags = (
            QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
        )

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | flags)

        self.setWindowTitle(titulo if titulo else "-")

        # self.restore_main_window()
        self.ajustaTam()

        resp = self.exec_()
        self.save_video()
        return resp

    def ajustaTam(self):
        if self.isMaximized():
            if not self.board.siMaximizado():
                self.board.maximizaTam(self.activadoF11)
        else:
            n = 0
            while self.height() > self.board.ancho + self.base.tb.height() + 18:
                self.adjustSize()
                self.refresh()
                n += 1
                if n > 3:
                    break
        self.refresh()

    def ajustaTamH(self):
        if not (self.isMaximized() or self.board.siF11):
            for n in range(3):
                self.adjustSize()
                self.refresh()
        self.refresh()

    def set_title(self):
        self.setWindowTitle(Code.lucas_chess)

    def set_label1(self, label):
        return self.base.set_label1(label)

    def set_label2(self, label):
        return self.base.set_label2(label)

    def set_label3(self, label):
        return self.base.set_label3(label)

    def set_hight_label3(self, px):
        return self.base.set_hight_label3(px)

    def get_labels(self):
        return self.base.get_labels()

    def ponWhiteBlack(self, white=None, black=None):
        self.base.ponWhiteBlack(white, black)

    def set_activate_tutor(self, siActivar):
        self.base.set_activate_tutor(siActivar)

    def pon_toolbar(self, li_acciones, separator=True, atajos=False, with_eboard=False):
        return self.base.pon_toolbar(li_acciones, separator, atajos, with_eboard=with_eboard)

    def get_toolbar(self):
        return self.base.get_toolbar()

    def ponAyudas(self, puntos, with_takeback=True):
        self.base.ponAyudas(puntos, with_takeback)

    def remove_hints(self, siTambienTutorAtras, with_takeback=True):
        self.base.remove_hints(siTambienTutorAtras, with_takeback)

    def enable_option_toolbar(self, opcion, siHabilitar):
        self.base.enable_option_toolbar(opcion, siHabilitar)

    def show_option_toolbar(self, opcion, must_show):
        self.base.show_option_toolbar(opcion, must_show)

    def is_enabled_option_toolbar(self, opcion):
        return self.base.is_enabled_option_toolbar(opcion)

    def set_title_toolbar_eboard(self):
        self.base.set_title_toolbar_eboard()

    def pgnRefresh(self, is_white):
        self.base.pgnRefresh()
        self.base.pgn.gobottom(2 if is_white else 1)

    def pgnColocate(self, fil, is_white):
        col = 1 if is_white else 2
        self.base.pgn.goto(fil, col)

    def pgnPosActual(self):
        return self.base.pgn.current_position()

    def hide_pgn(self):
        self.base.pgn.hide()
        # self.base.pgn.setDisabled(True)

    def show_pgn(self):
        self.base.pgn.show()
        # self.base.pgn.setDisabled(False)

    def refresh(self):
        self.update()
        QTUtil.refresh_gui()

    def activaCapturas(self, siActivar=None):
        if siActivar is None:
            self.siCapturas = not self.siCapturas
            Code.configuration.x_captures_activate = self.siCapturas
            Code.configuration.graba()
        else:
            self.siCapturas = siActivar
        self.base.lb_capt_white.setVisible(self.siCapturas)
        self.base.lb_capt_black.setVisible(self.siCapturas)

    def activaInformacionPGN(self, siActivar=None):
        if siActivar is None:
            self.siInformacionPGN = not self.siInformacionPGN
            Code.configuration.x_info_activate = self.siInformacionPGN
            Code.configuration.graba()
        else:
            self.siInformacionPGN = siActivar

        self.informacionPGN.activa(self.siInformacionPGN)
        sizes = self.informacionPGN.splitter.sizes()
        for n, size in enumerate(sizes):
            if size == 0:
                sizes[n] = 100
                self.informacionPGN.splitter.setSizes(sizes)
                break
        if not self.siInformacionPGN:
            self.ajustaTamH()

    def ponCapturas(self, dic):
        self.base.put_captures(dic)

    def put_informationPGN(self, game, move, opening):
        self.informacionPGN.set_move(game, move, opening)

    def activaJuego(self, siActivar=True, siReloj=False, siAyudas=None):
        self.base.activaJuego(siActivar, siReloj, siAyudas)
        if not self.board.siF11:
            self.ajustaTamH()

    def set_data_clock(self, bl, rb, ng, rn):
        self.base.set_data_clock(bl, rb, ng, rn)

    def set_clock_white(self, tm, tm2):
        self.base.set_clock_white(tm, tm2)

    def set_clock_black(self, tm, tm2):
        self.base.set_clock_black(tm, tm2)

    def change_player_labels(self, bl, ng):
        self.base.change_player_labels(bl, ng)

    def start_clock(self, enlace, transicion=100):
        if self.timer is not None:
            self.timer.stop()
            del self.timer

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(enlace)
        self.timer.start(transicion)

    def stop_clock(self):
        if self.timer is not None:
            self.timer.stop()
            del self.timer
            self.timer = None

    def columnas60(self, siPoner, cNivel=None, cWhite=None, cBlack=None):
        self.base.columnas60(siPoner, cNivel, cWhite, cBlack)

    def pressed_shortcut_Ctrl1(self):
        if self.manager and hasattr(self.manager, "control1"):
            self.manager.control1()

    def pressed_shortcut_Ctrl0(self):
        if self.manager and hasattr(self.manager, "control0"):
            self.manager.control0()

    def soloEdicionPGN(self, file):
        if file:
            titulo = file
        else:
            titulo = "<<< %s >>>" % _("Temporary file")

        self.setWindowTitle(titulo)
        self.setWindowIcon(Iconos.PGN())

    def cursorFueraBoard(self):
        p = self.mapToParent(self.board.pos())
        p.setX(p.x() + self.board.ancho + 4)

        QtGui.QCursor.setPos(p)

    def thinking(self, si_pensando):
        if si_pensando:
            if not self.cursor_pensando:
                QtWidgets.QApplication.setOverrideCursor(self.cursorthinking_rival)
        else:
            if self.cursor_pensando:
                QtWidgets.QApplication.restoreOverrideCursor()
        self.cursor_pensando = si_pensando
        self.refresh()

    def pensando_tutor(self, si_pensando):
        if si_pensando:
            if not self.cursor_pensando:
                QtWidgets.QApplication.setOverrideCursor(self.cursorthinking)
        else:
            if self.cursor_pensando:
                QtWidgets.QApplication.restoreOverrideCursor()
        self.cursor_pensando = si_pensando
        self.refresh()

    def save_video(self, dic_extended=None):
        dic = {} if dic_extended is None else dic_extended

        pos = self.pos()
        dic["_POSICION_"] = "%d,%d" % (pos.x(), pos.y())

        tam = self.size()
        dic["_SIZE_"] = "%d,%d" % (tam.width(), tam.height())

        for grid in self.liGrids:
            grid.save_video(dic)

        for sp, name in self.liSplitters:
            sps = sp.sizes()
            key = "SP_%s" % name
            if name == "InformacionPGN" and sps[1] == 0:
                sps = self.informacionPGN.sp_sizes
                if sps is None or sps[1] == 0:
                    dr = self.restore_dicvideo()
                    if key in dr:
                        dic[key] = dr
                        continue
                    sps = [1, 1]
            dic["SP_%s" % name] = sps

        dic["WINFO_WIDTH"] = self.informacionPGN.width_saved
        dic["WINFOPARENT_WIDTH"] = self.informacionPGN.parent_width_saved

        Code.configuration.save_video(self.key_video, dic)
        return dic

    def xrestore_video(self):
        if self.restore_video():
            dic = self.restore_dicvideo()
            self.informacionPGN.width_saved = dic.get("WINFO_WIDTH")
            self.informacionPGN.parent_width_saved = dic.get("WINFOPARENT_WIDTH")

    def check_translated_help_mode(self):
        if not Code.configuration.x_translation_mode:
            return

        self.work_translate = WorkTranslate.launch_wtranslation()

        QtCore.QTimer.singleShot(3000, self.check_translated_received)

    def check_translated_received(self):
        salto = 500 if self.work_translate.pending_commit else 1000

        if self.work_translate.check_commits():
            QtCore.QTimer.singleShot(salto, self.check_translated_received)

    def deactivate_eboard(self, ms=500):
        if Code.eboard and Code.eboard.driver:
            QTUtil.refresh_gui()

            def deactive():
                Code.eboard.deactivate()
                self.set_title_toolbar_eboard()
                del Code.eboard
                Code.eboard = Eboard.Eboard()

            if ms > 0:
                QtCore.QTimer.singleShot(ms, deactive)
            else:
                deactive()

    def delay_routine(self, ms, routine):
        QtCore.QTimer.singleShot(ms, routine)
