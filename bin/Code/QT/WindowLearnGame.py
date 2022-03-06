import time

from PySide2 import QtWidgets, QtCore

from Code import Util
from Code.Base import Game
from Code.Board import Board
from Code.Translations import TrListas
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL
from Code.QT import LCDialog

from Code.Databases import WindowDatabase


class DBLearnGame(UtilSQL.DictSQL):
    def __init__(self, file):
        UtilSQL.DictSQL.__init__(self, file)
        self.regKeys = self.keys(True, True)

    def leeRegistro(self, num):
        return self.__getitem__(self.regKeys[num])

    def append(self, valor):
        k = str(Util.today())
        self.__setitem__(k, valor)
        self.regKeys = self.keys(True, True)

    def cambiaRegistro(self, num, valor):
        self.__setitem__(self.regKeys[num], valor)

    def remove_list(self, li):
        li.sort()
        li.reverse()
        for x in li:
            self.__delitem__(self.regKeys[x])
        self.pack()
        self.regKeys = self.keys(True, True)


class WLearnBase(LCDialog.LCDialog):
    def __init__(self, procesador):

        titulo = _("Memorize a game")
        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, Iconos.LearnGame(), "learngame")

        self.procesador = procesador
        self.configuration = procesador.configuration

        self.db = DBLearnGame(self.configuration.file_learn_game())

        self.cache = {}

        o_columns = Columnas.ListaColumnas()

        def crea_col(key, label, centered=True):
            o_columns.nueva(key, label, 80, centered=centered)

        # # Claves segun orden estandar
        liBasic = ("EVENT", "SITE", "DATE", "ROUND", "WHITE", "BLACK", "RESULT", "ECO", "FEN", "WHITEELO", "BLACKELO")
        for key in liBasic:
            label = TrListas.pgnLabel(key)
            crea_col(key, label, key != "EVENT")
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("New"), Iconos.Nuevo(), self.nuevo),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Up"), Iconos.Arriba(), self.tw_up),
            None,
            (_("Down"), Iconos.Abajo(), self.tw_down),
            None,
            (_("Learn"), Iconos.Empezar(), self.empezar),
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        # Colocamos
        lyTB = Colocacion.H().control(self.tb).margen(0)
        ly = Colocacion.V().otro(lyTB).control(self.grid).margen(3)

        self.setLayout(ly)

        self.register_grid(self.grid)
        self.restore_video(siTam=False)

        self.grid.gotop()

    def grid_doble_click(self, grid, row, column):
        self.empezar()

    def grid_num_datos(self, grid):
        return len(self.db)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        if row in self.cache:
            game = self.cache[row]
        else:
            reg = self.db.leeRegistro(row)
            game = Game.Game()
            game.restore(reg["GAME"])
            self.cache[row] = game
        return game.get_tag(col)

    def terminar(self):
        self.save_video()
        self.db.close()
        self.accept()

    def nuevo(self):
        menu = QTVarios.LCMenu(self)
        if not QTVarios.lista_db(self.configuration, True).is_empty():
            menu.opcion("db", _("Game in a database"), Iconos.Database())
            menu.separador()
        menu.opcion("pgn", _("Game in a pgn"), Iconos.Filtrar())
        menu.separador()
        resp = menu.lanza()
        game = None
        if resp == "pgn":
            game = self.procesador.select_1_pgn(self)
        elif resp == "db":
            db = QTVarios.select_db(self, self.configuration, True, False)
            if db:
                w = WindowDatabase.WBDatabase(self, self.procesador, db, False, True)
                resp = w.exec_()
                if resp:
                    game = w.game
        if game and len(game) > 0:
            reg = {"GAME": game.save()}
            self.db.append(reg)
            self.cache = {}
            self.grid.refresh()
            self.grid.gotop()

    def borrar(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                self.db.remove_list(li)
        self.cache = {}
        self.grid.gotop()
        self.grid.refresh()

    def empezar(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            w = WLearn1(self, li[0])
            w.exec_()

    def tw_up(self):
        recno = self.grid.recno()
        if 0 < recno < len(self.db):
            r0 = recno
            r1 = recno-1
            reg0 = self.db.leeRegistro(r0)
            reg1 = self.db.leeRegistro(r1)
            self.db.cambiaRegistro(r0, reg1)
            self.db.cambiaRegistro(r1, reg0)
            if r0 in self.cache and r1 in self.cache:
                self.cache[r0], self.cache[r1] = self.cache[r1], self.cache[r0]
            else:
                if r0 in self.cache:
                    del self.cache[r0]
                if r1 in self.cache:
                    del self.cache[r1]
            self.grid.refresh()
            self.grid.goto(r1, 0)

    def tw_down(self):
        recno = self.grid.recno()
        if 0 <= recno < len(self.db)-1:
            r0 = recno
            r1 = recno+1
            reg0 = self.db.leeRegistro(r0)
            reg1 = self.db.leeRegistro(r1)
            self.db.cambiaRegistro(r0, reg1)
            self.db.cambiaRegistro(r1, reg0)
            if r0 in self.cache and r1 in self.cache:
                self.cache[r0], self.cache[r1] = self.cache[r1], self.cache[r0]
            else:
                if r0 in self.cache:
                    del self.cache[r0]
                if r1 in self.cache:
                    del self.cache[r1]
            self.grid.refresh()
            self.grid.goto(r1, 0)


class WLearn1(LCDialog.LCDialog):
    def __init__(self, owner, numRegistro):

        LCDialog.LCDialog.__init__(self, owner, _("Learn a game"), Iconos.PGN(), "learn1game")

        self.owner = owner
        self.db = owner.db
        self.procesador = owner.procesador
        self.configuration = self.procesador.configuration
        self.numRegistro = numRegistro
        self.registro = self.db.leeRegistro(numRegistro)

        self.game = Game.Game()
        self.game.restore(self.registro["GAME"])

        self.lbRotulo = Controles.LB(self, self.label()).ponTipoLetra(puntos=12).set_foreground_backgound("#076C9F", "#EFEFEF")

        self.liIntentos = self.registro.get("LIINTENTOS", [])

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("DATE", _("Date"), 100, centered=True)
        o_columns.nueva("LEVEL", _("Level"), 80, centered=True)
        o_columns.nueva("COLOR", _("Side you play with"), 80, centered=True)
        o_columns.nueva("ERRORS", _("Errors"), 80, centered=True)
        o_columns.nueva("HINTS", _("Hints"), 80, centered=True)
        o_columns.nueva("TIME", _("Time"), 80, centered=True)
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)

        # Tool bar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Train"), Iconos.Empezar(), self.empezar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        # Colocamos
        lyTB = Colocacion.H().control(self.tb).margen(0)
        ly = Colocacion.V().otro(lyTB).control(self.grid).control(self.lbRotulo).margen(3)

        self.setLayout(ly)

        self.register_grid(self.grid)
        self.restore_video(siTam=False)

        self.grid.gotop()

    def label(self):
        r = self.registro

        def x(k):
            return r.get(k, "")

        return "%s-%s : %s %s %s" % (x("WHITE"), x("BLACK"), x("DATE"), x("EVENT"), x("SITE"))

    def grid_num_datos(self, grid):
        return len(self.liIntentos)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        reg = self.liIntentos[row]

        if col == "DATE":
            f = reg["DATE"]
            return "%02d/%02d/%d-%02d:%02d" % (f.day, f.month, f.year, f.hour, f.minute)
        if col == "LEVEL":
            return str(reg["LEVEL"])
        if col == "COLOR":
            c = reg["COLOR"]
            if c == "b":
                return _("Black")
            elif c == "w":
                return _("White")
            else:
                return _("White") + "+" + _("Black")
        if col == "ERRORS":
            return str(reg["ERRORS"])
        if col == "HINTS":
            return str(reg["HINTS"])
        if col == "TIME":
            s = reg["SECONDS"]
            m = s // 60
            s -= m * 60
            return "%2d' %02d\"" % (m, s)

    def guardar(self, dic):
        self.liIntentos.insert(0, dic)
        self.grid.refresh()
        self.grid.gotop()
        self.registro["LIINTENTOS"] = self.liIntentos
        self.db.cambiaRegistro(self.numRegistro, self.registro)

    def terminar(self):
        self.save_video()
        self.accept()

    def borrar(self):
        li = self.grid.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                li.sort()
                li.reverse()
                for x in li:
                    del self.liIntentos[x]
        self.grid.gotop()
        self.grid.refresh()

    def empezar(self):
        regBase = self.liIntentos[0] if self.liIntentos else {}

        li_gen = [(None, None)]

        dic = self.configuration.read_variables("MEMORIZING_GAME")

        li_gen.append((FormLayout.Spinbox(_("Level"), 0, len(self.game), 40), regBase.get("LEVEL", 0)))
        li_gen.append((None, None))
        li_gen.append((None, _("Side you play with") + ":"))
        li_gen.append((_("White"), "w" in regBase.get("COLOR", "bw")))
        li_gen.append((_("Black"), "b" in regBase.get("COLOR", "bw")))
        li_gen.append((None, None))
        li_gen.append((_("Show clock"), dic.get("CLOCK", True)))

        resultado = FormLayout.fedit(li_gen, title=_("New try"), anchoMinimo=200, parent=self, icon=Iconos.TutorialesCrear())
        if resultado is None:
            return

        accion, liResp = resultado
        level = liResp[0]
        white = liResp[1]
        black = liResp[2]
        if not (white or black):
            return
        siClock = liResp[3]

        dic["CLOCK"] = siClock
        self.configuration.write_variables("MEMORIZING_GAME", dic)

        w = WLearnPuente(self, self.game, level, white, black, siClock)
        w.exec_()


class WLearnPuente(LCDialog.LCDialog):
    INICIO, FINAL_JUEGO, REPLAY, REPLAY_CONTINUE = range(4)

    def __init__(self, owner, game, nivel, white, black, siClock):

        LCDialog.LCDialog.__init__(self, owner, owner.label(), Iconos.PGN(), "learnpuente")

        self.owner = owner
        self.procesador = owner.procesador
        self.configuration = self.procesador.configuration
        self.game = game
        self.nivel = nivel
        self.white = white
        self.black = black
        self.siClock = siClock

        self.repTiempo = 3000
        self.repWorking = False

        # Tool bar
        self.tb = QTVarios.LCTB(self, [])

        self.pon_toolbar(self.INICIO)

        # Boards
        config_board = self.configuration.config_board("LEARNPGN", 48)

        self.boardIni = Board.Board(self, config_board)
        self.boardIni.crea()
        self.boardIni.set_dispatcher(self.player_has_moved, None)
        self.lbIni = Controles.LB(self).align_center().set_foreground_backgound("#076C9F", "#EFEFEF").anchoMinimo(self.boardIni.ancho)
        lyIni = Colocacion.V().control(self.boardIni).control(self.lbIni)

        self.boardFin = Board.BoardEstatico(self, config_board)
        self.boardFin.crea()
        self.lbFin = Controles.LB(self).align_center().set_foreground_backgound("#076C9F", "#EFEFEF").anchoMinimo(self.boardFin.ancho)
        lyFin = Colocacion.V().control(self.boardFin).control(self.lbFin)

        # Rotulo vtime
        f = Controles.TipoLetra(puntos=30, peso=75)
        self.lbReloj = (
            Controles.LB(self, "00:00").ponFuente(f).align_center().set_foreground_backgound("#076C9F", "#EFEFEF").anchoMinimo(200)
        )
        self.lbReloj.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)

        # Movimientos
        flb = Controles.TipoLetra(puntos=11)
        self.lbInfo = Controles.LB(self).anchoFijo(200).set_wrap().ponFuente(flb)

        # Layout
        lyC = Colocacion.V().control(self.lbReloj).control(self.lbInfo).relleno()
        lyTM = Colocacion.H().otro(lyIni).otro(lyC).otro(lyFin).relleno()

        ly = Colocacion.V().control(self.tb).otro(lyTM).relleno().margen(3)

        self.setLayout(ly)

        self.restore_video()
        self.adjustSize()

        self.working_clock = siClock
        if siClock:
            QtCore.QTimer.singleShot(500, self.ajustaReloj)
        else:
            self.lbReloj.hide()

        self.reset()

    def process_toolbar(self):
        getattr(self, self.sender().key)()

    def pon_toolbar(self, tipo):

        if tipo == self.INICIO:
            li_acciones = (
                (_("Cancel"), Iconos.Cancelar(), self.cancelar),
                None,
                (_("Reinit"), Iconos.Reiniciar(), self.reset),
                None,
                (_("Help"), Iconos.AyudaGR(), self.ayuda),
                None,
            )
        elif tipo == self.FINAL_JUEGO:
            li_acciones = (
                (_("Close"), Iconos.MainMenu(), self.final),
                None,
                (_("Reinit"), Iconos.Reiniciar(), self.reset),
                None,
                (_("Replay game"), Iconos.Pelicula(), self.replay),
                None,
            )
        elif tipo == self.REPLAY:
            li_acciones = (
                (_("Cancel"), Iconos.Cancelar(), self.repCancelar),
                None,
                (_("Reinit"), Iconos.Inicio(), self.repReiniciar),
                None,
                (_("Slow"), Iconos.Pelicula_Lento(), self.repSlow),
                None,
                (_("Pause"), Iconos.Pelicula_Pausa(), self.repPause),
                None,
                (_("Fast"), Iconos.Pelicula_Rapido(), self.repFast),
                None,
            )
        elif tipo == self.REPLAY_CONTINUE:
            li_acciones = (
                (_("Cancel"), Iconos.Cancelar(), self.repCancelar),
                None,
                (_("Continue"), Iconos.Pelicula_Seguir(), self.repContinue),
                None,
            )
        self.tb.reset(li_acciones)

    def replay(self):
        self.pon_toolbar(self.REPLAY)

        self.repJugada = -1
        self.repWorking = True
        self.boardIni.set_position(self.game.first_position)
        self.replayDispatch()

    def replayDispatch(self):
        QTUtil.refresh_gui()
        if not self.repWorking:
            return
        self.repJugada += 1
        self.ponInfo()
        num_moves = len(self.game)
        if self.repJugada == num_moves:
            self.pon_toolbar(self.FINAL_JUEGO)
            return

        move = self.game.move(self.repJugada)
        self.boardIni.set_position(move.position)
        self.boardIni.put_arrow_sc(move.from_sq, move.to_sq)
        self.lbIni.set_text("%d/%d" % (self.repJugada + 1, num_moves))

        self.boardFin.set_position(move.position)
        self.boardFin.put_arrow_sc(move.from_sq, move.to_sq)
        self.lbFin.set_text("%d/%d" % (self.repJugada + 1, num_moves))

        QtCore.QTimer.singleShot(self.repTiempo, self.replayDispatch)

    def repCancelar(self):
        self.repWorking = False
        self.pon_toolbar(self.FINAL_JUEGO)
        self.ponInfo()

    def repReiniciar(self):
        self.repJugada = -1

    def repSlow(self):
        self.repTiempo += 500

    def repFast(self):
        if self.repTiempo >= 800:
            self.repTiempo -= 500
        else:
            self.repTiempo = 200

    def repPause(self):
        self.repWorking = False
        self.pon_toolbar(self.REPLAY_CONTINUE)

    def repContinue(self):
        self.repWorking = True
        self.pon_toolbar(self.REPLAY)
        self.replayDispatch()

    def reset(self):
        self.time_base = time.time()
        self.boardIni.set_position(self.game.first_position)

        self.movActual = -1

        self.errors = 0
        self.hints = 0

        if self.siClock:
            self.working_clock = True
            QtCore.QTimer.singleShot(500, self.ajustaReloj)
            self.lbReloj.show()
        else:
            self.lbReloj.hide()

        self.pon_toolbar(self.INICIO)

        self.siguiente()

    def ponInfo(self):
        njg = self.repJugada if self.repWorking else self.movActual - 1
        txtPGN = self.game.pgn_translated(hastaJugada=njg)
        texto = "<big><center><b>%s</b>: %d<br><b>%s</b>: %d</center><br><br>%s</big>" % (
            _("Errors"),
            self.errors,
            _("Hints"),
            self.hints,
            txtPGN,
        )
        self.lbInfo.set_text(texto)

    def siguiente(self):
        num_moves = len(self.game)
        self.movActual += 1
        self.ponInfo()
        self.lbIni.set_text("%d/%d" % (self.movActual, num_moves))
        if self.movActual == num_moves:
            self.finalJuego()
            return

        move = self.game.move(self.movActual)

        self.boardIni.set_position(move.position_before)
        if self.movActual > 0:
            jgant = self.game.move(self.movActual - 1)
            self.boardIni.put_arrow_sc(jgant.from_sq, jgant.to_sq)

        mfin = self.movActual + self.nivel - 1
        if self.nivel == 0:
            mfin += 1
        if mfin >= num_moves:
            mfin = num_moves - 1

        jgf = self.game.move(mfin)
        self.boardFin.set_position(jgf.position)
        if self.nivel == 0:
            self.boardFin.put_arrow_sc(jgf.from_sq, jgf.to_sq)
        self.lbFin.set_text("%d/%d" % (mfin + 1, num_moves))

        color = move.position_before.is_white

        if (color and self.white) or (not color and self.black):
            self.boardIni.activate_side(color)
        else:
            self.siguiente()

    def player_has_moved(self, from_sq, to_sq, promotion=""):

        move = self.game.move(self.movActual)

        # Peon coronando
        if not promotion and move.position_before.siPeonCoronando(from_sq, to_sq):
            promotion = self.boardIni.peonCoronando(move.position_before.is_white)

        if from_sq == move.from_sq and to_sq == move.to_sq and promotion.lower() == move.promotion.lower():
            self.boardIni.put_arrow_sc(from_sq, to_sq)
            self.siguiente()
            return False  # Que actualice solo siguiente
        else:
            if to_sq != from_sq:
                self.errors += 1
                self.boardIni.ponFlechasTmp([(move.from_sq, move.to_sq, False)])
            self.ponInfo()
            return False

    def ayuda(self):

        move = self.game.move(self.movActual)
        self.boardIni.put_arrow_sc(move.from_sq, move.to_sq)
        self.hints += 1

        self.ponInfo()

    def guardar(self):
        color = ""
        if self.white:
            color += "w"
        if self.black:
            color += "b"
        dic = {}
        dic["SECONDS"] = time.time() - self.time_base
        dic["DATE"] = Util.today()
        dic["LEVEL"] = self.nivel
        dic["COLOR"] = color
        dic["HINTS"] = self.hints
        dic["ERRORS"] = self.errors
        self.owner.guardar(dic)

    def finalJuego(self):
        self.working_clock = False
        num_moves = len(self.game)
        self.lbIni.set_text("%d/%d" % (num_moves, num_moves))
        self.boardIni.set_position(self.game.last_position)
        self.guardar()

        self.pon_toolbar(self.FINAL_JUEGO)

    def final(self):
        self.working_clock = False
        self.save_video()
        self.accept()

    def cancelar(self):
        self.final()

    def ajustaReloj(self):
        if self.working_clock:
            s = int(time.time() - self.time_base)

            m = s // 60
            s -= m * 60

            self.lbReloj.set_text("%02d:%02d" % (m, s))
            QtCore.QTimer.singleShot(500, self.ajustaReloj)
