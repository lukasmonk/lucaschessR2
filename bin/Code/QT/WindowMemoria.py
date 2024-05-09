import random
import time

from PySide2 import QtCore, QtGui, QtWidgets

from Code.Base import Position
from Code.Board import Board2
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WDatos(QtWidgets.QDialog):
    def __init__(self, w_parent, txtcategoria, max_level):
        super(WDatos, self).__init__(w_parent)

        self.setWindowTitle(_("Check your memory on a chessboard"))
        self.setWindowIcon(Iconos.Memoria())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        tb = QTVarios.tb_accept_cancel(self)

        f = Controles.FontType(puntos=12, peso=75)

        self.ed, lb = QTUtil2.spinbox_lb(
            self, max_level, 1, max_level, etiqueta=txtcategoria + " " + _("Level"), max_width=40
        )
        lb.set_font(f)

        ly = Colocacion.H().control(lb).control(self.ed).margen(20)

        layout = Colocacion.V().control(tb).otro(ly).margen(3)

        self.setLayout(layout)

    def aceptar(self):
        self.nivel = self.ed.value()
        self.accept()


def paramMemoria(parent, txtCategoria, max_level):
    if max_level == 1:
        return 1

    # Datos
    w = WDatos(parent, txtCategoria, max_level)
    if w.exec_():
        return w.nivel
    else:
        return None


class WMemoria(LCDialog.LCDialog):
    def __init__(self, procesador, txtcategoria, nivel, seconds, listaFen, record):

        titulo = _("Check your memory on a chessboard")
        icono = Iconos.Memoria()
        extparam = "memoria"
        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, extparam)

        f = Controles.FontType(puntos=10, peso=75)

        self.configuration = procesador.configuration
        self.nivel = nivel
        self.seconds = seconds
        self.record = record

        # Board
        config_board = self.configuration.config_board("MEMORIA", 48)

        self.listaFen = listaFen

        self.position = Position.Position()

        self.board = Board2.PosBoard(self, config_board)
        self.board.crea()
        self.board.set_dispatch_drop(self.dispatchDrop)
        self.board.baseCasillasSC.setAcceptDrops(True)
        self.ultimaPieza = "P"
        self.piezas = self.board.piezas

        tamPiezas = max(16, int(32 * self.board.config_board.width_piece() / 48))
        self.listaPiezasW = QTVarios.ListaPiezas(self, "P,N,B,R,Q,K", self.board, tamPiezas, margen=0)
        self.listaPiezasB = QTVarios.ListaPiezas(self, "p,n,b,r,q,k", self.board, tamPiezas, margen=0)

        # Ayuda
        lbAyuda = Controles.LB(
            self,
            _(
                "<ul><li><b>Add piece</b> : Right mouse button on empty square</li><li><b>Copy piece</b> : Left mouse button on empty square</li><li><b>Move piece</b> : Drag and drop piece with left mouse button</li><li><b>Delete piece</b> : Right mouse button on occupied square</li></ul>"
            ),
        )
        ly = Colocacion.H().control(lbAyuda)
        self.gbAyuda = Controles.GB(self, _("Help"), ly)

        # Rotulos informacion
        lbCategoria = Controles.LB(self, txtcategoria).set_font(f)
        lbNivel = Controles.LB(self, _X(_("Level %1/%2"), str(nivel + 1), "25")).set_font(f)
        if record:
            lbRecord = Controles.LB(self, _X(_("Record %1 seconds"), str(record))).set_font(f)

        # Rotulo de vtime
        self.rotuloDispone = (
            Controles.LB(
                self,
                _X(
                    _("You have %1 seconds to remember the position of %2 pieces"),
                    str(self.seconds),
                    str(self.nivel + 3),
                ),
            )
            .set_wrap()
            .set_font(f)
            .align_center()
        )
        self.rotuloDispone1 = (
            Controles.LB(self, _("when you know you can press the Continue button"))
            .set_wrap()
            .set_font(f)
            .align_center()
        )
        ly = Colocacion.V().control(self.rotuloDispone).control(self.rotuloDispone1)
        self.gbTiempo = Controles.GB(self, "", ly)

        self.rotuloDispone1.hide()

        # Tool bar
        li_acciones = (
            (_("Start"), Iconos.Empezar(), "empezar"),
            (_("Continue"), Iconos.Pelicula_Seguir(), "seguir"),
            (_("Verify"), Iconos.Check(), "comprobar"),
            (_("Target"), Iconos.Verde32(), "objetivo"),
            (_("Wrong"), Iconos.Rojo32(), "nuestro"),
            (_("Repeat"), Iconos.Pelicula_Repetir(), "repetir"),
            (_("Resign"), Iconos.Abandonar(), "abandonar"),
        )
        self.tb = tb = Controles.TB(self, li_acciones)
        self.pon_toolbar(["empezar"])

        # Colocamos
        lyP = Colocacion.H().relleno().control(self.listaPiezasW).control(self.listaPiezasB).relleno().margen(0)
        lyT = Colocacion.V().control(self.board).otro(lyP).margen(0)

        lyI = Colocacion.V()
        lyI.control(tb)
        lyI.relleno()
        lyI.controlc(lbCategoria)
        lyI.controlc(lbNivel)
        if record:
            lyI.controlc(lbRecord)
        lyI.controlc(self.gbTiempo)
        lyI.relleno()
        lyI.control(self.gbAyuda)
        lyI.margen(3)

        ly = Colocacion.H().otro(lyT).otro(lyI).relleno()
        ly.margen(3)

        self.setLayout(ly)

        self.timer = None

        self.encenderExtras(False)

    def mueve(self, from_sq, to_sq):
        if from_sq == to_sq:
            return
        if self.squares.get(to_sq):
            self.board.borraPieza(to_sq)
        self.squares[to_sq] = self.squares.get(from_sq)
        self.squares[from_sq] = None
        self.board.muevePieza(from_sq, to_sq)

    def borraCasilla(self, from_sq):
        self.squares[from_sq] = None
        self.board.borraPieza(from_sq)

    def creaCasilla(self, from_sq):
        menu = QtWidgets.QMenu(self)

        siK = False
        sik = False
        for p in self.squares.values():
            if p == "K":
                siK = True
            elif p == "k":
                sik = True

        li_options = []
        if not siK:
            li_options.append((_("King"), "K"))
        li_options.extend(
            [(_("Queen"), "Q"), (_("Rook"), "R"), (_("Bishop"), "B"), (_("Knight"), "N"), (_("Pawn"), "P")]
        )
        if not sik:
            li_options.append((_("King"), "k"))
        li_options.extend(
            [(_("Queen"), "q"), (_("Rook"), "r"), (_("Bishop"), "b"), (_("Knight"), "n"), (_("Pawn"), "p")]
        )

        for txt, pieza in li_options:
            icono = self.board.piezas.icono(pieza)

            accion = QtWidgets.QAction(icono, txt, menu)
            accion.key = pieza
            menu.addAction(accion)

        resp = menu.exec_(QtGui.QCursor.pos())
        if resp:
            pieza = resp.key
            self.ponPieza(from_sq, pieza)

    def repitePieza(self, from_sq):
        self.squares[from_sq] = self.ultimaPieza
        pieza = self.board.creaPieza(self.ultimaPieza, from_sq)
        pieza.activa(True)

    def ponPieza(self, from_sq, pieza):
        antultimo = self.ultimaPieza
        self.ultimaPieza = pieza
        self.repitePieza(from_sq)
        if pieza == "K":
            self.ultimaPieza = antultimo
        if pieza == "k":
            self.ultimaPieza = antultimo

    def dispatchDrop(self, from_sq, pieza):
        if self.squares.get(from_sq):
            self.borraCasilla(from_sq)
        self.ponPieza(from_sq, pieza)

    def process_toolbar(self):
        accion = self.sender().key
        if accion == "abandonar":
            self.reject()
        elif accion == "empezar":
            self.empezar()
        elif accion == "seguir":
            self.seguir()
        elif accion == "comprobar":
            self.comprobar()
        elif accion == "objetivo":
            self.objetivo()
        elif accion == "nuestro":
            self.nuestro()
        elif accion == "repetir":
            self.repetir()

    def pon_toolbar(self, li_acciones):

        self.tb.clear()
        for k in li_acciones:
            self.tb.dic_toolbar[k].setVisible(True)
            self.tb.dic_toolbar[k].setEnabled(True)
            self.tb.addAction(self.tb.dic_toolbar[k])

        self.tb.li_acciones = li_acciones
        self.tb.update()

    def empezar(self):
        # Ha pulsado empezar

        # Elegimos el fen de la lista
        nPos = random.randint(0, len(self.listaFen) - 1)
        self.fenObjetivo = self.listaFen[nPos]
        del self.listaFen[nPos]
        self.position.read_fen(self.fenObjetivo)
        self.board.set_position(self.position)
        self.board.disable_all()
        self.squares = self.position.squares
        self.board.squares = self.squares

        # Quitamos empezar y ponemos seguir
        self.pon_toolbar(["seguir"])

        self.rotuloDispone.set_text(
            _X(_("You have %1 seconds to remember the position of %2 pieces"), str(self.seconds), str(self.nivel + 3))
        )
        self.rotuloDispone1.set_text(_("when you know you can press the Continue button"))
        self.rotuloDispone1.show()
        self.rotuloDispone1.show()
        self.gbTiempo.show()

        self.pending_time = self.seconds
        self.start_clock()

    def seguir(self):
        self.stop_clock()

        self.board.set_dispatcher(self.mueve)
        self.board.mensBorrar = self.borraCasilla
        self.board.mensCrear = self.creaCasilla
        self.board.mensRepetir = self.repitePieza

        # Quitamos seguir y ponemos comprobar
        self.pon_toolbar(["comprobar"])

        self.rotuloDispone1.set_text(
            _X(_("When you've loaded the %1 pieces you can click the Check button"), str(self.nivel + 3))
        )
        self.rotuloDispone.setVisible(False)

        self.iniTiempo = time.time()

        for k in self.squares:
            self.squares[k] = None
        self.board.set_position(self.position)

        self.encenderExtras(True)

    def encenderExtras(self, si):
        self.gbAyuda.setVisible(si)
        self.listaPiezasW.setEnabled(si)
        self.listaPiezasB.setEnabled(si)

    def ponCursor(self):
        cursor = self.piezas.cursor(self.ultimaPieza)
        for item in self.board.escena.items():
            item.setCursor(cursor)
        self.board.setCursor(cursor)

    def comprobar(self):

        self.vtime = int(time.time() - self.iniTiempo)

        fenNuevo = self.position.fen()
        fenNuevo = fenNuevo[: fenNuevo.index(" ")]
        fenComprobar = self.fenObjetivo
        fenComprobar = fenComprobar[: fenComprobar.index(" ")]

        if fenComprobar == fenNuevo:
            mens = _X(_("Right, it took %1 seconds."), str(self.vtime))
            if self.vtime < self.record or self.record == 0:
                mens += "<br>" + _("New record!")
            QTUtil2.message_bold(self, mens)
            self.accept()
            return

        QTUtil2.message_bold(self, _("The position is incorrect."))

        self.fenNuestro = self.position.fen()

        self.board.set_dispatcher(None)
        self.board.mensBorrar = None
        self.board.mensCrear = None
        self.board.mensRepetir = None
        self.board.disable_all()

        self.gbTiempo.hide()

        self.encenderExtras(False)

        # Quitamos comprobar y ponemos el resto
        li = ["objetivo", "nuestro"]
        if len(self.listaFen):
            li.append("repetir")

        self.pon_toolbar(li)

    def objetivo(self):
        self.position.read_fen(self.fenObjetivo)
        self.board.set_position(self.position)
        self.board.disable_all()

    def nuestro(self):
        self.position.read_fen(self.fenNuestro)
        self.board.set_position(self.position)
        self.board.disable_all()

    def repetir(self):
        self.rotuloDispone.set_text(
            _X(_("You have %1 seconds to remember the position of %2 pieces"), str(self.seconds), str(self.nivel + 3))
        )
        self.rotuloDispone.show()
        self.rotuloDispone1.hide()
        self.gbTiempo.show()

        self.empezar()

    def reloj(self):
        self.pending_time -= 1

        self.rotuloDispone.set_text(
            _X(
                _("You have %1 seconds to remember the position of %2 pieces"),
                str(self.pending_time),
                str(self.nivel + 3),
            )
        )
        if self.pending_time == 0:
            self.seguir()

    def start_clock(self):
        if self.timer is not None:
            self.timer.stop()
            del self.timer

        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.reloj)
        self.timer.start(1000)

    def stop_clock(self):
        if self.timer is not None:
            self.timer.stop()
            del self.timer
            self.timer = None


def lanzaMemoria(procesador, txtcategoria, nivel, seconds, listaFen, record):
    w = WMemoria(procesador, txtcategoria, nivel, seconds, listaFen, record)
    if w.exec_():
        return w.vtime
    else:
        return None
