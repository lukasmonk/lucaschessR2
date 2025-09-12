import random
import time

from PySide2 import QtCore, QtGui, QtWidgets

from Code.Base import Position
from Code.Base.Constantes import WHITE, BLACK
from Code.Board import Board2
from Code.QT import Colocacion
from Code.QT import Columnas, Grid
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
        self.repetitions = 0
        self.pending_time = 0
        self.cumulative_time = 0

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
        self.ini_time_target = None

        tamPiezas = max(16, int(32 * self.board.config_board.width_piece() / 48))
        self.listaPiezasW = QTVarios.ListaPiezas(self, WHITE, self.board, tamPiezas, margen=0)
        self.listaPiezasB = QTVarios.ListaPiezas(self, BLACK, self.board, tamPiezas, margen=0)

        # Ayuda
        lb_ayuda = Controles.LB(
            self,
            _(
                "<ul><li><b>Add piece</b> : Right mouse button on empty square</li><li><b>Copy piece</b> : Left mouse button on empty square</li><li><b>Move piece</b> : Drag and drop piece with left mouse button</li><li><b>Delete piece</b> : Right mouse button on occupied square</li></ul>"
            ),
        )
        lb_ayuda.set_wrap()
        ly = Colocacion.H().control(lb_ayuda)
        self.gbAyuda = Controles.GB(self, _("Help"), ly)

        # Rotulos informacion
        lb_categoria = Controles.LB(self, txtcategoria)
        lb_categoria.setStyleSheet("border:1px solid lightgray;")
        lb_nivel = Controles.LB(self, _X(_("Level %1/%2"), str(nivel + 1), "25"))

        lb_record = Controles.LB(self, _X(_("Record %1 seconds"), f"{record:0.02f}") if record else "")
        lb_record.setVisible(record)

        f_rot16 = Controles.FontType(puntos=16, peso=75)
        f_rot14 = Controles.FontType(puntos=14)
        for lb in (lb_nivel, lb_categoria, lb_record):
            lb.set_font(f_rot16 if lb == lb_categoria else f_rot14)
            lb.align_center()
            lb.anchoFijo(460)

        ly_rot_basicos = Colocacion.V().control(lb_categoria).control(lb_nivel).control(lb_record).margen(0)

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

        tbmenu = Controles.TBrutina(self)
        tbmenu.new(_("Close"), Iconos.MainMenu(), self.terminar)

        # Toolbar
        li_acciones = (
            (_("Start"), Iconos.Empezar(), self.start),
            (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir),
            (_("Verify"), Iconos.Check(), self.comprobar),
            (_("Target"), Iconos.Verde32(), self.target),
            (_("Wrong"), Iconos.Rojo32(), self.wrong),
            (_("Repeat"), Iconos.Pelicula_Repetir(), self.repetir),
            (_("Resign"), Iconos.Abandonar(), self.abandonar),
            (_("New"), Iconos.New1(), self.new_try),
        )
        self.tb = tb = Controles.TBrutina(self)
        tb.set_actions(li_acciones)
        self.pon_toolbar([self.start, ])

        ly_tb = Colocacion.H().control(tbmenu).relleno().control(self.tb).margen(0)

        # Colocamos
        ly_up = Colocacion.H().relleno().control(self.listaPiezasB).relleno().margen(0)
        ly_down = Colocacion.H().relleno().control(self.listaPiezasW).relleno().margen(0)
        ly_t = Colocacion.V().otro(ly_up).control(self.board).otro(ly_down).margen(0)

        ly_i = Colocacion.V()
        ly_i.otro(ly_tb)
        ly_i.espacio(10)
        ly_i.otro(ly_rot_basicos)
        ly_i.relleno()
        ly_i.controlc(self.gbTiempo)
        ly_i.relleno(2)
        ly_i.control(self.gbAyuda)
        ly_i.margen(3)

        ly = Colocacion.H().otro(ly_i).otro(ly_t).relleno()
        ly.margen(3)

        self.setLayout(ly)

        self.timer = None

        for lb in (lb_ayuda, self.rotuloDispone1, self.rotuloDispone):
            lb.anchoFijo(420)

        self.encenderExtras(False)

        self.restore_video()

    def terminar(self):
        self.save_video()
        self.reject()

    def closeEvent(self, event):
        self.save_video()

    def mueve(self, from_sq, to_sq):
        if from_sq == to_sq:
            return
        if self.squares.get(to_sq):
            self.board.remove_piece(to_sq)
        self.squares[to_sq] = self.squares.get(from_sq)
        self.squares[from_sq] = None
        self.board.move_piece(from_sq, to_sq)

    def clean_square(self, from_sq):
        self.squares[from_sq] = None
        self.board.remove_piece(from_sq)

    def rightmouse_square(self, from_sq):
        menu = QtWidgets.QMenu(self)

        si_kw = False
        si_kb = False
        for p in self.squares.values():
            if p == "K":
                si_kw = True
            elif p == "k":
                si_kb = True

        li_options = []
        if not si_kw:
            li_options.append((_("King"), "K"))
        li_options.extend(
            [(_("Queen"), "Q"), (_("Rook"), "R"), (_("Bishop"), "B"), (_("Knight"), "N"), (_("Pawn"), "P")]
        )
        if not si_kb:
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
            self.clean_square(from_sq)
        self.ponPieza(from_sq, pieza)

    def new_try(self):
        self.empezar(True)

    def start(self):
        self.empezar(True)

    def abandonar(self):
        self.reject()

    def pon_toolbar(self, li_acciones):
        self.tb.clear()
        for k in li_acciones:
            self.tb.dic_toolbar[k].setVisible(True)
            self.tb.dic_toolbar[k].setEnabled(True)
            self.tb.addAction(self.tb.dic_toolbar[k])

        self.tb.li_acciones = li_acciones
        self.tb.update()
        self.tb.remove_tooltips()

    def empezar(self, new=True):

        # Elegimos el fen de la lista
        if new:
            n_pos = random.randint(0, len(self.listaFen) - 1)
            self.fenObjetivo = self.listaFen[n_pos]
            del self.listaFen[n_pos]
            self.repetitions = 0
            self.cumulative_time = 0
        else:
            self.repetitions += 1
            if self.ini_time_target:
                self.cumulative_time += time.time() - self.ini_time_target

        self.ini_time_target = None
        self.position.read_fen(self.fenObjetivo)
        self.board.set_position(self.position)
        self.board.disable_all()
        self.squares = self.position.squares
        self.board.squares = self.squares

        # Quitamos empezar y ponemos seguir
        self.pon_toolbar([self.seguir, ])

        if new:
            self.pending_time = self.seconds
        else:
            self.pending_time = max(int(self.seconds // (self.repetitions + 1)), self.nivel + 3)

        self.rotuloDispone.set_text(
            _X(_("You have %1 seconds to remember the position of %2 pieces"), str(self.pending_time),
               str(self.nivel + 3))
        )
        self.rotuloDispone1.set_text(_("when you know you can press the Continue button"))

        self.rotuloDispone.show()
        self.rotuloDispone1.show()
        self.gbTiempo.show()

        self.start_clock()

    def seguir(self):
        self.stop_clock()

        self.board.set_dispatcher(self.mueve)
        self.board.mensBorrar = self.clean_square
        self.board.mensCrear = self.rightmouse_square
        self.board.mensRepetir = self.repitePieza

        # Quitamos seguir y ponemos comprobar
        self.pon_toolbar([self.comprobar, ])

        self.rotuloDispone1.set_text(
            _X(_("When you've loaded the %1 pieces you can click the Check button"), str(self.nivel + 3))
        )
        self.rotuloDispone.setVisible(False)

        self.iniTiempo = time.time()

        for k in self.squares:
            self.squares[k] = None
        self.board.set_position(self.position)

        self.encenderExtras(True)

        self.rotuloDispone1.show()

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
        self.vtime = time.time() - self.iniTiempo
        self.cumulative_time += self.vtime

        fen_nuevo = self.position.fen()
        fen_nuevo = fen_nuevo[: fen_nuevo.index(" ")]
        fen_comprobar = self.fenObjetivo
        fen_comprobar = fen_comprobar[: fen_comprobar.index(" ")]

        if fen_comprobar == fen_nuevo:
            mens = _X(_("Right, it took %1 seconds."), f"{self.cumulative_time: 0.02f}")
            if self.cumulative_time < self.record or self.record == 0:
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
        li = [self.repetir, self.target, self.wrong]
        if len(self.listaFen):
            li.append(self.new_try)

        self.pon_toolbar(li)

    # def quita_repetir(self):
    #     li = [self.target, self.wrong]
    #     if len(self.listaFen):
    #         li.append(self.new_try)
    #
    #     self.pon_toolbar(li)

    def target(self):
        self.ini_time_target = time.time()
        self.position.read_fen(self.fenObjetivo)
        self.board.set_position(self.position)
        self.board.disable_all()
        # self.quita_repetir()

    def wrong(self):
        if self.ini_time_target:
            self.cumulative_time += time.time() - self.ini_time_target
            self.ini_time_target = None
        self.position.read_fen(self.fenNuestro)
        self.board.set_position(self.position)
        self.board.disable_all()
        # self.quita_repetir()

    def repetir(self):
        self.rotuloDispone.set_text(
            _X(_("You have %1 seconds to remember the position of %2 pieces"), str(self.seconds), str(self.nivel + 3))
        )
        self.rotuloDispone.show()
        self.rotuloDispone1.hide()
        self.gbTiempo.show()

        self.empezar(False)

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
        self.timer.timeout.connect(self.reloj)
        self.timer.start(1000)

    def stop_clock(self):
        if self.timer is not None:
            self.timer.stop()
            del self.timer
            self.timer = None


def lanza_memoria(procesador, txtcategoria, nivel, seconds, lista_fen, record):
    w = WMemoria(procesador, txtcategoria, nivel, seconds, lista_fen, record)
    if w.exec_():
        return w.cumulative_time
    else:
        return None


class WMemoryResults(LCDialog.LCDialog):
    def __init__(self, w_parent, memory):
        super(WMemoryResults, self).__init__(w_parent, _("Results"), Iconos.Estadisticas2(), "memory_results7")

        self.memory = memory

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("level", _("Level"), 60, align_center=True)

        for num_cat in range(6):
            cat = memory.categorias.number(num_cat)
            o_columns.nueva(f"cat_{num_cat}", cat.name(), 140, align_center=True)
            o_columns.nueva(f"inc_{num_cat}", "∆", 60, align_center=True)
        grid = Grid.Grid(self, o_columns, siSelecFilas=True, altoFila=24)
        grid.coloresAlternados()
        self.register_grid(grid)

        tb = Controles.TBrutina(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)

        layout = Colocacion.V().control(tb).control(grid).margen(3)

        self.setLayout(layout)

        self.restore_video(default_width=grid.anchoColumnas() + 24, default_height=720)
        grid.gotop()
        grid.setFocus()

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()

    @staticmethod
    def grid_num_datos(grid):
        return 25

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        level = row
        if key == "level":
            return str(level + 1)
        xcat = int(key[4:])
        li_data = self.memory.dic_data[xcat]
        record = li_data[row]
        if record == 0:
            return ""
        if key.startswith("inc"):
            record = record / (level + 3)
        return f"{record:0.02f}"
