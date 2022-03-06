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
    def __init__(self, manager, tutor, siRival, siOpenings, is_white, siPuntos):
        titulo = _("Analyzing the move....")
        icono = Iconos.Tutor()
        extparam = "tutor"
        LCDialog.LCDialog.__init__(self, manager.main_window, titulo, icono, extparam)

        self.tutor = tutor
        self.manager = manager
        self.respLibro = None
        self.siElegidaOpening = False

        self.x_tutor_view = manager.configuration.x_tutor_view

        # ~ self.setStyleSheet("QDialog,QGroupBox { background: #f0f0f0; }")

        f = Controles.TipoLetra(puntos=12, peso=75)
        flb = Controles.TipoLetra(puntos=10)
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
            lytb, tb = QTVarios.lyBotonesMovimiento(self, name, siLibre, siMas=siMas)
            return board, lytb, tb

        self.boardTutor, lytbtutor, self.tbtutor = create_board("tutor")
        self.boardUsuario, lytbuser, self.tbuser = create_board("user")
        self.boardRival, lytbRival, self.tbRival = create_board("rival", siRival)
        self.boardOpening, lytbOpening, self.tbOpening = create_board("opening", siOpenings, siLibre=False)
        tutor.ponBoardsGUI(self.boardTutor, self.boardUsuario, self.boardRival, self.boardOpening)

        # Puntuaciones
        self.lbTutorPuntuacion = Controles.LB(self).align_center().ponFuente(flb)
        self.lbUsuarioPuntuacion = Controles.LB(self).align_center().ponFuente(flb)
        if siRival:
            self.lbRivalPuntuacion = Controles.LB(self).align_center().ponFuente(flb)

        # Openings
        if siOpenings:
            li_options = self.tutor.opcionesOpenings()
            self.cbOpenings = Controles.CB(self, li_options, 0)
            self.cbOpenings.setFont(flba)
            self.connect(self.cbOpenings, QtCore.SIGNAL("currentIndexChanged(int)"), self.tutor.cambiarOpening)

        # RM
        liRM = []
        for n, uno in enumerate(tutor.list_rm):
            liRM.append((uno[1], n))

        self.cbRM, self.lbRM = QTUtil2.comboBoxLB(self, liRM, liRM[0][1], _("Moves analyzed"))
        self.connect(self.cbRM, QtCore.SIGNAL("currentIndexChanged (int)"), tutor.cambiadoRM)
        lyRM = Colocacion.H().control(self.lbRM).control(self.cbRM)

        lyTutor = Colocacion.V().relleno().control(self.lbTutorPuntuacion).relleno()
        gbTutor = Controles.GB(self, _("Tutor's suggestion"), lyTutor).ponFuente(f).align_center()
        if siPuntos:
            gbTutor.to_connect(self.elegirTutor)
            self.lbTutorPuntuacion.setEnabled(True)

        lyUsuario = Colocacion.V().relleno().control(self.lbUsuarioPuntuacion).relleno()
        gbUsuario = (
            Controles.GB(self, _("Your move"), lyUsuario).ponFuente(f).align_center().to_connect(self.elegirUsuario)
        )
        self.lbUsuarioPuntuacion.setEnabled(True)
        btLibros = Controles.PB(self, _("Consult a book"), self.consultaLibro).ponPlano(False)

        if siRival:
            lyRival = Colocacion.V().relleno().control(self.lbRivalPuntuacion).relleno()
            gbRival = Controles.GB(self, _("Opponent's prediction"), lyRival).ponFuente(f).align_center()

        if siOpenings:
            lyOpenings = Colocacion.V().relleno().control(self.cbOpenings).relleno()
            gbOpenings = Controles.GB(self, _("Opening"), lyOpenings).align_center().ponFuente(f)
            if siPuntos:
                gbOpenings.to_connect(self.elegirOpening)
            self.cbOpenings.setEnabled(True)
            self.tutor.cambiarOpening(0)

        dicVista = {
            POS_TUTOR_HORIZONTAL: ((0, 1), (0, 2)),
            POS_TUTOR_HORIZONTAL_2_1: ((0, 1), (4, 0)),
            POS_TUTOR_HORIZONTAL_1_2: ((4, 0), (4, 1)),
            POS_TUTOR_VERTICAL: ((4, 0), (8, 0)),
        }

        usu, riv = dicVista[self.x_tutor_view]

        fu, cu = usu
        fr, cr = riv

        layout = Colocacion.G()
        layout.controlc(gbTutor, 0, 0).controlc(self.boardTutor, 1, 0).otro(lytbtutor, 2, 0).otroc(lyRM, 3, 0)
        layout.controlc(gbUsuario, fu, cu).controlc(self.boardUsuario, fu + 1, cu).otro(lytbuser, fu + 2, cu).controlc(
            btLibros, fu + 3, cu
        )
        if siRival:
            layout.controlc(gbRival, fr, cr).controlc(self.boardRival, fr + 1, cr).otro(lytbRival, fr + 2, cr)
        elif siOpenings:
            layout.controlc(gbOpenings, fr, cr).controlc(self.boardOpening, fr + 1, cr).otro(lytbOpening, fr + 2, cr)

        layout.margen(8)

        self.setLayout(layout)

        self.restore_video(siTam=False)

    def process_toolbar(self):
        self.exeTB(self.sender().key)

    def exeTB(self, accion):
        x = accion.index("Mover")
        quien = accion[:x]
        que = accion[x + 5 :]
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

    def elegirTutor(self):
        self.save_video()
        self.accept()

    def elegirOpening(self):
        self.siElegidaOpening = True
        self.save_video()
        self.accept()

    def elegirUsuario(self):
        self.save_video()
        self.reject()

    def ponPuntuacionUsuario(self, txt):
        self.lbUsuarioPuntuacion.setText(txt)

    def ponPuntuacionTutor(self, txt):
        self.lbTutorPuntuacion.setText(txt)

    def ponPuntuacionRival(self, txt):
        self.lbRivalPuntuacion.setText(txt)

    def start_clock(self, funcion):
        if not hasattr(self, "timer"):
            self.timer = QtCore.QTimer(self)
            self.connect(self.timer, QtCore.SIGNAL("timeout()"), funcion)
        self.timer.start(1000)

    def stop_clock(self):
        if hasattr(self, "timer"):
            self.timer.stop()
            delattr(self, "timer")
