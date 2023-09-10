import time

from PySide2 import QtCore

from Code import ControlPGN
from Code import Util
from Code.Analysis import Analysis
from Code.Base import Game, Position
from Code.Base.Constantes import GT_BMT, GO_BACK, GO_END, GO_FORWARD, GO_START
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2


class WTrainBMT(LCDialog.LCDialog):
    def __init__(self, owner, dbf):

        # Variables
        self.procesador = owner.procesador
        self.configuration = owner.configuration

        self.iniTiempo = None
        self.antTxtSegundos = ""

        dic_var = self.configuration.read_variables("BMT_OPTIONS")

        self.pts_tolerance = dic_var.get("PTS_TOLERANCE", 0)

        self.game = Game.Game()
        self.siMostrarPGN = False

        self.position = Position.Position()
        self.actualP = 0  # Posicion actual

        self.game_type = GT_BMT
        self.controlPGN = ControlPGN.ControlPGN(self)

        self.state = None  # compatibilidad con ControlPGN
        self.human_is_playing = False  # compatibilidad con ControlPGN
        self.borrar_fen_lista = set()

        # Datos ----------------------------------------------------------------
        self.dbf = dbf
        self.recnoActual = self.dbf.recno
        self.bmt_lista = Util.zip2var_change_import(
            dbf.leeOtroCampo(self.recnoActual, "BMT_LISTA"), b"Code.BMT", b"Code.TrainBMT.BMT"
        )
        self.bmt_lista.patch()
        self.bmt_lista.check_color()
        self.historial = Util.zip2var(dbf.leeOtroCampo(self.recnoActual, "HISTORIAL"))
        self.siTerminadaAntes = self.is_finished = self.bmt_lista.is_finished()
        self.timer = None
        self.datosInicio = self.bmt_lista.calc_thpse()

        # Dialogo ---------------------------------------------------------------
        icono = Iconos.BMT()
        titulo = dbf.NOMBRE
        extparam = "bmtentrenar"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        # Juegan ---------------------------------------------------------------
        self.lbJuegan = Controles.LB(self, "").set_foreground_backgound("white", "black").align_center()

        # Board ---------------------------------------------------------------
        config_board = self.configuration.config_board("BMT", 32)

        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_dispatcher(self.player_has_moved)
        self.board.dbvisual_set_show_always(False)

        # Info -------------------------------------------------------------------
        colorFondo = QTUtil.qtColor(config_board.colorNegras())
        self.trPuntos = "<big><b>" + _("Score") + "<br>%s</b></big>"
        self.trSegundos = "<big><b>" + _("Time") + "<br>%s</b></big>"
        self.lbPuntos = Controles.LB(self, "").set_color_background(colorFondo).align_center().anchoMinimo(80)
        self.lbSegundos = Controles.LB(self, "").set_color_background(colorFondo).align_center().anchoMinimo(80)
        self.texto_lbPrimera = _("* indicates actual move played in game")
        self.ptsMejor = 0
        self.ptsPrimero = 0
        self.lbPrimera = Controles.LB(self, self.texto_lbPrimera)
        f = Controles.TipoLetra(puntos=8)
        self.lb_conditions = Controles.LB(self, "").ponFuente(f)
        self.lb_game = Controles.LB(self, "").ponFuente(f)

        # Grid-PGN ---------------------------------------------------------------
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMBER", _("N."), 35, align_center=True)
        with_figurines = self.configuration.x_pgn_withfigurines
        o_columns.nueva("WHITE", _("White"), 100, edicion=Delegados.EtiquetaPGN(True if with_figurines else None))
        o_columns.nueva("BLACK", _("Black"), 100, edicion=Delegados.EtiquetaPGN(False if with_figurines else None))
        self.pgn = Grid.Grid(self, o_columns, siCabeceraMovible=False)
        nAnchoPgn = self.pgn.anchoColumnas() + 20
        self.pgn.setMinimumWidth(nAnchoPgn)

        self.pgn.setVisible(False)

        # BT posiciones ---------------------------------------------------------------
        self.liBT = []
        nSalto = (self.board.ancho + 34) // 26
        self.dicIconos = {
            0: Iconos.PuntoBlanco(),
            1: Iconos.PuntoNegro(),
            2: Iconos.PuntoAmarillo(),
            3: Iconos.PuntoNaranja(),
            4: Iconos.PuntoVerde(),
            5: Iconos.PuntoAzul(),
            6: Iconos.PuntoMagenta(),
            7: Iconos.PuntoRojo(),
            8: Iconos.PuntoEstrella(),
        }
        nfila = 0
        ncolumna = 0
        lyBT = Colocacion.G()
        number = 0
        nposic = len(self.bmt_lista)
        for bmt_lista in range(nposic):
            bt = Controles.PB(self, str(bmt_lista + 1), rutina=self.number).anchoFijo(36) #.altoFijo(20)
            bt.number = number
            number += 1
            estado = self.bmt_lista.state(bmt_lista)
            bt.ponIcono(self.dicIconos[estado])
            self.liBT.append(bt)

            lyBT.controlc(bt, nfila, ncolumna)
            nfila += 1
            if nfila == nSalto:
                ncolumna += 1
                nfila = 0
        # if ncolumna == 0:
        lyBT = Colocacion.V().otro(lyBT).relleno()

        gbBT = Controles.GB(self, _("Positions"), lyBT)

        # Lista de RM max 16 ---------------------------------------------------------------
        self.liBTrm = []
        nfila = 0
        ncolumna = 0
        lyRM = Colocacion.G()
        number = 0
        for bmt_lista in range(16):
            btRM = Controles.PB(self, "", rutina=self.pulsadoRM).anchoFijo(180).altoFijo(24).ponPlano(True)
            btRM.number = number
            btRM.setEnabled(False)
            number += 1
            self.liBTrm.append(btRM)
            lyRM.controlc(btRM, nfila, ncolumna)
            ncolumna += 1
            if ncolumna == 2:
                nfila += 1
                ncolumna = 0

        self.gbRM = Controles.GB(self, _("Moves"), lyRM)

        # Tool bar ---------------------------------------------------------------
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), "terminar"),
            (_("Repeat"), Iconos.Pelicula_Repetir(), "repetir"),
            (_("Resign"), Iconos.Abandonar(), "abandonar"),
            (_("Remove"), Iconos.Borrar(), "borrar"),
            (_("Options"), Iconos.Opciones(), "opciones"),
            (_("Start"), Iconos.Empezar(), "empezar"),
            (_("Actual game"), Iconos.PartidaOriginal(), "original"),
            (_("Next"), Iconos.Siguiente(), "seguir"),
        )
        self.tb = Controles.TB(self, li_acciones)

        self.restore_video(siTam=False)

        # Colocamos ---------------------------------------------------------------
        lyPS = Colocacion.H().relleno().control(self.lbPuntos).relleno(2).control(self.lbSegundos).relleno()
        lyV = Colocacion.V().otro(lyPS).control(self.pgn).control(self.gbRM).control(self.lbPrimera)
        lyT = (
            Colocacion.V()
            .control(self.lbJuegan)
            .control(self.board)
            .control(self.lb_conditions)
            .control(self.lb_game)
            .relleno()
        )
        lyTV = Colocacion.H().otro(lyT).otro(lyV).control(gbBT).margen(5)
        ly = Colocacion.V().control(self.tb).otro(lyTV).margen(2).relleno()

        self.setLayout(ly)

        if self.is_finished:
            self.empezar()
        else:
            self.pon_toolbar(["terminar", "empezar"])

        self.muestraControles(False)

    def muestraControles(self, si):
        for control in (
            self.lbJuegan,
            self.board,
            self.lbPuntos,
            self.lbSegundos,
            self.lbPrimera,
            self.lb_conditions,
            self.lb_game,
            self.pgn,
            self.gbRM,
        ):
            control.setVisible(si)

    def seguir(self):
        self.muestraControles(True)
        pos = self.actualP + 1
        if pos >= len(self.liBT):
            pos = 0
        self.buscaPrimero(pos)

    def opciones(self):
        form = FormLayout.FormLayout(self, "Training settings", Iconos.Opciones(), anchoMinimo=500)
        form.separador()
        form.editbox(
            _("Tolerance: How many centipawns below the best move are accepted"),
            tipo=int,
            ancho=50,
            init_value=self.pts_tolerance,
        )
        resultado = form.run()
        if not resultado:
            return
        accion, li_gen = resultado
        self.pts_tolerance = li_gen[0]
        dic_var = self.configuration.read_variables("BMT_OPTIONS")
        dic_var["PTS_TOLERANCE"] = self.pts_tolerance
        self.configuration.write_variables("BMT_OPTIONS", dic_var)

    def abandonar(self):
        self.bmt_uno.puntos = 0
        self.activaJugada(0)
        self.ponPuntos(0)
        self.pon_toolbar()

    def borrar(self):
        if QTUtil2.pregunta(self, _("Do you want to delete this position?")):
            self.borrar_fen_lista.add(self.bmt_uno.fen)
            QTUtil2.message(self, _("This position will be deleted on exit."))
            self.seguir()

    def process_toolbar(self):
        accion = self.sender().key
        if accion == "terminar":
            self.terminar()
            self.accept()
        elif accion == "seguir":
            self.seguir()
        elif accion == "abandonar":
            self.abandonar()
        elif accion == "borrar":
            self.borrar()
        elif accion == "repetir":
            self.muestraControles(True)
            self.repetir()
        elif accion == "empezar":
            self.muestraControles(True)
            self.empezar()
        elif accion == "original":
            self.original()
        elif accion == "opciones":
            self.opciones()

    def closeEvent(self, event):
        self.terminar()

    def empezar(self):
        self.buscaPrimero(0)
        self.ponPuntos(0)
        self.ponSegundos()
        self.set_clock()

    def terminar(self):
        self.finalizaTiempo()

        if len(self.borrar_fen_lista) > 0:
            self.bmt_lista.borrar_fen_lista(self.borrar_fen_lista)

        atotal, ahechos, at_puntos, at_segundos, at_estado = self.datosInicio

        total, hechos, t_puntos, t_segundos, t_estado = self.bmt_lista.calc_thpse()

        if (
            (hechos != ahechos)
            or (t_puntos != at_puntos)
            or (t_segundos != at_segundos)
            or (t_estado != at_estado)
            or len(self.borrar_fen_lista) > 0
        ):

            reg = self.dbf.baseRegistro()

            reg.BMT_LISTA = Util.var2zip(self.bmt_lista)

            reg.HECHOS = hechos
            reg.SEGUNDOS = t_segundos
            reg.PUNTOS = t_puntos
            # Si hay posiciones borradas, tenemos que actualizar TOTAL y MAXPUNTOS
            reg.TOTAL = len(self.bmt_lista)
            reg.MAXPUNTOS = self.bmt_lista.max_puntos()

            if self.historial:
                reg.HISTORIAL = Util.var2zip(self.historial)
                reg.REPE = len(self.historial)

            if self.is_finished:
                if not self.siTerminadaAntes:
                    reg.ESTADO = str(t_estado / total)
                    reg.FFINAL = Util.dtos(Util.today())

            self.dbf.modificarReg(self.recnoActual, reg)

        self.save_video()

    def repetir(self):
        # # Opcion de repetir solo las posiciones dificiles
        # Contamos las posiciones debajo un cierto state para el combobox

        num_pos_estate = {}
        for y in range(0, 9):
            num_pos_estate[y] = 0

        nposic = len(self.bmt_lista)
        for x in range(nposic):
            estado = self.bmt_lista.state(x)
            for y in range(0, 9):
                if estado < y:
                    num_pos_estate[y] += 1

        num_pos_estate[9] = nposic
        labels_score = {
            9: _("Repeat all"),
            8: _("Best move"),
            7: _("Excellent"),
            6: _("Very good"),
            5: _("Good"),
            4: _("Acceptable"),
        }

        li_gen = [(None, None)]
        liJ = []

        for x in reversed(range(5, 10)):
            if num_pos_estate[x] > 0:
                label = "%s (%s)" % (labels_score[x], num_pos_estate[x])
                liJ.append((label, x))

        config = FormLayout.Combobox(_("Repeat only below score"), liJ)
        li_gen.append((config, 9))

        titulo = "%s" % (_("Do you want to repeat this training?"))
        resultado = FormLayout.fedit(li_gen, title=titulo, parent=self, anchoMinimo=560, icon=Iconos.Opciones())
        if not resultado:
            return

        accion, li_gen = resultado
        reiniciar_debajo_state = li_gen[0]

        self.quitaReloj()

        total, hechos, t_puntos, t_segundos, t_estado = self.bmt_lista.calc_thpse()

        dic = {}
        dic["FFINAL"] = self.dbf.FFINAL if self.siTerminadaAntes else Util.dtos(Util.today())
        dic["STATE"] = str(t_estado / total)
        dic["PUNTOS"] = t_puntos
        dic["SEGUNDOS"] = t_segundos

        self.historial.append(dic)

        self.bmt_lista.reiniciar(reiniciar_debajo_state)

        for x in range(nposic):
            estado = self.bmt_lista.state(x)
            self.liBT[x].ponIcono(self.dicIconos[estado])

        # for bt in self.liBT:
        #    bt.ponIcono(self.dicIconos[0])

        self.siTerminadaAntes = self.is_finished = False
        self.board.set_position(Position.Position().logo())
        for bt in self.liBTrm:
            bt.set_text("")
        self.siMostrarPGN = False
        self.pgn.refresh()
        self.lbPuntos.set_text("")
        self.lbSegundos.set_text("")
        self.lbJuegan.set_text("")
        self.lbPrimera.set_text(self.texto_lbPrimera)
        self.lbPrimera.setVisible(False)
        self.pon_toolbar(["terminar", "empezar"])
        # Ahora la ventana se queda vacia - por eso lo cierro
        self.terminar()
        self.accept()

    def disable_all(self):  # compatibilidad ControlPGN
        return

    def refresh(self):  # compatibilidad ControlPGN
        self.board.escena.update()
        self.update()
        QTUtil.refresh_gui()

    def set_position(self, position):
        self.board.set_position(position)

    def put_arrow_sc(self, from_sq, to_sq, liVar=None):  # liVar incluido por compatibilidad
        self.board.put_arrow_sc(from_sq, to_sq)

    def grid_num_datos(self, grid):
        if self.siMostrarPGN:
            return self.controlPGN.num_rows()
        else:
            return 0

    def ponteAlPrincipio(self):
        self.board.set_position(self.game.first_position)
        self.pgn.goto(0, 0)
        self.pgn.refresh()

    def pgnMueveBase(self, row, column):
        if column == "NUMBER":
            if row == 0:
                self.ponteAlPrincipio()
                return
            else:
                row -= 1
        self.controlPGN.mueve(row, column == "WHITE")

    def keyPressEvent(self, event):
        self.key_pressed("V", event.key())

    def boardWheelEvent(self, nada, forward):
        self.key_pressed("T", QtCore.Qt.Key.Key_Left if forward else QtCore.Qt.Key.Key_Right)

    def grid_dato(self, grid, row, o_column):
        return self.controlPGN.dato(row, o_column.key)

    def grid_left_button(self, grid, row, column):
        self.pgnMueveBase(row, column.key)

    def grid_right_button(self, grid, row, column, modificadores):
        self.pgnMueveBase(row, column.key)

    def grid_doble_click(self, grid, row, column):
        if column.key == "NUMBER":
            return
        self.analize_position(row, column.key)

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        self.key_pressed("G", k)

    def grid_wheel_event(self, ogrid, forward):
        self.key_pressed("T", QtCore.Qt.Key.Key_Left if forward else QtCore.Qt.Key.Key_Right)

    def key_pressed(self, tipo, tecla):
        if self.siMostrarPGN:
            dic = QTUtil2.dic_keys()
            if tecla in dic:
                self.mueveJugada(dic[tecla])
        if tecla == 82 and tipo == "V":  # R = resign
            self.abandonar()
        elif tecla == 78 and tipo == "V":  # N = next
            self.seguir()
        elif tecla in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):  # Del
            self.borrar()

    def mueveJugada(self, tipo):
        game = self.game
        row, column = self.pgn.current_position()

        key = column.key
        if key == "NUMBER":
            is_white = tipo == GO_BACK
            row -= 1
        else:
            is_white = key != "BLACK"

        starts_with_black = game.starts_with_black

        lj = len(game)
        if starts_with_black:
            lj += 1
        ultFila = (lj - 1) / 2
        siUltBlancas = lj % 2 == 1

        if tipo == GO_BACK:
            if is_white:
                row -= 1
            is_white = not is_white
            pos = row * 2
            if not is_white:
                pos += 1
            if row < 0 or (row == 0 and pos == 0 and starts_with_black):
                self.ponteAlPrincipio()
                return
        elif tipo == GO_FORWARD:
            if not is_white:
                row += 1
            is_white = not is_white
        elif tipo == GO_START:  # Inicio
            self.ponteAlPrincipio()
            return
        elif tipo == GO_END:
            row = ultFila
            is_white = not game.last_position.is_white

        if row == ultFila:
            if siUltBlancas and not is_white:
                return

        if row < 0 or row > ultFila:
            self.refresh()
            return
        if row == 0 and is_white and starts_with_black:
            is_white = False

        self.pgnColocate(row, is_white)
        self.pgnMueveBase(row, "WHITE" if is_white else "BLACK")

    def pgnColocate(self, fil, is_white):
        col = 1 if is_white else 2
        self.pgn.goto(fil, col)

    def number(self):
        bt = self.sender()
        self.activaPosicion(bt.number)
        return 0

    def pulsadoRM(self):
        if self.siMostrarPGN:
            bt = self.sender()
            self.muestra(bt.number)

    def pon_toolbar(self, li=None):
        if not li:
            li = ["terminar"]

            if not self.bmt_uno.finished:
                li.append("abandonar")

            li.append("borrar")
            li.append("opciones")

            if self.bmt_uno.finished:
                if self.is_finished:
                    li.append("repetir")
                if self.bmt_uno.cl_game:
                    li.append("original")
            li.append("seguir")

        self.tb.clear()
        for k in li:
            self.tb.dic_toolbar[k].setVisible(True)
            self.tb.dic_toolbar[k].setEnabled(True)
            self.tb.addAction(self.tb.dic_toolbar[k])

        self.tb.li_acciones = li
        self.tb.update()

    def ponPuntos(self, descontar):
        self.bmt_uno.puntos -= descontar
        if self.bmt_uno.puntos < 0:
            self.bmt_uno.puntos = 0
        self.bmt_uno.update_state()

        eti = "%d/%d" % (self.bmt_uno.puntos, self.bmt_uno.max_puntos)
        self.lbPuntos.set_text(self.trPuntos % eti)

    def ponSegundos(self):
        seconds = self.bmt_uno.seconds
        if self.iniTiempo:
            seconds += int(time.time() - self.iniTiempo)
        minutos = seconds // 60
        seconds -= minutos * 60

        if minutos:
            eti = "%d'%d\"" % (minutos, seconds)
        else:
            eti = '%d"' % (seconds,)
        eti = self.trSegundos % eti

        if eti != self.antTxtSegundos:
            self.antTxtSegundos = eti
            self.lbSegundos.set_text(eti)

    def buscaPrimero(self, from_sq):
        # Buscamos el primero que no se ha terminado
        n = len(self.bmt_lista)
        for x in range(n):
            t = from_sq + x
            if t >= n:
                t = 0
            if not self.bmt_lista.finished(t):
                self.activaPosicion(t)
                return

        self.activaPosicion(from_sq)

    def activaJugada1(self, num):
        rm = self.bmt_uno.mrm.li_rm[num]
        if num == 0:
            self.ptsMejor = rm.centipawns_abs()
        game = Game.Game()
        game.restore(rm.txtPartida)

        bt = self.liBTrm[num]
        txt = "%d: %s" % (rm.nivelBMT + 1, game.move(0).pgn_translated())
        mas = rm.abrTexto()
        if mas:
            txt += " = %s" % rm.abrTexto()
        if rm.siPrimero:
            txt = "%s *" % txt
            self.lbPrimera.setVisible(True)
            self.ptsPrimero = rm.centipawns_abs()

        bt.set_text(txt)
        bt.setEnabled(True)
        bt.ponPlano(False)

    def activaJugada(self, num):
        rm = self.bmt_uno.mrm.li_rm[num]
        mm = self.bmt_uno.mrm.li_rm[0]
        if rm.nivelBMT == 0 or abs(rm.centipawns_abs() - mm.centipawns_abs()) <= self.pts_tolerance:
            self.finalizaTiempo()
            for n in range(len(self.bmt_uno.mrm.li_rm)):
                self.activaJugada1(n)
            self.bmt_uno.finished = True
            diferenciaPtsPrimero = self.ptsPrimero - self.ptsMejor
            self.lbPrimera.set_text(
                "%s (%s %s)" % (self.texto_lbPrimera, "%0.2f" % (-diferenciaPtsPrimero / 100.0), _("pws lost"))
            )
            self.muestra(num)
            self.ponPuntos(0)
            bt = self.liBT[self.actualP]
            bt.ponIcono(self.dicIconos[self.bmt_uno.state])

            self.is_finished = self.bmt_lista.is_finished()

            self.pon_toolbar()

        else:
            self.activaJugada1(num)

    def activaPosicion(self, num):
        self.finalizaTiempo()  # Para que guarde el vtime, si no es el primero
        self.muestraControles(True)

        self.bmt_uno = bmt_uno = self.bmt_lista.dame_uno(num)

        mrm = bmt_uno.mrm
        tm = mrm.max_time
        dp = mrm.max_depth
        txt_engine = mrm.name + " "
        if tm > 0:
            txt_engine += "%d %s" % (tm / 1000, _("Second(s)"))
        elif dp > 0:
            txt_engine = "%s %d" % (_("depth"), dp)

        self.position.read_fen(bmt_uno.fen)

        mens = ""
        if self.position.castles:
            color, colorR = _("White"), _("Black")
            cK, cQ, cKR, cQR = "K", "Q", "k", "q"

            def menr(ck, cq):
                enr = ""
                if ck in self.position.castles:
                    enr += "O-O"
                if cq in self.position.castles:
                    if enr:
                        enr += "  +  "
                    enr += "O-O-O"
                return enr

            enr = menr(cK, cQ)
            if enr:
                mens += "  %s : %s" % (color, enr)
            enr = menr(cKR, cQR)
            if enr:
                mens += "  %s : %s" % (colorR, enr)
        if self.position.en_passant != "-":
            mens += "\n%s : %s" % (_("En passant"), self.position.en_passant)

        if mens:
            mens = mens.strip()

        self.lb_conditions.set_text(txt_engine + "\n" + mens)
        self.lb_game.set_text("")
        self.lbPrimera.set_text(self.texto_lbPrimera)

        self.board.dbvisual_set_show_always(False)
        self.board.set_position(self.position)

        self.liBT[self.actualP].ponPlano(True)
        self.liBT[num].ponPlano(False)
        self.actualP = num

        nliRM = len(mrm.li_rm)
        game = Game.Game()
        for x in range(16):
            bt = self.liBTrm[x]
            if x < nliRM:
                rm = mrm.li_rm[x]
                bt.setVisible(True)
                bt.ponPlano(not rm.siElegida)
                baseTxt = str(rm.nivelBMT + 1)
                if rm.siElegida:
                    game.set_position(self.position)
                    game.read_pv(rm.pv)
                    baseTxt += " - " + game.move(0).pgn_translated()
                bt.set_text(baseTxt)
            else:
                bt.setVisible(False)

        self.ponPuntos(0)
        self.ponSegundos()

        self.pon_toolbar()
        if bmt_uno.finished:
            self.activaJugada(0)
            self.muestra(0)
        else:
            self.lbPrimera.setVisible(False)
            self.iniciaTiempo()
            self.sigueHumano()

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.paraHumano()

        movimiento = from_sq + to_sq

        # Peon coronando
        if not promotion and self.position.siPeonCoronando(from_sq, to_sq):
            promotion = self.board.peonCoronando(self.position.is_white)
        if promotion:
            movimiento += promotion

        nElegido = None
        puntosDescontar = self.bmt_uno.mrm.li_rm[-1].nivelBMT
        for n, rm in enumerate(self.bmt_uno.mrm.li_rm):
            if rm.pv.lower().startswith(movimiento.lower()):
                nElegido = n
                puntosDescontar = rm.nivelBMT
                break

        self.ponPuntos(puntosDescontar)

        if nElegido is not None:
            self.activaJugada(nElegido)

        if not self.bmt_uno.finished:
            self.sigueHumano()
        return True

    def paraHumano(self):
        self.board.disable_all()

    def sigueHumano(self):
        self.siMostrarPGN = False
        self.pgn.refresh()
        siW = self.position.is_white
        self.board.set_position(self.position)
        self.board.set_side_bottom(siW)
        self.board.set_side_indicator(siW)
        self.board.activate_side(siW)
        self.lbJuegan.set_text(_("White to play") if siW else _("Black to play"))

    def set_clock(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.enlaceReloj)
        self.timer.start(500)

    def quitaReloj(self):
        if self.timer:
            self.timer.stop()
            self.timer = None

    def enlaceReloj(self):
        self.ponSegundos()

    def original(self):
        self.siMostrarPGN = True
        self.lbJuegan.set_text(_("Actual game"))
        txtPartida = self.bmt_lista.dic_games[self.bmt_uno.cl_game]
        self.game.restore(txtPartida)

        def tag(ctag):
            t = self.game.get_tag(ctag)
            if t:
                if "?" in t:
                    if t != "?":
                        t = t.replace("?", "")
                        t = t.strip(".")
                    else:
                        t = ""
            return t

        event = tag("EVENT")
        site = tag("SITE")
        result = tag("RESULT")
        white = tag("WHITE")
        white = "%s: %s" % (_("White"), white) if white else ""
        black = tag("BLACK")
        black = "%s: %s" % (_("Black"), black) if black else ""
        date = tag("DATE")
        info = event + " " + site + " " + date + "\n" + white + " - " + black + " " + result
        info = info.strip()
        while "  " in info:
            info = info.replace("  ", " ")
        self.lb_game.set_text(info)
        self.lb_game.setToolTip(self.game.pgn_tags())

        siW = self.position.is_white
        fen = self.position.fen()
        row = 0
        for move in self.game.li_moves:
            if move.position_before.fen() == fen:
                break
            if not move.position_before.is_white:
                row += 1
        self.pgnMueveBase(row, "WHITE" if siW else "BLACK")
        self.pgn.goto(row, 1 if siW else 2)

        self.board.set_side_bottom(siW)

        self.pgn.refresh()

    def muestra(self, num):
        for n, bt in enumerate(self.liBTrm):
            f = bt.font()
            siBold = f.bold()
            if (num == n and not siBold) or (num != n and siBold):
                f.setBold(not siBold)
                bt.setFont(f)
            bt.setAutoDefault(num == n)
            bt.setDefault(num == n)

        self.siMostrarPGN = True
        self.lbJuegan.set_text(self.liBTrm[num].text())
        self.game.set_position(self.position)
        rm = self.bmt_uno.mrm.li_rm[num]
        self.game.restore(rm.txtPartida)

        siW = self.position.is_white
        self.pgnMueveBase(0, "WHITE" if siW else "BLACK")
        self.pgn.goto(0, 1 if siW else 2)

        self.board.set_side_bottom(siW)

        self.pgn.refresh()

    def iniciaTiempo(self):
        self.iniTiempo = time.time()
        if not self.timer:
            self.set_clock()

    def finalizaTiempo(self):
        if self.iniTiempo:
            vtime = time.time() - self.iniTiempo
            self.bmt_uno.seconds += int(vtime)
        self.iniTiempo = None
        self.quitaReloj()

    def dameJugadaEn(self, row, key):
        is_white = key != "BLACK"

        pos = row * 2
        if not is_white:
            pos += 1
        if self.game.starts_with_black:
            pos -= 1
        tam_lj = len(self.game)
        if tam_lj == 0:
            return
        siUltimo = (pos + 1) >= tam_lj

        move = self.game.move(pos)
        return move, is_white, siUltimo, tam_lj, pos

    def analize_position(self, row, key):
        if row < 0:
            return

        move, is_white, siUltimo, tam_lj, pos = self.dameJugadaEn(row, key)
        if move.is_mate:
            return

        Analysis.show_analysis(self.procesador, self.procesador.XTutor(), move, is_white, pos, main_window=self)
