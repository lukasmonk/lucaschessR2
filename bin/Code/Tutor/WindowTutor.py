from PySide2 import QtCore

import Code
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
    def __init__(self, manager, tutor, siRival, siOpenings, is_white, has_hints):
        titulo = _("Tutor")
        icono = Iconos.Tutor()
        extparam = "tutor"
        LCDialog.LCDialog.__init__(self, manager.main_window, titulo, icono, extparam)

        self.tutor = tutor
        self.manager = manager
        self.respLibro = None
        self.siElegidaOpening = False

        self.x_tutor_view = manager.configuration.x_tutor_view

        f = Controles.TipoLetra(puntos=12, peso=75)
        flba = Controles.TipoLetra(puntos=8)

        ae = QTUtil.anchoEscritorio()
        mx = 32 if ae > 1000 else 20
        config_board = Code.configuration.config_board("TUTOR", mx)

        # Boards

        def create_board(name, si=True, siLibre=True, siMas=False):
            if not si:
                return None, None, None
            board = Board.Board(self, config_board)
            board.crea()
            board.set_side_bottom(is_white)
            lytb, tb = QTVarios.ly_mini_buttons(self, name, siLibre, siMas=siMas)
            return board, lytb, tb

        self.boardTutor, lytbtutor, self.tbtutor = create_board("tutor")
        self.boardUsuario, lytbuser, self.tbuser = create_board("user")
        self.boardRival, lytbRival, self.tbRival = create_board("rival", siRival)
        self.boardOpening, lytbOpening, self.tbOpening = create_board("opening", siOpenings, siLibre=False)
        tutor.ponBoardsGUI(self.boardTutor, self.boardUsuario, self.boardRival, self.boardOpening)

        # Puntuaciones
        self.lb_tutor = Controles.LB(self).ponFuente(f).align_center()
        self.lb_tutor.setFixedWidth(self.boardTutor.ancho)
        manager.configuration.set_property(self.lb_tutor, "tutor-tutor" if has_hints else "tutor-tutor-disabled")
        if has_hints:
            self.lb_tutor.mousePressEvent = self.elegirTutor

        self.lb_player = Controles.LB(self).ponFuente(f).align_center()
        self.lb_player.setFixedWidth(self.boardUsuario.ancho)
        self.lb_player.mousePressEvent = self.elegirUsuario
        manager.configuration.set_property(self.lb_player, "tutor-player" if has_hints else "tutor-tutor")

        if siRival:
            self.lb_rival = Controles.LB(self).ponFuente(f).align_center()
            self.lb_rival.setFixedWidth(self.boardRival.ancho)
            manager.configuration.set_property(self.lb_rival, "tutor-tutor-disabled")

        # Openings
        if siOpenings:
            li_options = self.tutor.opcionesOpenings()
            self.cbOpenings = Controles.CB(self, li_options, 0)
            self.cbOpenings.setFont(flba)
            self.cbOpenings.set_multiline(self.boardOpening.width())
            self.cbOpenings.capture_changes(self.tutor.cambiarOpening)

            lb_openings = Controles.LB(self, _("Opening")).ponFuente(f).align_center()
            lb_openings.setFixedWidth(self.boardOpening.ancho)
            manager.configuration.set_property(lb_openings, "tutor-tutor" if has_hints else "tutor-tutor-disabled")
            if has_hints:
                lb_openings.mousePressEvent = self.elegirOpening
            ly_openings = Colocacion.V().control(lb_openings).control(self.cbOpenings)
            self.tutor.cambiarOpening(0)

        # RM
        li_rm = []
        for n, uno in enumerate(tutor.list_rm):
            li_rm.append((uno[1], n))

        self.cbRM, self.lbRM = QTUtil2.combobox_lb(self, li_rm, li_rm[0][1], _("Moves analyzed"))
        self.cbRM.capture_changes(tutor.cambiadoRM)
        ly_rm = Colocacion.H().control(self.lbRM).control(self.cbRM)

        btLibros = Controles.PB(self," %s " %  _("Consult a book"), self.consultaLibro).ponPlano(False)

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
        layout.controlc(self.lb_tutor, 0, 0).controlc(self.boardTutor, 1, 0).otro(lytbtutor, 2, 0).otroc(ly_rm, 3, 0)
        layout.controlc(self.lb_player, fu, cu).controlc(self.boardUsuario, fu + 1, cu).otro(lytbuser, fu + 2, cu).controlc(
            btLibros, fu + 3, cu
        )
        if siRival:
            layout.controlc(self.lb_rival, fr, cr).controlc(self.boardRival, fr + 1, cr).otro(lytbRival, fr + 2, cr)
        elif siOpenings:
            layout.otroc(ly_openings, fr, cr).controlc(self.boardOpening, fr + 1, cr).otro(lytbOpening, fr + 2, cr)

        layout.margen(8)

        self.setLayout(layout)

        self.restore_video(siTam=False)

    def toolbar_rightmouse(self):
        self.stop_clock()
        QTVarios.change_interval(self, Code.configuration)

    def process_toolbar(self):
        self.exeTB(self.sender().key)

    def exeTB(self, accion):
        x = accion.index("Mover")
        quien = accion[:x]
        que = accion[x + 5:]
        self.tutor.mueve(quien, que)

    # def cambioBoard(self):
    #     self.boardUsuario.crea()
    #     if self.boardRival:
    #         self.boardRival.crea()
    #     if self.boardOpening:
    #         self.boardOpening.crea()

    def boardWheelEvent(self, board, forward):
        for t in ["Tutor", "Usuario", "Rival", "Opening"]:
            if eval("self.board%s == board" % t):
                self.exeTB(t.lower() + "Mover" + ("Adelante" if forward else "Atras"))
                return

    def consultaLibro(self):
        liMovs = self.manager.librosConsulta(True)
        if liMovs:
            self.respLibro = liMovs[-1]
            self.save_video()
            self.accept()

    def elegirTutor(self, ev):
        self.save_video()
        self.accept()

    def elegirOpening(self, ev):
        self.siElegidaOpening = True
        self.save_video()
        self.accept()

    def elegirUsuario(self, ev):
        self.save_video()
        self.reject()

    def ponPuntuacionUsuario(self, txt):
        self.lb_player.setText(txt)

    def ponPuntuacionTutor(self, txt):
        self.lb_tutor.setText(txt)

    def ponPuntuacionRival(self, txt):
        self.lb_rival.setText(txt)

    def start_clock(self, funcion):
        if not hasattr(self, "timer"):
            self.timer = QtCore.QTimer(self)
            self.connect(self.timer, QtCore.SIGNAL("timeout()"), funcion)
        self.timer.start(Code.configuration.x_interval_replay)

    def stop_clock(self):
        if hasattr(self, "timer"):
            self.timer.stop()
            delattr(self, "timer")
