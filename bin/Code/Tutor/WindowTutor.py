from PySide2 import QtCore, QtWidgets

import Code
from Code.Analysis import Analysis
from Code.Base.Constantes import (
    POS_TUTOR_HORIZONTAL,
    POS_TUTOR_HORIZONTAL_1_2,
    POS_TUTOR_HORIZONTAL_2_1,
    POS_TUTOR_VERTICAL,
)
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WindowTutor(LCDialog.LCDialog):
    def __init__(self, manager, tutor, with_rival, with_openings, is_white, has_hints):
        titulo = _("Tutor")
        icono = Iconos.Tutor()
        extparam = "tutor"
        LCDialog.LCDialog.__init__(self, manager.main_window, titulo, icono, extparam)

        self.tutor = tutor
        self.manager = manager
        self.respLibro = None
        self.siElegidaOpening = False
        self.timer = None

        self.x_tutor_view = manager.configuration.x_tutor_view

        f = Controles.FontType(puntos=12, peso=75)
        flba = Controles.FontType(puntos=8)

        ae = QTUtil.desktop_width()
        mx = 32 if ae > 1000 else 20
        config_board = Code.configuration.config_board("TUTOR", mx)

        # Boards

        def create_board(name, si=True, si_libre=False, si_mas=False):
            if not si:
                return None, None, None
            board = Board.Board(self, config_board)
            board.crea()
            board.set_side_bottom(is_white)
            board.disable_eboard_here()
            lytb, tb = QTVarios.ly_mini_buttons(self, name, si_libre, siMas=si_mas)
            return board, lytb, tb

        self.board_tutor, lytbtutor, self.tbtutor = create_board("tutor")
        self.board_user, lytbuser, self.tbuser = create_board("user")
        self.board_rival, lytbRival, self.tbrival = create_board("rival", with_rival)
        self.boardOpening, lytbOpening, self.tbOpening = create_board("opening", with_openings, si_libre=False)
        tutor.ponBoardsGUI(self.board_tutor, self.board_user, self.board_rival, self.boardOpening)

        tb_analisis = Controles.TBrutina(self, icon_size=16, with_text=False)
        tb_analisis.new("", Iconos.Analisis(), self.launch_analysis, tool_tip=_("Analysis"))
        lytbtutor = Colocacion.H().relleno().otro(lytbtutor).relleno().control(tb_analisis)

        # Puntuaciones
        self.lb_tutor = Controles.LB(self).set_font(f).align_center().set_wrap()
        self.lb_tutor.setFixedWidth(self.board_tutor.ancho)
        manager.configuration.set_property(self.lb_tutor, "tutor-tutor" if has_hints else "tutor-tutor-disabled")
        if has_hints:
            self.lb_tutor.mousePressEvent = self.select_tutor

        self.lb_player = Controles.LB(self).set_font(f).align_center().set_wrap()
        self.lb_player.setFixedWidth(self.board_user.ancho)
        self.lb_player.mousePressEvent = self.select_user
        manager.configuration.set_property(self.lb_player, "tutor-player" if has_hints else "tutor-tutor")

        if with_rival:
            self.lb_rival = Controles.LB(self).set_font(f).align_center().set_wrap()
            self.lb_rival.setFixedWidth(self.board_rival.ancho)
            manager.configuration.set_property(self.lb_rival, "tutor-tutor-disabled")

        # Openings
        ly_openings = None
        if with_openings:
            self.tutor.set_toolbaropening_gui(self.tbOpening)
            li_options = self.tutor.opcionesOpenings()
            self.cbOpenings = Controles.CB(self, li_options, 0)
            self.cbOpenings.setFont(flba)
            self.cbOpenings.set_multiline(self.boardOpening.width())
            self.cbOpenings.capture_changes(self.tutor.cambiarOpening)

            lb_openings = Controles.LB(self, _("Opening")).set_font(f).align_center()
            lb_openings.setFixedWidth(self.boardOpening.ancho)
            lb_openings.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            manager.configuration.set_property(lb_openings, "tutor-tutor" if has_hints else "tutor-tutor-disabled")
            if has_hints:
                lb_openings.mousePressEvent = self.select_opening
            ly_openings = Colocacion.V().control(lb_openings).control(self.cbOpenings)
            self.tutor.cambiarOpening(0)

        # RM
        li_rm = []
        for n, uno in enumerate(tutor.list_rm):
            li_rm.append((uno[1], n))

        self.cbRM, self.lbRM = QTUtil2.combobox_lb(self, li_rm, li_rm[0][1], _("Moves analyzed"))
        self.cbRM.capture_changes(tutor.changed_rm)

        ly_rm = Colocacion.H().control(self.lbRM).control(self.cbRM).relleno(1)

        bt_libros = Controles.PB(self, " %s " % _("Consult a book"), self.consult_book).ponPlano(False)

        dic_vista = {
            POS_TUTOR_HORIZONTAL: ((0, 1), (0, 2)),
            POS_TUTOR_HORIZONTAL_2_1: ((0, 1), (4, 0)),
            POS_TUTOR_HORIZONTAL_1_2: ((4, 0), (4, 1)),
            POS_TUTOR_VERTICAL: ((4, 0), (8, 0)),
        }

        usu, riv = dic_vista[self.x_tutor_view]

        fu, cu = usu
        fr, cr = riv

        layout = Colocacion.G()
        layout.controlc(self.lb_tutor, 0, 0).controlc(self.board_tutor, 1, 0).otro(lytbtutor, 2, 0).otroc(ly_rm, 3, 0)
        layout.controlc(self.lb_player, fu, cu).controlc(self.board_user, fu + 1, cu).otro(lytbuser, fu + 2,
                                                                                             cu).controlc(
            bt_libros, fu + 3, cu
        )
        if with_rival:
            layout.controlc(self.lb_rival, fr, cr).controlc(self.board_rival, fr + 1, cr).otro(lytbRival, fr + 2, cr)
        elif with_openings:
            layout.otroc(ly_openings, fr, cr).controlc(self.boardOpening, fr + 1, cr).otro(lytbOpening, fr + 2, cr)

        layout.margen(8)

        self.setLayout(layout)

        self.restore_video(with_tam=False)

    def launch_analysis(self):
        game_base = self.tutor.game.copia()
        move = self.tutor.move
        game_base.add_move(move)
        rm_user, pos_user = self.tutor.mrm_tutor.search_rm(move.movimiento())
        move.analysis = self.tutor.mrm_tutor, pos_user
        move_tmp = game_base.move(-1)

        Analysis.show_analysis(Code.procesador, self.manager.xanalyzer, move_tmp, self.manager.board.is_white_bottom,
                               pos_user, main_window=self, must_save=False)

    def process_toolbar(self):
        self.run_toolbar(self.sender().key)

    def run_toolbar(self, accion):
        x = accion.index("Mover")
        quien = accion[:x]
        que = accion[x + 5:]
        self.tutor.mueve(quien, que)

    def board_wheel_event(self, board, forward):
        forward = Code.configuration.wheel_board(forward)
        for t in ["Tutor", "Usuario", "Rival", "Opening"]:
            if eval("self.board%s == board" % t):
                self.run_toolbar(t.lower() + "Mover" + ("Adelante" if forward else "Atras"))
                return

    def consult_book(self):
        li_movs = self.manager.librosConsulta(True)
        if li_movs:
            self.respLibro = li_movs[-1]
            self.save_video()
            self.accept()

    def select_tutor(self, ev):
        self.save_video()
        self.accept()

    def select_opening(self, ev):
        self.siElegidaOpening = True
        self.save_video()
        self.accept()

    def select_user(self, ev):
        self.save_video()
        self.reject()

    def set_score_user(self, txt):
        self.lb_player.setText(txt)

    def set_score_tutor(self, txt):
        self.lb_tutor.setText(txt)

    def set_score_rival(self, txt):
        self.lb_rival.setText(txt)

    def start_clock(self, funcion):
        if self.timer is None:
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(funcion)
        self.timer.start(Code.configuration.x_interval_replay)

    def stop_clock(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
            self.tutor.is_moving_time = False
            self.tutor.time_others_tb(True)
