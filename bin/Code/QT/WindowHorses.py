import atexit
import datetime
import random
import time

import FasterCode

from Code import Util
from Code.Base import Position
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import Base


class HorsesHistorico:
    def __init__(self, file, test):
        self.file = file
        self.db = Base.DBBase(file)
        self.tabla = test

        if not self.db.existeTabla(self.tabla):
            self.creaTabla()

        self.dbf = self.db.dbf(self.tabla, "FECHA,MOVES,SECONDS,HINTS", orden="FECHA DESC")
        self.dbf.leer()

        self.orden = "FECHA", "DESC"

        atexit.register(self.close)

    def close(self):
        if self.dbf:
            self.dbf.cerrar()
            self.dbf = None
        self.db.cerrar()

    def creaTabla(self):
        tb = Base.TablaBase(self.tabla)
        tb.nuevoCampo("FECHA", "VARCHAR", notNull=True, primaryKey=True)
        tb.nuevoCampo("MOVES", "INTEGER")
        tb.nuevoCampo("SECONDS", "INTEGER")
        tb.nuevoCampo("HINTS", "INTEGER")
        self.db.generarTabla(tb)

    def __len__(self):
        return self.dbf.reccount()

    def goto(self, num):
        self.dbf.goto(num)

    def put_order(self, key):
        nat, orden = self.orden
        if key == nat:
            orden = "DESC" if orden == "ASC" else "ASC"
        else:
            nat = key
            orden = "DESC" if key == "FECHA" else "ASC"
        self.dbf.put_order(nat + " " + orden)
        self.orden = nat, orden

        self.dbf.leer()
        self.dbf.gotop()

    def fecha2txt(self, fecha):
        return "%4d%02d%02d%02d%02d%02d" % (fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute, fecha.second)

    def txt2fecha(self, txt):
        def x(d, h):
            return int(txt[d:h])

        year = x(0, 4)
        month = x(4, 6)
        day = x(6, 8)
        hour = x(8, 10)
        minute = x(10, 12)
        second = x(12, 14)
        fecha = datetime.datetime(year, month, day, hour, minute, second)
        return fecha

        self.dbf = self.db.dbf(self.tabla, "", orden="fecha desc")

    def append(self, fecha, moves, seconds, hints):
        br = self.dbf.baseRegistro()
        br.FECHA = self.fecha2txt(fecha)
        br.MOVES = moves
        br.SECONDS = seconds
        br.HINTS = hints
        self.dbf.insertar(br)

    def __getitem__(self, num):
        self.dbf.goto(num)
        reg = self.dbf.registroActual()
        reg.FECHA = self.txt2fecha(reg.FECHA)
        return reg

    def remove_list_recnos(self, liNum):
        self.dbf.remove_list_recnos(liNum)
        self.dbf.pack()
        self.dbf.leer()


class WHorsesBase(LCDialog.LCDialog):
    def __init__(self, procesador, test, titulo, tabla, icono):

        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, "horsesBase")

        self.procesador = procesador
        self.configuration = procesador.configuration
        self.tabla = tabla
        self.icono = icono
        self.test = test
        self.titulo = titulo

        self.historico = HorsesHistorico(self.configuration.ficheroHorses, tabla)

        # Historico
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("FECHA", _("Date"), 120, align_center=True)
        o_columns.nueva("MOVES", _("Moves"), 100, align_center=True)
        o_columns.nueva("SECONDS", _("Second(s)"), 80, align_center=True)
        o_columns.nueva("HINTS", _("Hints"), 90, align_center=True)
        self.ghistorico = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.ghistorico.setMinimumWidth(self.ghistorico.anchoColumnas() + 20)

        # Tool bar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Start"), Iconos.Empezar(), self.empezar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        # Colocamos
        lyTB = Colocacion.H().control(self.tb).margen(0)
        ly = Colocacion.V().otro(lyTB).control(self.ghistorico).margen(3)

        self.setLayout(ly)

        self.register_grid(self.ghistorico)
        self.restore_video(siTam=False)

        self.ghistorico.gotop()

    def grid_doubleclick_header(self, grid, o_column):
        key = o_column.key
        if key in ("FECHA", "MOVES", "HINTS"):
            self.historico.put_order(key)
            self.ghistorico.gotop()
            self.ghistorico.refresh()

    def grid_num_datos(self, grid):
        return len(self.historico)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        reg = self.historico[row]
        if col == "FECHA":
            return Util.localDateT(reg.FECHA)
        elif col == "MOVES":
            return "%d" % reg.MOVES
        elif col == "SECONDS":
            return "%d" % reg.SECONDS
        elif col == "HINTS":
            return "%d" % reg.HINTS

    def terminar(self):
        self.save_video()
        self.historico.close()
        self.reject()

    def borrar(self):
        li = self.ghistorico.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                self.historico.remove_list_recnos(li)
        self.ghistorico.gotop()
        self.ghistorico.refresh()

    def empezar(self):
        w = WHorses(self, self.test, self.procesador, self.titulo, self.icono)
        w.exec_()
        self.ghistorico.gotop()
        self.ghistorico.refresh()


class WHorses(LCDialog.LCDialog):
    def __init__(self, owner, test, procesador, titulo, icono):

        LCDialog.LCDialog.__init__(self, owner, titulo, icono, "horses")

        self.historico = owner.historico
        self.procesador = owner.procesador
        self.configuration = self.procesador.configuration

        self.test = test

        # Board
        config_board = self.configuration.config_board("HORSES", 48)

        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.side_indicator_sc.setOpacity(0.01)
        self.board.set_dispatcher(self.player_has_moved)

        # Rotulo vtime
        self.lbInformacion = Controles.LB(self, _("Goal: to capture the king up to the square a8")).align_center()
        self.lbMoves = Controles.LB(self, "")

        # Tool bar
        li_acciones = (
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Reinit"), Iconos.Reiniciar(), self.reiniciar),
            None,
            (_("Help"), Iconos.AyudaGR(), self.get_help),
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        # Layout
        lyInfo = Colocacion.H().control(self.lbInformacion).relleno().control(self.lbMoves)
        lyT = Colocacion.V().relleno().control(self.board).otro(lyInfo).relleno().margen(10)

        ly = Colocacion.V().control(self.tb).otro(lyT).relleno().margen(0)

        self.setLayout(ly)

        self.restore_video()
        self.adjustSize()

        self.reset()

    def reset(self):
        self.preparaTest()
        self.board.set_side_bottom(True)
        self.board.set_position(self.cpInicial)
        self.board.remove_arrows()
        self.min_moves = 0
        self.timer = time.time()
        self.moves = 0
        self.hints = 0
        self.nayuda = 0  # para que haga un rondo al elegir en la get_help de todos los caminos uno de ellos
        self.ponSiguiente()

    def ponNumMoves(self):
        color = "red" if self.numMoves <= self.movesParcial else "green"
        self.lbMoves.set_text('<font color="%s">%d/%d</font>' % (color, self.movesParcial, self.numMoves))

    def ponSiguiente(self):

        posDesde = self.camino[0 if self.baseUnica else self.current_position]
        posHasta = self.camino[self.current_position + 1]
        tlist = FasterCode.li_n_min(posDesde, posHasta, self.celdas_ocupadas)
        self.numMoves = len(tlist[0]) - 1
        self.min_moves += self.numMoves
        self.movesParcial = 0

        cp = self.cpInicial.copia()

        self.posTemporal = posDesde
        ca = FasterCode.pos_a1(posDesde)
        cp.squares[ca] = "N" if self.is_white else "n"
        cs = FasterCode.pos_a1(posHasta)
        cp.squares[cs] = "k" if self.is_white else "K"

        self.cpActivo = cp

        self.board.set_position(cp)
        self.board.activate_side(self.is_white)

        self.ponNumMoves()

    def avanza(self):
        self.board.remove_arrows()
        self.current_position += 1
        if self.current_position == len(self.camino) - 1:
            self.final()
            return
        self.ponSiguiente()

    def final(self):
        seconds = int(time.time() - self.timer)
        self.historico.append(Util.today(), self.moves, seconds, self.hints)

        QTUtil2.message_bold(
            self,
            "<b>%s<b><ul><li>%s: <b>%d</b> (%s=%d) </li><li>%s: <b>%d</b></li><li>%s: <b>%d</b></li></ul>"
            % (
                _("Congratulations, goal achieved"),
                _("Moves"),
                self.moves,
                _("Minimum"),
                self.min_moves,
                _("Second(s)"),
                seconds,
                _("Hints"),
                self.hints,
            ),
        )

        self.save_video()
        self.accept()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        p0 = FasterCode.a1_pos(from_sq)
        p1 = FasterCode.a1_pos(to_sq)
        if p1 in FasterCode.dict_n[p0]:
            self.moves += 1
            self.movesParcial += 1
            self.ponNumMoves()
            if not (p1 in self.camino):
                return False
            self.cpActivo.squares[from_sq] = None
            self.cpActivo.squares[to_sq] = "N" if self.is_white else "n"
            self.board.set_position(self.cpActivo)
            self.board.activate_side(self.is_white)
            self.posTemporal = p1
            if p1 == self.camino[self.current_position + 1]:
                self.avanza()
                return True
            return True
        return False

    def preparaTest(self):
        self.cpInicial = Position.Position()
        self.cpInicial.read_fen("8/8/8/8/8/8/8/8 w - - 0 1")
        squares = self.cpInicial.squares
        self.baseUnica = self.test > 3
        self.is_white = random.randint(1, 2) == 1

        if self.test in (1, 4, 5):
            celdas_ocupadas = []
        elif self.test == 2:  # 4 peones
            if self.is_white:
                celdas_ocupadas = [18, 21, 9, 11, 12, 14, 42, 45, 33, 35, 36, 38]
            else:
                celdas_ocupadas = [18, 21, 25, 27, 28, 30, 42, 45, 49, 51, 52, 54]
            for a1 in ("c3", "c6", "f3", "f6"):
                squares[a1] = "p" if self.is_white else "P"
        elif self.test == 3:  # levitt
            ch = celdas_ocupadas = [27]
            for li in FasterCode.dict_q[27]:
                for x in li:
                    ch.append(x)

            squares["d4"] = "q" if self.is_white else "Q"

        self.camino = []
        p, f, s = 0, 7, 1
        for x in range(8):
            li = list(range(p, f + s, s))
            for t in range(7, -1, -1):
                if li[t] in celdas_ocupadas:
                    del li[t]
            self.camino.extend(li)
            if s == 1:
                s = -1
                p += 15
                f += 1
            else:
                s = +1
                p += 1
                f += 15

        if self.test == 5:  # empieza en e4
            for n, x in enumerate(self.camino):
                if x == 28:
                    del self.camino[n]
                    self.camino.insert(0, 28)
                    break

        self.current_position = 0
        self.celdas_ocupadas = celdas_ocupadas

    def closeEvent(self, event):
        self.save_video()
        event.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def reiniciar(self):
        # Si no esta en la position actual, le lleva a la misma
        pa = self.posTemporal
        pi = self.camino[0 if self.baseUnica else self.current_position]

        if pa == pi:
            self.reset()
        else:
            self.ponSiguiente()

    def get_help(self):
        self.hints += 1
        self.board.remove_arrows()
        self.ponSiguiente()
        pa = self.camino[0 if self.baseUnica else self.current_position]
        ps = self.camino[self.current_position + 1]
        tlist = FasterCode.li_n_min(pa, ps, self.celdas_ocupadas)
        if self.nayuda >= len(tlist):
            self.nayuda = 0

        li = tlist[self.nayuda]
        for x in range(len(li) - 1):
            d = FasterCode.pos_a1(li[x])
            h = FasterCode.pos_a1(li[x + 1])
            self.board.show_arrow_mov(d, h, "2")
        self.nayuda += 1
        self.board.refresh()


def windowHorses(procesador, test, titulo, icono):
    tabla = "TEST%d" % test
    w = WHorsesBase(procesador, test, titulo, tabla, icono)
    w.exec_()
