import copy

from PySide2 import QtCore, QtWidgets

import Code
from Code import Util
from Code import Variations
from Code.Base import Game, Move
from Code.Board import Board
from Code.Openings import OpeningsStd
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import LCDialog


class WOpenings(LCDialog.LCDialog):
    def __init__(self, owner, configuration, opening_block):
        icono = Iconos.Opening()
        titulo = _("Select an opening")
        extparam = "selectOpening"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        # Variables--------------------------------------------------------------------------
        self.ap_std = OpeningsStd.ap
        self.configuration = configuration
        self.game = Game.Game()
        self.opening_block = opening_block
        self.liActivas = []

        # Board
        config_board = configuration.config_board("APERTURAS", 32)
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_dispatcher(self.player_has_moved)

        # Current pgn
        self.lbPGN = Controles.LB(self, "").set_wrap().ponTipoLetra(puntos=10, peso=75)
        ly = Colocacion.H().control(self.lbPGN)
        gb = Controles.GB(self, _("Selected opening"), ly).ponTipoLetra(puntos=11, peso=75).align_center()
        gb.setStyleSheet("""QGroupBox {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #E0E0E0, stop: 1 #FFFFFF);
    border: 2px solid gray;
    border-radius: 5px;
    margin-top: 10px; /* leave space at the top for the title */
    margin-bottom: 5px; /* leave space at the top for the title */
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center; /* position at the top center */
    padding: 3px;
    margin-top: -3px; /* leave space at the top for the title */
}
""")

        # Movimiento
        self.is_moving_time = False

        lyBM, tbBM = QTVarios.lyBotonesMovimiento(self, "", siLibre=False, icon_size=24)
        self.tbBM = tbBM

        # Tool bar
        tb = QTVarios.LCTB(self, icon_size=24)
        tb.new(_("Select"), Iconos.Aceptar(), self.aceptar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancelar)
        tb.new(_("Reinit"), Iconos.Reiniciar(), self.resetPartida)
        tb.new(_("Takeback"), Iconos.Atras(), self.atras)
        tb.new(_("Remove"), Iconos.Borrar(), self.borrar)

        # Lista Openings
        o_columns = Columnas.ListaColumnas()
        dicTipos = {"b": Iconos.pmSun(), "n": Iconos.pmPuntoAzul(), "l": Iconos.pmNaranja()}
        o_columns.nueva("TYPE", "", 24, edicion=Delegados.PmIconosBMT(dicIconos=dicTipos))
        o_columns.nueva("OPENING", _("Possible continuation"), 480)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, altoFila=32)
        self.register_grid(self.grid)

        # # Derecha
        lyD = Colocacion.V().control(tb).control(gb).control(self.grid)
        gbDerecha = Controles.GB(self, "", lyD)

        # # Izquierda
        lyI = Colocacion.V().control(self.board).otro(lyBM)
        gbIzquierda = Controles.GB(self, "", lyI)

        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(gbIzquierda)
        splitter.addWidget(gbDerecha)
        self.register_splitter(splitter, "splitter")

        # Completo
        ly = Colocacion.H().control(splitter).margen(3)
        self.setLayout(ly)

        self.ponActivas()
        self.resetPartida()
        self.actualizaPosicion()

        dic = {"_SIZE_": "916,444", "SP_splitter": [356, 548]}
        self.restore_video(dicDef=dic)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.board.disable_all()

        movimiento = from_sq + to_sq

        position = self.game.move(self.posCurrent).position if self.posCurrent >= 0 else self.game.last_position

        # Peon coronando
        if not promotion and position.siPeonCoronando(from_sq, to_sq):
            promotion = self.board.peonCoronando(position.is_white)
        if promotion:
            movimiento += promotion

        ok, mens, move = Move.get_game_move(self.game, position, from_sq, to_sq, promotion)
        if ok:
            self.nuevaJugada(move)
        else:
            self.actualizaPosicion()

    def grid_num_datos(self, grid):
        return len(self.liActivas)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        ap = self.liActivas[row]
        if key == "TYPE":
            return "b" if ap.is_basic else "n"
        else:
            return ap.name + "\n" + ap.pgn

    def grid_doble_click(self, grid, row, column):
        if -1 < row < len(self.liActivas):
            ap = self.liActivas[row]
            self.game.set_position()
            self.game.read_pv(ap.a1h8)
            self.ponActivas()

    def nuevaJugada(self, move):
        self.posCurrent += 1
        if self.posCurrent < len(self.game):
            self.game.li_moves = self.game.li_moves[: self.posCurrent]
        self.game.add_move(move)
        self.ponActivas()

    def ponActivas(self):
        self.liActivas = self.ap_std.list_possible_openings(self.game)

        self.board.set_position(self.game.last_position)

        self.game.assign_opening()
        txt = self.game.pgn_translated()
        if not txt:
            txt = _("None")
        if self.game.opening:
            txt = '%s<br><span style="color:gray;">%s</span>' % (txt, self.game.opening.name)

        self.lbPGN.set_text(txt)
        self.posCurrent = len(self.game) - 1

        self.actualizaPosicion()
        self.grid.refresh()
        self.grid.gotop()

        w = self.width()
        self.adjustSize()
        if self.width() != w:
            self.resize(w, self.height())

    def actualizaPosicion(self):
        if self.posCurrent > -1:
            move = self.game.move(self.posCurrent)
            position = move.position
        else:
            position = self.game.first_position
            move = None

        self.board.set_position(position)
        self.board.activate_side(position.is_white)
        if move:
            self.board.put_arrow_sc(move.from_sq, move.to_sq)

    def resetPartida(self):
        self.game.set_position()
        if self.opening_block:
            self.game.read_pv(self.opening_block.a1h8)
        self.ponActivas()
        self.mueve(siFinal=True)

    def terminar(self):
        self.is_moving_time = False
        self.save_video()

    def closeEvent(self, event):
        self.terminar()

    def aceptar(self):
        self.terminar()
        self.accept()

    def cancelar(self):
        self.terminar()
        self.reject()

    def atras(self):
        self.game.anulaSoloUltimoMovimiento()
        self.ponActivas()

    def borrar(self):
        self.game.set_position()
        self.ponActivas()

    def process_toolbar(self):
        accion = self.sender().key
        if accion == "MoverAdelante":
            self.mueve(n_saltar=1)
        elif accion == "MoverAtras":
            self.mueve(n_saltar=-1)
        elif accion == "MoverInicio":
            self.mueve(si_inicio=True)
        elif accion == "MoverFinal":
            self.mueve(siFinal=True)
        elif accion == "MoverTiempo":
            self.move_timed()

    def mueve(self, si_inicio=False, n_saltar=0, siFinal=False):
        num_moves = len(self.game)
        if n_saltar:
            pos = self.posCurrent + n_saltar
            if 0 <= pos < num_moves:
                self.posCurrent = pos
            else:
                return
        elif si_inicio:
            self.posCurrent = -1
        elif siFinal:
            self.posCurrent = num_moves - 1
        else:
            return
        self.actualizaPosicion()

    def move_timed(self):
        if self.is_moving_time:
            self.is_moving_time = False

        else:
            self.is_moving_time = True
            self.mueve(si_inicio=True)
            QtCore.QTimer.singleShot(1000, self.siguienteTiempo)

    def siguienteTiempo(self):
        if self.is_moving_time:
            if self.posCurrent < len(self.game) - 1:
                self.mueve(n_saltar=1)
                QtCore.QTimer.singleShot(2500, self.siguienteTiempo)
            else:
                self.is_moving_time = False

    def resultado(self):
        if len(self.game) == 0:
            return None
        ap = self.game.opening
        if ap is None:
            ap = OpeningsStd.OpeningsStd(_("Unknown"))
            ap.a1h8 = self.game.pv()
        else:
            if not self.game.last_jg().in_the_opening:
                p = Game.Game()
                p.read_pv(ap.a1h8)
                ap.a1h8 = self.game.pv()
                ap.tr_name += " + %s" % (self.game.pgn_translated()[len(p.pgn_translated()) + 1 :],)

        ap.pgn = self.game.pgn_translated()
        return ap


class EntrenamientoOpening(LCDialog.LCDialog):
    def __init__(self, owner, listaOpeningsStd, dic_data):
        icono = Iconos.Opening()
        titulo = _("Learn openings by repetition")
        extparam = "opentrainingE"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        name = dic_data.get("NOMBRE", "")
        self.listaOpeningsStd = listaOpeningsStd
        self.liBloques = self.leeBloques(dic_data.get("LISTA", []))

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Add"), Iconos.Nuevo(), self.nueva),
            None,
            (_("Modify"), Iconos.Modificar(), self.modificar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        lbNombre = Controles.LB(self, _("Name") + ": ")
        self.edNombre = Controles.ED(self, name)

        lyNombre = Colocacion.H().control(lbNombre).control(self.edNombre)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NOMBRE", _("Name"), 240)
        o_columns.nueva("PGN", _("Moves"), 360)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        n = self.grid.anchoColumnas()
        self.grid.setMinimumWidth(n + 20)
        self.register_grid(self.grid)
        self.grid.gotop()

        layout = Colocacion.V().control(tb).otro(lyNombre).control(self.grid)

        self.setLayout(layout)
        self.restore_video()

    def grid_num_datos(self, grid):
        return len(self.liBloques)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        bloque = self.liBloques[row]
        if key == "NOMBRE":
            return bloque.tr_name
        return bloque.pgn

    def grid_doble_click(self, grid, fil, col):
        self.modificar()

    def leeBloques(self, li_pv):
        li = []
        for pv in li_pv:
            p = Game.Game()
            p.read_pv(pv)
            p.assign_opening()
            ap = p.opening
            if ap is None:
                ap = OpeningsStd.OpeningsStd(_("Unknown"))
                ap.a1h8 = pv
            else:
                ap.a1h8 = pv
                ap.pgn = ap.pgn.replace(". ", ".")
                nap = len(ap.pgn)
                pgn_translated = p.pgn_translated()
                if len(pgn_translated) > nap:
                    ap.tr_name += " + %s" % (pgn_translated[nap + 1 :],)
            ap.pgn = p.pgn_translated()
            li.append(ap)
        return li

    def nueva(self):
        bloque = self.edit(None)
        if bloque:
            self.liBloques.append(bloque)
            if not self.edNombre.texto().strip():
                self.edNombre.set_text(bloque.tr_name)
            self.grid.refresh()
            self.grid.gobottom()

    def modificar(self):
        row = self.grid.recno()
        if row >= 0:
            bloque = self.liBloques[row]
            bloque = self.edit(bloque)
            if bloque:
                self.liBloques[row] = bloque
                self.grid.refresh()

    def edit(self, bloque):
        me = QTUtil2.unMomento(self)
        w = WOpenings(self, Code.configuration, bloque)
        me.final()
        if w.exec_():
            return w.resultado()
        return None

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            bloque = self.liBloques[row]
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), bloque.tr_name)):
                del self.liBloques[row]
                self.grid.refresh()

    def aceptar(self):
        if not self.liBloques:
            QTUtil2.message_error(self, _("you have not indicated any opening"))
            return

        self.name = self.edNombre.texto().strip()
        if not self.name:
            if len(self.liBloques) == 1:
                self.name = self.liBloques[0].tr_name
            else:
                QTUtil2.message_error(self, _("Not indicated the name of training"))
                return

        self.accept()

    def cancelar(self):
        self.reject()

    def listaPV(self):
        li = []
        for bloque in self.liBloques:
            li.append(bloque.a1h8)
        return li


class OpeningsPersonales(LCDialog.LCDialog):
    def __init__(self, procesador, owner=None):

        self.procesador = procesador
        self.ficheroDatos = procesador.configuration.file_pers_openings()
        self.lista = self.leer()

        if owner is None:
            owner = procesador.main_window
        icono = Iconos.Opening()
        titulo = _("Custom openings")
        extparam = "customopen"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb.new(_("New"), Iconos.TutorialesCrear(), self.nuevo)
        tb.new(_("Modify"), Iconos.Modificar(), self.modificar)
        tb.new(_("Remove"), Iconos.Borrar(), self.borrar)
        tb.new(_("Copy"), Iconos.Copiar(), self.copiar)
        tb.new(_("Up"), Iconos.Arriba(), self.arriba)
        tb.new(_("Down"), Iconos.Abajo(), self.abajo)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NOMBRE", _("Name"), 240)
        o_columns.nueva("ECO", "ECO", 70, centered=True)
        o_columns.nueva("PGN", "PGN", 280)
        o_columns.nueva("ESTANDAR", _("Add to standard list"), 120, centered=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        n = self.grid.anchoColumnas()
        self.grid.setMinimumWidth(n + 20)
        self.register_grid(self.grid)
        self.grid.gotop()

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(8)
        self.setLayout(layout)

        self.restore_video(siTam=True)

        self.dicPGNSP = {}

    def terminar(self):
        self.save_video()
        self.reject()
        return

    def grid_num_datos(self, grid):
        return len(self.lista)

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        reg = self.lista[row]
        if key == "ESTANDAR":
            return _("Yes") if reg["ESTANDAR"] else _("No")
        elif key == "PGN":
            pgn = reg["PGN"]
            if not (pgn in self.dicPGNSP):
                p = Game.Game()
                p.read_pv(reg["A1H8"])
                self.dicPGNSP[pgn] = p.pgn_translated()
            return self.dicPGNSP[pgn]
        return reg[key]

    def grid_doble_click(self, grid, fil, col):
        self.edit(fil)

    def grid_doubleclick_header(self, grid, o_column):
        key = o_column.key

        li = sorted(self.lista, key=lambda x: x[key].upper())

        self.lista = li

        self.grid.refresh()
        self.grid.gotop()

        self.grabar()

    def edit(self, row):

        if row is None:
            name = ""
            eco = ""
            pgn = ""
            estandar = True
            titulo = _("New opening")

        else:
            reg = self.lista[row]

            name = reg["NOMBRE"]
            eco = reg["ECO"]
            pgn = reg["PGN"]
            estandar = reg["ESTANDAR"]

            titulo = name

        # Datos
        li_gen = [(None, None)]
        li_gen.append((_("Name") + ":", name))
        config = FormLayout.Editbox("ECO", ancho=30, rx="[A-Z, a-z][0-9][0-9]")
        li_gen.append((config, eco))
        li_gen.append((_("Add to standard list") + ":", estandar))

        # Editamos
        resultado = FormLayout.fedit(li_gen, title=titulo, parent=self, anchoMinimo=460, icon=Iconos.Opening())
        if resultado is None:
            return

        accion, liResp = resultado
        name = liResp[0].strip()
        if not name:
            return
        eco = liResp[1].upper()
        estandar = liResp[2]

        self.procesador.procesador = self.procesador  # ya que edit_variation espera un manager

        if pgn:
            ok, game = Game.pgn_game(pgn)
            if not ok:
                game = Game.Game()
        else:
            game = Game.Game()

        resp = Variations.edit_variation(self.procesador, game, titulo=name, is_white_bottom=True)

        if resp:
            game = resp

            reg = {}
            reg["NOMBRE"] = name
            reg["ECO"] = eco
            reg["PGN"] = game.pgnBaseRAW()
            reg["A1H8"] = game.pv()
            reg["ESTANDAR"] = estandar

            if row is None:
                self.lista.append(reg)
                self.grid.refresh()
                self.grabar()
            else:
                self.lista[row] = reg
            self.grid.refresh()
            self.grabar()

    def nuevo(self):
        self.edit(None)

    def modificar(self):
        recno = self.grid.recno()
        if recno >= 0:
            self.edit(recno)

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            if QTUtil2.pregunta(self, _X(_("Do you want to delete the opening %1?"), self.lista[row]["NOMBRE"])):
                del self.lista[row]
                self.grid.refresh()
                self.grabar()

    def copiar(self):
        row = self.grid.recno()
        if row >= 0:
            reg = self.lista[row]
            nreg = copy.deepcopy(reg)
            self.lista.append(nreg)
            self.grid.refresh()
            self.grabar()

    def leer(self):
        lista = Util.restore_pickle(self.ficheroDatos)
        if lista is None:
            lista = []

        return lista

    def grabar(self):
        Util.save_pickle(self.ficheroDatos, self.lista)

    def arriba(self):
        row = self.grid.recno()
        if row > 0:
            self.lista[row - 1], self.lista[row] = self.lista[row], self.lista[row - 1]
            self.grid.goto(row - 1, 0)
            self.grid.refresh()
            self.grid.setFocus()
            self.grabar()

    def abajo(self):
        row = self.grid.recno()
        if 0 <= row < (len(self.lista) - 1):
            self.lista[row + 1], self.lista[row] = self.lista[row], self.lista[row + 1]
            self.grid.goto(row + 1, 0)
            self.grid.refresh()
            self.grid.setFocus()
            self.grabar()
