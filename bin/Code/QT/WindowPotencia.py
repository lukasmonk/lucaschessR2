import atexit
import datetime
import random
import time

from PySide2 import QtWidgets, QtCore, QtGui

import Code
from Code import Util
from Code.Analysis import Analysis
from Code.Base import Game, Move, Position
from Code.Board import Board2
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import Base
from Code.SQL import UtilSQL


def lee_1_linea_mfn(linea):
    cabs, pv, move = linea.strip().split("||")
    dic = Util.SymbolDict()
    for x in cabs.split("|"):
        k, v = x.split("·")
        dic[k] = v
    game = Game.Game()
    game.read_pv(pv)
    event = dic["Event"]
    site = dic["Site"]
    if site and site != event:
        event += "-%s" % site
    date = dic["Date"].replace(".?", "").replace("?", "")
    white = dic["White"]
    black = dic["Black"]
    result = dic["Result"]
    info = "<b>%s - %s (%s)</b>    %s (%s) " % (white, black, result, event, date)
    return game, dic, info, int(move), linea


def lee_linea_mfn():
    npos = random.randint(0, 9999)
    with open(Code.path_resource("IntFiles", "games.mfn"), "rt", encoding="utf-8") as f:
        for num, linea in enumerate(f):
            if num == npos:
                return lee_1_linea_mfn(linea)


def lee_varias_lineas_mfn(nlineas):  # WindowDailyTest
    lipos = random.sample(range(0, 9999), nlineas)
    lifen = []
    with open(Code.path_resource("IntFiles", "games.mfn"), "rt", encoding="utf-8") as f:
        for num, linea in enumerate(f):
            if num in lipos:
                cabs, pv, move = linea.strip().split("||")
                p = Game.Game()
                p.read_pv(pv)
                fen = p.move(int(move)).position.fen()
                lifen.append(fen)
    return lifen


class PotenciaHistorico:
    def __init__(self, file):
        self.file = file
        self.db = Base.DBBase(file)
        self.tabla = "datos"

        if not self.db.existeTabla(self.tabla):
            self.crea_tabla()

        self.dbf = self.db.dbf(self.tabla, "REF,FECHA,SCORE,ENGINE,SEGUNDOS,MIN_MIN,MIN_MAX,LINE", orden="FECHA DESC")

        if not self.dbf.existe_column("ENGINE"):
            self.dbf.add_column_varchar("ENGINE")
            if self.dbf.existe_column("MOTOR"):
                self.dbf.copy_column("MOTOR", "ENGINE")
            self.dbf.cerrar()
            self.dbf = self.db.dbf(
                self.tabla, "REF,FECHA,SCORE,ENGINE,SEGUNDOS,MIN_MIN,MIN_MAX,LINE", orden="FECHA DESC"
            )

        self.dbf.leer()

        self.orden = "FECHA", "DESC"

        atexit.register(self.close)

    def close(self):
        if self.dbf:
            self.dbf.cerrar()
            self.dbf = None
        self.db.cerrar()

    def crea_tabla(self):
        tb = Base.TablaBase(self.tabla)
        tb.nuevoCampo("FECHA", "VARCHAR", notNull=True, primaryKey=True)
        tb.nuevoCampo("REF", "INTEGER")
        tb.nuevoCampo("SCORE", "INTEGER")
        tb.nuevoCampo("ENGINE", "VARCHAR")
        tb.nuevoCampo("SEGUNDOS", "INTEGER")
        tb.nuevoCampo("MIN_MIN", "INTEGER")
        tb.nuevoCampo("MIN_MAX", "INTEGER")
        tb.nuevoCampo("LINE", "TEXT")
        tb.nuevoIndice("IND_SCORE", "SCORE")
        self.db.generarTabla(tb)

    def __len__(self):
        return self.dbf.reccount()

    def goto(self, num):
        self.dbf.goto(num)

    def pon_orden(self, key):
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

    @staticmethod
    def fecha2txt(fecha):
        return "%4d%02d%02d%02d%02d%02d" % (fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute, fecha.second)

    @staticmethod
    def txt2fecha(txt):
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

    def append(self, fecha, score, engine, seconds, min_min, min_max, linea, ref):

        br = self.dbf.baseRegistro()
        if ref is None:
            ref = self.dbf.maxCampo("REF")
            if not ref:
                ref = 1
            else:
                ref += 1
        br.REF = ref
        br.FECHA = self.fecha2txt(fecha)
        br.SCORE = score
        br.ENGINE = engine
        br.SEGUNDOS = seconds
        br.MIN_MIN = min_min
        br.MIN_MAX = min_max
        br.LINE = linea
        self.dbf.insertar(br)

    def __getitem__(self, num):
        self.dbf.goto(num)
        reg = self.dbf.registroActual()
        reg.FECHA = self.txt2fecha(reg.FECHA)
        return reg

    def borrar_lista(self, linum):
        self.dbf.remove_list_recnos(linum)
        self.dbf.pack()
        self.dbf.leer()


class EDCelda(Controles.ED):
    def focusOutEvent(self, event):
        self.parent.focusOut(self)
        Controles.ED.focusOutEvent(self, event)


class WEdMove(QtWidgets.QWidget):
    def __init__(self, owner, conj_piezas, si_blancas):
        QtWidgets.QWidget.__init__(self)

        self.owner = owner

        self.conj_piezas = conj_piezas

        self.filaPromocion = (7, 8) if si_blancas else (2, 1)

        self.menuPromocion = self.creaMenuPiezas("QRBN ", si_blancas)

        self.promocion = " "

        self.origen = (
            EDCelda(self, "")
            .caracteres(2)
            .controlrx("(|[a-h][1-8])")
            .anchoFijo(24)
            .align_center()
            .capture_changes(self.miraPromocion)
        )

        self.arrow = arrow = Controles.LB(self).ponImagen(Iconos.pmMover())

        self.destino = (
            EDCelda(self, "")
            .caracteres(2)
            .controlrx("(|[a-h][1-8])")
            .anchoFijo(24)
            .align_center()
            .capture_changes(self.miraPromocion)
        )

        self.pbPromocion = Controles.PB(self, "", self.pulsadoPromocion, plano=False).anchoFijo(24)

        ly = (
            Colocacion.H()
            .relleno()
            .control(self.origen)
            .espacio(2)
            .control(arrow)
            .espacio(2)
            .control(self.destino)
            .control(self.pbPromocion)
            .margen(0)
            .relleno()
        )
        self.setLayout(ly)

        self.miraPromocion()

    def focusOut(self, quien):
        self.owner.ponUltimaCelda(quien)

    def activa(self):
        self.setFocus()
        self.origen.setFocus()

    def activaDestino(self):
        self.setFocus()
        self.destino.setFocus()

    def resultado(self):
        from_sq = self.origen.texto()
        if len(from_sq) != 2:
            from_sq = ""

        to_sq = self.destino.texto()
        if len(to_sq) != 2:
            from_sq = ""

        return from_sq, to_sq, self.promocion.strip()

    def deshabilita(self):
        self.origen.set_disabled(True)
        self.destino.set_disabled(True)
        self.pbPromocion.setEnabled(False)
        if not self.origen.texto() or not self.destino.texto():
            self.origen.hide()
            self.destino.hide()
            self.pbPromocion.hide()
            self.arrow.hide()

    def miraPromocion(self):
        show = True
        ori, dest = self.filaPromocion
        txtO = self.origen.texto()
        if len(txtO) < 2 or int(txtO[-1]) != ori:
            show = False
        if show:
            txtD = self.destino.texto()
            if len(txtD) < 2 or int(txtD[-1]) != dest:
                show = False
        self.pbPromocion.setVisible(show)
        return show

    def pulsadoPromocion(self):
        if not self.miraPromocion():
            return
        resp = self.menuPromocion.exec_(QtGui.QCursor.pos())
        if resp is not None:
            icono = self.conj_piezas.icono(resp.key) if resp.key else QtGui.QIcon()
            self.pbPromocion.ponIcono(icono)
            self.promocion = resp.key

    def creaMenuPiezas(self, lista, is_white):
        menu = QtWidgets.QMenu(self)

        dic = {"K": _("King"), "Q": _("Queen"), "R": _("Rook"), "B": _("Bishop"), "N": _("Knight"), "P": _("Pawn")}

        for pz in lista:
            if pz == " ":
                icono = QtGui.QIcon()
                txt = _("Remove")
            else:
                txt = dic[pz]
                if not is_white:
                    pz = pz.lower()
                icono = self.conj_piezas.icono(pz)

            accion = QtWidgets.QAction(icono, txt, menu)

            accion.key = pz.strip()
            menu.addAction(accion)

        return menu


class WBlqMove(QtWidgets.QWidget):
    def __init__(self, owner, conj_piezas, is_white, position):
        QtWidgets.QWidget.__init__(self)

        self.owner = owner
        self.wm = WEdMove(self, conj_piezas, is_white)
        self.ms = Controles.LB(self, "")
        self.an = Controles.PB(self, "?", self.analizarUno, plano=False).anchoFijo(18)
        self.cancelar = Controles.LB(self, "").ponImagen(Iconos.pmCancelarPeque())
        self.aceptar = Controles.LB(self, "").ponImagen(Iconos.pmAceptarPeque())
        ly = (
            Colocacion.H()
            .control(self.aceptar)
            .control(self.cancelar)
            .control(self.wm)
            .control(self.an)
            .control(self.ms)
            .relleno()
            .margen(0)
        )
        self.setLayout(ly)

        self.ms.hide()
        self.an.hide()
        self.aceptar.hide()
        self.cancelar.hide()

        self.position = position

    def ponUltimaCelda(self, quien):
        self.owner.ponUltimaCelda(quien)

    def activa(self):
        self.setFocus()
        self.wm.activa()

    def analizarUno(self):
        self.owner.analizar(self.position)

    def deshabilita(self):
        self.wm.deshabilita()
        self.an.hide()
        self.ms.hide()
        self.aceptar.hide()
        self.cancelar.hide()

    def resultado(self):
        return self.wm.resultado()

    def set_score(self, puntos):
        self.ms.set_text("%s: %d/100" % (_("Score"), puntos))
        self.ms.show()
        self.an.show()

    def ponError(self, mensaje):
        self.ms.set_text(mensaje)
        self.ms.show()

    def siCorrecto(self, correcto):
        if correcto:
            self.aceptar.show()
        else:
            self.cancelar.show()


class WPotenciaBase(LCDialog.LCDialog):
    def __init__(self, procesador):

        LCDialog.LCDialog.__init__(
            self, procesador.main_window, _("Determine your calculating power"), Iconos.Potencia(), "potenciaBase"
        )

        self.procesador = procesador
        self.configuration = procesador.configuration

        self.historico = PotenciaHistorico(self.configuration.ficheroPotencia)

        self.engine, self.seconds, self.min_min, self.min_max = self.leeParametros()

        # Historico
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("REF", _("N."), 35, align_center=True)
        o_columns.nueva("FECHA", _("Date"), 120, align_center=True)
        o_columns.nueva("SCORE", _("Score"), 100, align_center=True)
        o_columns.nueva("ENGINE", _("Engine"), 120, align_center=True)
        o_columns.nueva("SEGUNDOS", _("Second(s)"), 80, align_center=True)
        o_columns.nueva("MIN_MIN", _("Observation time"), 100, align_center=True)
        o_columns.nueva("MIN_MAX", _("Total time"), 100, align_center=True)
        self.ghistorico = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.ghistorico.setMinimumWidth(self.ghistorico.anchoColumnas() + 20)

        # Tool bar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Start"), Iconos.Empezar(), self.empezar),
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Configuration"), Iconos.Opciones(), self.configurar),
            None,
            (_("Repeat"), Iconos.Pelicula_Repetir(), self.repetir),
            None,
        )
        self.tb = QTVarios.LCTB(self, li_acciones)
        # self.pon_toolbar([self.terminar, self.empezar, self.repetir, self.configurar, self.borrar])

        # Colocamos
        lyTB = Colocacion.H().control(self.tb).margen(0)
        ly = Colocacion.V().otro(lyTB).control(self.ghistorico).margen(3)

        self.setLayout(ly)

        self.register_grid(self.ghistorico)
        self.restore_video(siTam=False)

        self.ghistorico.gotop()

    def grid_doubleclick_header(self, grid, o_column):
        key = o_column.key
        if key in ("FECHA", "SCORE", "REF"):
            self.historico.pon_orden(key)
            self.ghistorico.gotop()
            self.ghistorico.refresh()

    def grid_doble_click(self, grid, fil, col):
        self.repetir(fil)

    def repetir(self, fil=None):
        if fil is None:
            fil = self.ghistorico.recno()
            if fil < 0:
                return
        reg = self.historico[fil]
        linea = reg.LINE
        if linea:
            w = WPotencia(self, self.engine, self.seconds, self.min_min, self.min_max, linea, reg.REF)
            w.exec_()
            self.ghistorico.gotop()
            self.ghistorico.refresh()

    def leeParametros(self):
        param = UtilSQL.DictSQL(self.configuration.ficheroPotencia, tabla="parametros")
        engine = param.get("ENGINE", "stockfish")
        seconds = param.get("SEGUNDOS", 5)
        min_min = param.get("MIN_MIN", 1)
        min_max = param.get("MIN_MAX", 5)
        param.close()

        return engine, seconds, min_min, min_max

    def grid_num_datos(self, grid):
        return len(self.historico)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        reg = self.historico[row]
        if col == "FECHA":
            return Util.localDateT(reg.FECHA)
        elif col == "SCORE":
            return str(reg.SCORE)
        elif col == "ENGINE":
            return reg.ENGINE
        elif col == "SEGUNDOS":
            return str(reg.SEGUNDOS)
        elif col == "MIN_MIN":
            return str(reg.MIN_MIN)
        elif col == "MIN_MAX":
            return str(reg.MIN_MAX)
        elif col == "REF":
            return str(reg.REF)

    def terminar(self):
        self.save_video()
        self.historico.close()
        self.reject()

    def borrar(self):
        li = self.ghistorico.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                self.historico.borrar_lista(li)
        self.ghistorico.gotop()
        self.ghistorico.refresh()

    def configurar(self):
        # Datos
        li_gen = [(None, None)]

        # # Motor
        mt = self.configuration.tutor_default if self.engine is None else self.engine

        li_combo = [mt]
        for name, key in self.configuration.combo_engines_multipv10():
            li_combo.append((key, name))

        li_gen.append((_("Engine") + ":", li_combo))

        # # Segundos a pensar el tutor
        config = FormLayout.Spinbox(_("Duration of engine analysis (secs)"), 1, 99, 50)
        li_gen.append((config, self.seconds))

        # Minutos
        config = FormLayout.Spinbox(_("Observation time in minutes"), 0, 99, 50)
        li_gen.append((config, self.min_min))

        config = FormLayout.Spinbox(_("Total time (observation + resolution) in minutes"), 0, 99, 50)
        li_gen.append((config, self.min_max))

        # Editamos
        resultado = FormLayout.fedit(li_gen, title=_("Configuration"), parent=self, icon=Iconos.Opciones())
        if resultado:
            accion, li_resp = resultado
            self.engine = li_resp[0]
            self.seconds = li_resp[1]
            self.min_min = li_resp[2]
            self.min_max = li_resp[3]

            param = UtilSQL.DictSQL(self.configuration.ficheroPotencia, tabla="parametros")
            param["ENGINE"] = self.engine
            param["SEGUNDOS"] = self.seconds
            param["MIN_MIN"] = self.min_min
            param["MIN_MAX"] = self.min_max
            param.close()

            # def pon_toolbar(self, li_acciones):

            # self.tb.clear()
            # for k in li_acciones:
            # self.tb.dic_toolbar[k].setVisible(True)
            # self.tb.dic_toolbar[k].setEnabled(True)
            # self.tb.addAction(self.tb.dic_toolbar[k])

            # self.tb.li_acciones = li_acciones
            # self.tb.update()

    def empezar(self):
        w = WPotencia(self, self.engine, self.seconds, self.min_min, self.min_max)
        w.exec_()
        self.ghistorico.gotop()
        self.ghistorico.refresh()


class WPotencia(LCDialog.LCDialog):
    def __init__(self, owner, engine, seconds, min_min, min_max, linea=None, ref=None):

        super(WPotencia, self).__init__(owner, _("Determine your calculating power"), Iconos.Potencia(), "potencia")

        self.game, self.dicPGN, info, self.jugadaInicial, self.linea = (
            lee_1_linea_mfn(linea) if linea else lee_linea_mfn()
        )
        self.fen = self.game.move(self.jugadaInicial).position.fen()
        self.ref = ref

        self.historico = owner.historico
        self.procesador = owner.procesador
        self.configuration = self.procesador.configuration

        if engine.startswith("*"):
            engine = engine[1:]
        confMotor = self.configuration.buscaTutor(engine)
        self.xtutor = self.procesador.creaManagerMotor(confMotor, seconds * 1000, None)
        self.xtutor.maximize_multipv()

        # Board
        config_board = self.configuration.config_board("POTENCIA", 48)

        self.min_min = min_min
        self.min_max = min_max

        cp = self.game.move(self.jugadaInicial).position

        self.board = Board2.BoardEstatico(self, config_board)
        self.board.crea()
        self.board.set_side_bottom(cp.is_white)
        self.board.set_position(cp)

        # Rotulo informacion
        self.lbInformacion = self.creaLBInformacion(info, cp)

        # Consultar la game
        self.btConsultar = Controles.PB(self, _("Show game"), self.consultar, plano=False)

        # Rotulo vtime
        self.lbTiempo = Controles.LB(self, "").align_center()

        self.liwm = []
        conj_piezas = self.board.piezas
        is_white = cp.is_white
        for i in range(12):
            wm = WBlqMove(self, conj_piezas, is_white, i)
            self.liwm.append(wm)
            is_white = not is_white

        # Tool bar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            (_("Verify"), Iconos.Check(), self.comprobar),
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        # Layout
        lyInfo = Colocacion.H().relleno().control(self.lbInformacion).control(self.btConsultar).relleno()
        lyT = Colocacion.V().relleno().control(self.board).otro(lyInfo).controlc(self.lbTiempo).relleno()

        lyV = Colocacion.V()
        for wm in self.liwm:
            lyV.control(wm)
        lyV.relleno()
        f = Controles.FontType(puntos=10, peso=75)
        self.gbMovs = Controles.GB(self, _("Next moves"), lyV).set_font(f)

        lyTV = Colocacion.H().otro(lyT).control(self.gbMovs).relleno()

        ly = Colocacion.V().control(self.tb).otro(lyTV).relleno()

        self.setLayout(ly)

        self.restore_video()
        self.adjustSize()

        liTB = [self.cancelar]

        # Tiempo
        self.timer = None
        if min_min or min_max:
            self.time_base = time.time()
            if min_min:
                self.gbMovs.hide()
                self.start_clock(self.pensandoHastaMin)
            else:
                liTB.insert(0, self.comprobar)
                self.start_clock(self.pensandoHastaMax)

        self.pon_toolbar(liTB)

        self.liwm[0].activa()

        self.btConsultar.hide()

        self.ultimaCelda = None

    def consultar(self):
        self.procesador.manager_game(self, self.game, False, True, self.board)

    def pulsada_celda(self, celda):
        if self.ultimaCelda:
            self.ultimaCelda.set_text(celda)

            ucld = self.ultimaCelda
            for num, blq in enumerate(self.liwm):
                wm = blq.wm
                if wm.origen == ucld:
                    wm.miraPromocion()
                    wm.activaDestino()
                    self.ultimaCelda = wm.destino
                    return
                elif wm.destino == ucld:
                    wm.miraPromocion()
                    if num < (len(self.liwm) - 1):
                        x = num + 1
                    else:
                        x = 0
                    blq = self.liwm[x]
                    wm = blq.wm
                    wm.activa()
                    self.ultimaCelda = wm.origen
                    return

    def ponUltimaCelda(self, wmcelda):
        self.ultimaCelda = wmcelda

    def pensandoHastaMin(self):
        dif = self.min_min * 60 - int(time.time() - self.time_base)
        if dif <= 0:
            self.pon_toolbar([self.comprobar, self.cancelar])
            self.stop_clock()
            if self.min_max:
                self.gbMovs.show()
                self.liwm[0].activa()
                self.time_base = time.time()
                self.start_clock(self.pensandoHastaMax)
        else:
            self.lbTiempo.set_text(_X(_("%1 seconds remain to think moves before you can indicate them"), str(dif)))

    def pensandoHastaMax(self):
        dif = (self.min_max - self.min_min) * 60 - int(time.time() - self.time_base)
        if dif <= 0:
            self.stop_clock()
            self.comprobar()
        else:
            self.lbTiempo.set_text(_X(_("%1 seconds remain to indicate moves"), str(dif)))

    def start_clock(self, enlace, transicion=1000):
        if self.timer is not None:
            self.timer.stop()

        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), enlace)
        self.timer.start(transicion)

    def stop_clock(self):
        self.lbTiempo.set_text("")
        if self.timer is not None:
            self.timer.stop()
            del self.timer
            self.timer = None

    def closeEvent(self, event):
        self.stop_clock()
        self.save_video()
        event.accept()

    def terminar(self):
        self.stop_clock()
        self.save_video()
        self.reject()

    def cancelar(self):
        self.terminar()

    def comprobar(self):
        self.stop_clock()
        self.pon_toolbar([self.cancelar])
        for wm in self.liwm:
            wm.deshabilita()

        um = QTUtil2.analizando(self)

        self.li_analysis = []
        cp = Position.Position()
        cp.read_fen(self.fen)
        siError = False
        totalPuntos = 0
        factor = 1
        previo = 100
        for wm in self.liwm:
            from_sq, to_sq, promotion = wm.resultado()
            if from_sq:
                cpNue = cp.copia()
                ok, mensaje = cpNue.play(from_sq, to_sq, promotion)
                wm.siCorrecto(ok)
                if not ok:
                    wm.ponError(_("Invalid move"))
                    siError = True
                    break
                move = Move.Move(None, cp, cpNue, from_sq, to_sq, promotion)
                mrm, pos = self.xtutor.analysis_move(move, self.xtutor.mstime_engine)
                move.analysis = mrm, pos

                self.li_analysis.append(move)

                rm = mrm.li_rm[pos]
                rj = mrm.li_rm[0]
                dif = rj.centipawns_abs() - rm.centipawns_abs()
                if dif >= 100:
                    puntos = 0
                else:
                    puntos = 100 - dif
                wm.set_score(puntos)
                cp = cpNue
                totalPuntos += int(puntos * factor * previo / 100)
                previo = puntos * previo / 100
                factor *= 2
            else:
                break

        um.final()
        self.btConsultar.show()

        if not siError:
            self.lbTiempo.set_text("<h2>%s: %d %s</h2>" % (_("Result"), totalPuntos, _("pts")))

            self.historico.append(
                Util.today(),
                totalPuntos,
                self.xtutor.key,
                int(self.xtutor.mstime_engine / 1000),
                self.min_min,
                self.min_max,
                self.linea,
                self.ref,
            )

            self.pon_toolbar([self.terminar])

    def pon_toolbar(self, li_acciones):
        self.tb.clear()
        for k in li_acciones:
            self.tb.dic_toolbar[k].setVisible(True)
            self.tb.dic_toolbar[k].setEnabled(True)
            self.tb.addAction(self.tb.dic_toolbar[k])

        self.tb.li_acciones = li_acciones
        self.tb.update()

    def creaLBInformacion(self, info, cp):
        color, colorR = _("White"), _("Black")
        cK, cQ, cKR, cQR = "K", "Q", "k", "q"

        mens = ""

        if cp.castles:

            def menr(ck, cq):
                enr = ""
                if ck in cp.castles:
                    enr += "O-O"
                if cq in cp.castles:
                    if enr:
                        enr += "  +  "
                    enr += "O-O-O"
                return enr

            enr = menr(cK, cQ)
            if enr:
                mens += "  %s : %s" % (color, enr)
            enr = menr(cKR, cQR)
            if enr:
                mens += " %s : %s" % (colorR, enr)
        if cp.en_passant != "-":
            mens += "     %s : %s" % (_("En passant"), cp.en_passant)

        if mens:
            mens = "<b>%s</b><br>" % mens
        mens += info

        mens = "<center>%s</center>" % mens

        return Controles.LB(self, mens)

    def analizar(self, position):

        move = self.li_analysis[position]
        is_white = move.position_before.is_white
        Analysis.show_analysis(self.procesador, self.xtutor, move, is_white, 1, main_window=self, must_save=False)


def windowPotencia(procesador):
    w = WPotenciaBase(procesador)
    w.exec_()
