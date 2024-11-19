import os.path

from Code import Util
from Code.Base import Game, Position
from Code.BestMoveTraining import BMT, WindowBMTtrain
from Code.Odt import WOdt
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2, SelectFiles
from Code.QT import QTVarios
from Code.Translations import TrListas


class WHistorialBMT(LCDialog.LCDialog):
    def __init__(self, owner, dbf):

        # Variables
        self.procesador = owner.procesador
        self.configuration = owner.configuration

        # Datos ----------------------------------------------------------------
        self.dbf = dbf
        self.recnoActual = self.dbf.recno
        bmt_lista = Util.zip2var(dbf.leeOtroCampo(self.recnoActual, "BMT_LISTA")).patch()
        self.liHistorial = Util.zip2var(dbf.leeOtroCampo(self.recnoActual, "HISTORIAL"))
        self.max_puntos = dbf.MAXPUNTOS

        if bmt_lista.is_finished():
            dic = {"FFINAL": dbf.FFINAL, "STATE": dbf.ESTADO, "PUNTOS": dbf.PUNTOS, "SEGUNDOS": dbf.SEGUNDOS}
            self.liHistorial.append(dic)

        # Dialogo ---------------------------------------------------------------
        icono = Iconos.Historial()
        titulo = _("History") + ": " + dbf.NOMBRE
        extparam = "bmthistorial"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        # Toolbar
        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("STATE", "", 26, edicion=Delegados.PmIconosBMT(), align_center=True)
        o_columns.nueva("PUNTOS", _("Score"), 104, align_center=True)
        o_columns.nueva("TIME", _("Time"), 80, align_center=True)
        o_columns.nueva("FFINAL", _("End date"), 90, align_center=True)

        self.grid = grid = Grid.Grid(self, o_columns, xid=False, is_editable=True)
        # n = grid.anchoColumnas()
        # grid.setMinimumWidth( n + 20 )
        self.register_grid(grid)

        # Colocamos ---------------------------------------------------------------
        ly = Colocacion.V().control(tb).control(self.grid)

        self.setLayout(ly)

        self.restore_video(siTam=True)

    def terminar(self):
        self.save_video()
        self.accept()

    def grid_num_datos(self, grid):
        return len(self.liHistorial)

    def grid_dato(self, grid, row, o_column):
        dic = self.liHistorial[row]
        col = o_column.key
        if col == "STATE":
            return dic["STATE"]

        elif col == "HECHOS":
            return "%d" % (dic["HECHOS"])

        elif col == "PUNTOS":
            p = dic["PUNTOS"]
            m = self.max_puntos
            porc = p * 100 / m
            return "%d/%d=%d" % (p, m, porc) + "%"

        elif col == "FFINAL":
            f = dic["FFINAL"]
            return "%s-%s-%s" % (f[6:], f[4:6], f[:4]) if f else ""

        elif col == "TIME":
            s = dic["SEGUNDOS"]
            if not s:
                s = 0
            m = s / 60
            s %= 60
            return "%d' %d\"" % (m, s) if m else '%d"' % s


class WBMT(LCDialog.LCDialog):
    def __init__(self, procesador):

        self.procesador = procesador
        self.configuration = procesador.configuration
        self.configuration.compruebaBMT()

        self.bmt = BMT.BMT(self.configuration.ficheroBMT)
        self.read_dbf()

        owner = procesador.main_window
        icono = Iconos.BMT()
        titulo = self.titulo()
        extparam = "bmt"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        # Toolbar
        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Play"), Iconos.Empezar(), self.entrenar),
            None,
            (_("New"), Iconos.Nuevo(), self.nuevo),
            None,
            (_("Modify"), Iconos.Modificar(), self.modificar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("History"), Iconos.Historial(), self.historial),
            None,
            (_("Utilities"), Iconos.Utilidades(), self.utilities),
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        self.tab = tab = Controles.Tab()

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NOMBRE", _("Name"), 274, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("EXTRA", _("Extra info."), 64, align_center=True)
        o_columns.nueva("HECHOS", _("Made"), 84, align_center=True)
        o_columns.nueva("PUNTOS", _("Score"), 84, align_center=True)
        o_columns.nueva("TIME", _("Time"), 80, align_center=True)
        o_columns.nueva("REPETICIONES", _("Rep."), 50, align_center=True)
        o_columns.nueva("ORDEN", _("Order"), 70, align_center=True)

        self.grid = grid = Grid.Grid(
            self, o_columns, xid="P", is_editable=False, siSelecFilas=True, siSeleccionMultiple=True
        )
        self.register_grid(grid)
        tab.new_tab(grid, _("Pending"))

        # Terminados
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("STATE", "", 26, edicion=Delegados.PmIconosBMT(), align_center=True)
        o_columns.nueva("NOMBRE", _("Name"), 240)
        o_columns.nueva("EXTRA", _("Extra info."), 64, align_center=True)
        o_columns.nueva("HECHOS", _("Positions"), 64, align_center=True)
        o_columns.nueva("PUNTOS", _("Score"), 84, align_center=True)
        o_columns.nueva("FFINAL", _("End date"), 90, align_center=True)
        o_columns.nueva("TIME", _("Time"), 80, align_center=True)
        o_columns.nueva("REPETICIONES", _("Rep."), 50, align_center=True)
        o_columns.nueva("ORDEN", _("Order"), 70, align_center=True)

        self.gridT = gridT = Grid.Grid(
            self, o_columns, xid="T", is_editable=True, siSelecFilas=True, siSeleccionMultiple=True
        )
        self.register_grid(gridT)
        tab.new_tab(gridT, _("Finished"))

        self.dicReverse = {}

        # Layout
        layout = Colocacion.V().control(tb).control(tab).margen(8)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=760, altoDefecto=500)

        self.grid.gotop()
        self.gridT.gotop()

        self.grid.setFocus()

    def titulo(self):
        fdir, fnam = os.path.split(self.configuration.ficheroBMT)
        return "%s : %s (%s)" % (_("Find best move"), fnam, Util.relative_path(fdir))

    def terminar(self):
        self.bmt.cerrar()
        self.save_video()
        self.reject()
        return

    def actual(self):
        if self.tab.current_position() == 0:
            grid = self.grid
            dbf = self.dbf
        else:
            grid = self.gridT
            dbf = self.dbfT
        recno = grid.recno()
        if recno >= 0:
            dbf.goto(recno)

        return grid, dbf, recno

    def historial(self):
        grid, dbf, recno = self.actual()
        if recno >= 0:
            if dbf.REPE > 0:
                w = WHistorialBMT(self, dbf)
                w.exec_()

    def utilities(self):
        menu = QTVarios.LCMenu(self)

        menu.opcion("cambiar", _("Select/create another file of training"), Iconos.BMT())

        menu.separador()
        menu1 = menu.submenu(_("Import") + "/" + _("Export"), Iconos.PuntoMagenta())
        menu1.opcion("exportar", _("Export the current training"), Iconos.PuntoVerde())
        menu1.separador()
        menu1.opcion("exportarLimpio", _("Export current training with no history"), Iconos.PuntoAzul())
        menu1.separador()
        menu1.opcion("importar", _("Import a training"), Iconos.PuntoNaranja())

        menu.separador()
        menu2 = menu.submenu(_("Generate new trainings"), Iconos.PuntoRojo())
        menu2.opcion("dividir", _("Dividing the active training"), Iconos.PuntoVerde())
        menu2.separador()
        menu2.opcion("extraer", _("Extract a range of positions"), Iconos.PuntoAzul())
        menu2.separador()
        menu2.opcion("juntar", _("Joining selected trainings"), Iconos.PuntoNaranja())
        menu2.separador()
        menu2.opcion("rehacer", _("Analyze again"), Iconos.PuntoAmarillo())

        menu.separador()
        menu.opcion("odt", "%s: %s (*.odt)" % (_("Export to"), _("Open Document Format")), Iconos.ODT())

        resp = menu.lanza()
        if resp:
            if resp == "cambiar":
                self.cambiar()
            elif resp == "importar":
                self.importar()
            elif resp.startswith("exportar"):
                self.exportar(resp == "exportarLimpio")
            elif resp == "dividir":
                self.dividir()
            elif resp == "extraer":
                self.extraer()
            elif resp == "juntar":
                self.juntar()
            elif resp == "pack":
                self.pack()
            elif resp == "rehacer":
                self.rehacer()
            elif resp == "odt":
                self.odt()

    def odt(self):
        grid, dbf, recno = self.actual()
        if recno < 0:
            return

        bmt_lista = Util.zip2var(dbf.leeOtroCampo(recno, "BMT_LISTA"))
        if bmt_lista is None:
            return
        bmt_lista.patch()
        bmt_lista.check_color()

        dic_games = bmt_lista.dic_games

        dic = {"POS": -1, "TOTAL": len(bmt_lista)}

        path_odt = WOdt.path_saveas_odt(self, dbf.NOMBRE)
        if not path_odt:
            return
        wodt = WOdt.WOdt(self, path_odt)
        board = wodt.board

        def run_data(wodt):
            current_pos = dic["POS"]
            total = dic["TOTAL"]
            if current_pos == -1:
                wodt.create_document("%s - %s: %s" % (_("Lucas Chess"), _("Find best move"), dbf.NOMBRE), True)
                current_pos += 1
            else:
                wodt.odt_doc.add_pagebreak()

            wodt.set_cpos("%d/%d" % (current_pos + 1, total))

            bmt_uno = bmt_lista.li_bmt_uno[current_pos]
            position = Position.Position()
            position.read_fen(bmt_uno.fen)
            board.set_position(position)
            if board.is_white_bottom != position.is_white:
                board.rotate_board()

            wodt.odt_doc.add_paragraph("%s %d" % (_("Position"), current_pos + 1), bold=True)
            wodt.odt_doc.add_linebreak()
            path_img = self.configuration.ficheroTemporal("png")
            board.save_as_img(path_img, "png", False, True)
            wodt.odt_doc.add_png(path_img, 13.4)
            wodt.odt_doc.add_pagebreak()
            wodt.odt_doc.add_paragraph8("FEN: " + bmt_uno.fen)
            mrm = bmt_uno.mrm
            best_score = 0

            for j in range(0, len(mrm.li_rm)):
                rm = mrm.li_rm[j]
                if j == 0:
                    best_score = rm.centipawns_abs()

                wodt.odt_doc.add_linebreak()
                game = Game.Game()
                game.restore(rm.txtPartida)

                def get_move_list(game):
                    is_black = game.starts_with_black
                    move_ctr = 1 if is_black else 0
                    lst_moves = "1. .." if is_black else "1."
                    for move in game.li_moves:
                        if not is_black:
                            move_ctr += 1
                            if move_ctr > 1:
                                lst_moves += " %s." % move_ctr
                        lst_moves += " %s" % move.pgnBase
                        is_black = not is_black
                    return lst_moves

                lst_moves = get_move_list(game)
                pts_lost = best_score - rm.centipawns_abs()
                if pts_lost > 0:
                    txt_lost = " (%s %s)" % (pts_lost / 100, _("pws lost"))
                else:
                    txt_lost = ""
                txt = "%d: %s = %s%s" % (rm.nivelBMT + 1, game.move(0).pgn_translated(), rm.abbrev_text(), txt_lost)
                if rm.siPrimero:
                    txt = "* %s" % txt
                wodt.odt_doc.add_paragraph("%s | %s" % (txt, lst_moves))

            original_game = None
            if bmt_uno.cl_game and bmt_uno.cl_game in dic_games:
                txt_game = dic_games[bmt_uno.cl_game]
                original_game = Game.Game()
                original_game.restore(txt_game)

            if original_game:
                di_tags = {}
                for name, value in original_game.li_tags:
                    di_tags[name] = value

                wodt.odt_doc.add_linebreak()
                wodt.odt_doc.add_linebreak()

                tag_txt = _("Actual game") + ": "
                if "White" in di_tags and "Black" in di_tags:
                    tag_txt += "%s vs %s" % (di_tags["White"], di_tags["Black"])
                if "Date" in di_tags:
                    tag_txt += " (%s)" % (di_tags["Date"])

                if "Site" in di_tags and di_tags["Site"].startswith("http"):
                    gamelink = di_tags["Site"]
                    tag_txt += ": %s" % gamelink
                    wodt.odt_doc.add_hyperlink(gamelink, tag_txt)
                else:
                    wodt.odt_doc.add_paragraph(tag_txt)

                for tag in ["Event", "TimeControl", "Opening", "Result", "WhiteElo", "BlackElo"]:
                    if tag in di_tags:
                        wodt.odt_doc.add_paragraph("%s: %s " % (tag, di_tags[tag]))

            dic["POS"] = current_pos + 1
            if dic["POS"] < total:
                return True
            else:
                wodt.odt_doc.create(path_odt)
                os.startfile(path_odt)
                return False

        wodt.set_routine(run_data)
        wodt.exec_()

    def pack(self):
        um = QTUtil2.one_moment_please(self)
        self.dbf.pack()
        self.releer()
        um.final()

    def rehacer(self):
        grid, dbf, recno = self.actual()
        if recno < 0:
            return
        name = dbf.NOMBRE
        extra = dbf.EXTRA
        bmt_lista = Util.zip2var(dbf.leeOtroCampo(recno, "BMT_LISTA")).patch()

        # Motor y vtime, cogemos los estandars de analysis
        file = self.configuration.file_param_analysis()
        dic = Util.restore_pickle(file)
        if dic:
            engine = dic["ENGINE"]
            vtime = dic["TIME"]
        else:
            engine = self.configuration.x_tutor_clave
            vtime = self.configuration.x_tutor_mstime

        # Bucle para control de errores
        li_gen = [(None, None)]

        # # Nombre del entrenamiento
        li_gen.append((_("Name") + ":", name))
        li_gen.append((_("Extra info.") + ":", extra))

        # # Tutor
        li = self.configuration.ayudaCambioTutor()
        li[0] = engine
        li_gen.append((_("Engine") + ":", li))

        # Decimas de segundo a pensar el tutor
        li_gen.append((_("Duration of engine analysis (secs)") + ":", vtime / 1000.0))

        li_gen.append((None, None))

        resultado = FormLayout.fedit(li_gen, title=name, parent=self, anchoMinimo=560, icon=Iconos.Opciones())
        if not resultado:
            return
        accion, li_gen = resultado

        name = li_gen[0]
        extra = li_gen[1]
        engine = li_gen[2]
        vtime = int(li_gen[3] * 1000)

        if not vtime or not name:
            return

        dic = {"ENGINE": engine, "TIME": vtime}
        Util.save_pickle(file, dic)

        # Analizamos todos, creamos las games, y lo salvamos
        confMotor = self.configuration.buscaRival(engine)
        confMotor.multiPV = 16
        xmanager = self.procesador.creaManagerMotor(confMotor, vtime, None, True)

        tamLista = len(bmt_lista.li_bmt_uno)

        mensaje = _("Analyzing the move....")
        tmpBP = QTUtil2.BarraProgreso(self.procesador.main_window, name, mensaje, tamLista).mostrar()

        cp = Position.Position()
        is_canceled = False

        game = Game.Game()

        for pos in range(tamLista):

            uno = bmt_lista.dame_uno(pos)

            fen = uno.fen
            ant_movimiento = ""
            for rm in uno.mrm.li_rm:
                if rm.siPrimero:
                    ant_movimiento = rm.movimiento()
                    break

            tmpBP.mensaje(mensaje + " %d/%d" % (pos, tamLista))
            tmpBP.pon(pos)
            if tmpBP.is_canceled():
                is_canceled = True
                break

            mrm = xmanager.analiza(fen)

            cp.read_fen(fen)

            previa = 999999999
            nprevia = -1
            tniv = 0

            for rm in mrm.li_rm:
                if tmpBP.is_canceled():
                    is_canceled = True
                    break
                pts = rm.centipawns_abs()
                if pts != previa:
                    previa = pts
                    nprevia += 1
                tniv += nprevia
                rm.nivelBMT = nprevia
                rm.siElegida = False
                rm.siPrimero = rm.movimiento() == ant_movimiento
                game.set_position(cp)
                game.read_pv(rm.pv)
                rm.txtPartida = game.save()

            if is_canceled:
                break

            uno.mrm = mrm  # lo cambiamos y ya esta

        xmanager.terminar()

        if not is_canceled:
            # Grabamos

            bmt_lista.reiniciar()

            reg = self.dbf.baseRegistro()
            reg.ESTADO = "0"
            reg.NOMBRE = name
            reg.EXTRA = extra
            reg.TOTAL = len(bmt_lista)
            reg.HECHOS = 0
            reg.PUNTOS = 0
            reg.MAXPUNTOS = bmt_lista.max_puntos()
            reg.FINICIAL = Util.dtos(Util.today())
            reg.FFINAL = ""
            reg.SEGUNDOS = 0
            reg.BMT_LISTA = Util.var2zip(bmt_lista)
            reg.HISTORIAL = Util.var2zip([])
            reg.REPE = 0

            reg.ORDEN = 0

            self.dbf.insertarReg(reg, siReleer=True)

        tmpBP.cerrar()
        self.grid.refresh()

    def grid_doubleclick_header(self, grid, o_column):
        key = o_column.key
        if key != "NOMBRE":
            return

        grid, dbf, recno = self.actual()

        li = []
        for x in range(dbf.reccount()):
            dbf.goto(x)
            li.append((dbf.NOMBRE, x))

        li.sort(key=lambda x: x[0])

        si_reverse = self.dicReverse.get(grid.id, False)
        self.dicReverse[grid.id] = not si_reverse

        if si_reverse:
            li.reverse()

        order = 0
        reg = dbf.baseRegistro()
        for nom, recno in li:
            reg.ORDEN = order
            dbf.modificarReg(recno, reg)
            order += 1
        dbf.commit()
        dbf.leer()
        grid.refresh()
        grid.gotop()

    def dividir(self):
        grid, dbf, recno = self.actual()
        if recno < 0:
            return
        reg = dbf.registroActual()  # Importante ya que dbf puede cambiarse mientras se edita

        li_gen = [(None, None)]

        mx = dbf.TOTAL
        if mx <= 1:
            return
        bl = mx / 2

        li_gen.append((FormLayout.Spinbox(_("Block Size"), 1, mx - 1, 50), bl))

        resultado = FormLayout.fedit(
            li_gen, title="%s %s" % (reg.NOMBRE, reg.EXTRA), parent=self, icon=Iconos.Opciones()
        )

        if resultado:
            accion, li_gen = resultado
            bl = li_gen[0]

            um = QTUtil2.one_moment_please(self)
            bmt_lista = Util.zip2var(dbf.leeOtroCampo(recno, "BMT_LISTA")).patch()

            from_sq = 0
            pos = 1
            extra = reg.EXTRA
            while from_sq < mx:
                to_sq = from_sq + bl
                if to_sq >= mx:
                    to_sq = mx
                bmt_listaNV = bmt_lista.extrae(from_sq, to_sq)
                reg.TOTAL = to_sq - from_sq
                reg.BMT_LISTA = Util.var2zip(bmt_listaNV)
                reg.HISTORIAL = Util.var2zip([])
                reg.REPE = 0
                reg.ESTADO = "0"
                reg.EXTRA = (extra + " (%d)" % pos).strip()
                pos += 1
                reg.HECHOS = 0
                reg.PUNTOS = 0
                reg.MAXPUNTOS = bmt_listaNV.max_puntos()
                reg.FFINAL = ""
                reg.SEGUNDOS = 0

                dbf.insertarReg(reg, siReleer=False)

                from_sq = to_sq

            self.releer()
            um.final()

    def extraer(self):
        grid, dbf, recno = self.actual()
        if recno < 0:
            return
        reg = dbf.registroActual()  # Importante ya que dbf puede cambiarse mientras se edita
        li_gen = [(None, None)]
        config = FormLayout.Editbox(
            '<div align="right">' + _("List of positions") + "<br>" + _("By example:") + " -5,7-9,14,19-",
            rx=r"[0-9,\-,\,]*",
        )
        li_gen.append((config, ""))

        resultado = FormLayout.fedit(li_gen, title=reg.NOMBRE, parent=self, anchoMinimo=200, icon=Iconos.Opciones())

        if resultado:
            accion, li_gen = resultado

            bmt_lista = Util.zip2var(dbf.leeOtroCampo(recno, "BMT_LISTA")).patch()
            clista = li_gen[0]
            if clista:
                lni = Util.ListaNumerosImpresion(clista)
                bmt_listaNV = bmt_lista.extrae_lista(lni)

                reg.TOTAL = len(bmt_listaNV)
                reg.BMT_LISTA = Util.var2zip(bmt_listaNV)
                reg.HISTORIAL = Util.var2zip([])
                reg.REPE = 0
                reg.ESTADO = "0"
                reg.EXTRA = clista
                reg.HECHOS = 0
                reg.PUNTOS = 0
                reg.MAXPUNTOS = bmt_listaNV.max_puntos()
                reg.FFINAL = ""
                reg.SEGUNDOS = 0

                um = QTUtil2.one_moment_please(self)
                dbf.insertarReg(reg, siReleer=False)

                self.releer()
                um.final()

    def juntar(self):
        # Lista de recnos
        grid, dbf, recno = self.actual()
        li = grid.recnosSeleccionados()

        if len(li) < 1:
            return

        orden = getattr("dbf", "ORDEN", 0)
        name = dbf.NOMBRE
        extra = dbf.EXTRA

        # Se pide name y extra
        li_gen = [(None, None)]

        # # Nombre del entrenamiento
        li_gen.append((_("Name") + ":", name))

        li_gen.append((_("Extra info.") + ":", extra))

        li_gen.append((FormLayout.Editbox(_("Order"), tipo=int, ancho=50), orden))

        liJ = [
            ("--", 9),
            (_("Best move"), 8),
            (_("Excellent"), 7),
            (_("Very good"), 6),
            (_("Good"), 5),
            (_("Acceptable"), 4),
        ]
        config = FormLayout.Combobox(_("Drop answers with minimum score"), liJ)
        li_gen.append((config, 9))

        titulo = "%s (%d)" % (_("Joining selected trainings"), len(li))
        resultado = FormLayout.fedit(li_gen, title=titulo, parent=self, anchoMinimo=560, icon=Iconos.Opciones())
        if not resultado:
            return

        um = QTUtil2.one_moment_please(self)

        accion, li_gen = resultado
        name = li_gen[0].strip()
        extra = li_gen[1]
        orden = li_gen[2]
        eliminar_state_minimo = li_gen[3]

        # Se crea una bmt_lista, suma de todas
        bmt_lista = BMT.BMTLista()

        li_unos = []
        dic_games = {}
        for recno in li:
            bmt_lista1 = Util.zip2var(dbf.leeOtroCampo(recno, "BMT_LISTA")).patch()
            li_unos.extend(bmt_lista1.li_bmt_uno)
            dic_games.update(bmt_lista1.dic_games)

        st_fen = set()
        if eliminar_state_minimo < 9:
            for uno in li_unos:
                if uno.state >= eliminar_state_minimo:
                    st_fen.add(uno.fen)

        for uno in li_unos:
            if uno.fen not in st_fen:
                st_fen.add(uno.fen)
                bmt_lista.nuevo(uno)
                if uno.cl_game:
                    bmt_lista.check_game(uno.cl_game, dic_games[uno.cl_game])

        if len(bmt_lista) == 0:
            return

        bmt_lista.reiniciar()

        # Se graba el registro
        reg = dbf.baseRegistro()
        reg.ESTADO = "0"
        reg.NOMBRE = name
        reg.EXTRA = extra
        reg.TOTAL = len(bmt_lista)
        reg.HECHOS = 0
        reg.PUNTOS = 0
        reg.MAXPUNTOS = bmt_lista.max_puntos()
        reg.FINICIAL = Util.dtos(Util.today())
        reg.FFINAL = ""
        reg.SEGUNDOS = 0
        reg.BMT_LISTA = Util.var2zip(bmt_lista)
        reg.HISTORIAL = Util.var2zip([])
        reg.REPE = 0

        reg.ORDEN = orden

        dbf.insertarReg(reg, siReleer=False)

        self.releer()

        um.final()

    def cambiar(self):
        fbmt = SelectFiles.salvaFichero(
            self, _("Select/create another file of training"), self.configuration.ficheroBMT, "bmt", False
        )
        if fbmt:
            fbmt = Util.relative_path(fbmt)
            abmt = self.bmt
            try:
                self.bmt = BMT.BMT(fbmt)
            except:
                QTUtil2.message_error(self, _X(_("Unable to read file %1"), fbmt))
                return
            abmt.cerrar()
            self.read_dbf()
            self.configuration.ficheroBMT = fbmt
            self.configuration.graba()
            self.setWindowTitle(self.titulo())
            self.grid.refresh()
            self.gridT.refresh()

    def exportar(self, siLimpiar):
        grid, dbf, recno = self.actual()

        if recno >= 0:
            regActual = dbf.registroActual()
            carpeta = "%s/%s.bm1" % (
                os.path.dirname(self.configuration.ficheroBMT),
                dbf.NOMBRE,
            )  # @Lucas: ya tienes este cambio
            fbm1 = SelectFiles.salvaFichero(self, _("Export the current training"), carpeta, "bm1", True)
            if fbm1:
                if siLimpiar:
                    regActual.ESTADO = "0"
                    regActual.HECHOS = 0
                    regActual.PUNTOS = 0
                    regActual.FFINAL = ""
                    regActual.SEGUNDOS = 0
                    bmt_lista = Util.zip2var(dbf.leeOtroCampo(recno, "BMT_LISTA")).patch()
                    bmt_lista.reiniciar()
                    regActual.BMT_LISTA = bmt_lista
                    regActual.HISTORIAL = []
                    regActual.REPE = 0
                else:
                    regActual.BMT_LISTA = Util.zip2var(dbf.leeOtroCampo(recno, "BMT_LISTA")).patch()
                    regActual.HISTORIAL = Util.zip2var(dbf.leeOtroCampo(recno, "HISTORIAL"))

                Util.save_pickle(fbm1, regActual)

    def modificar(self):
        grid, dbf, recno = self.actual()

        if recno >= 0:
            dbf.goto(recno)

            name = dbf.NOMBRE
            extra = dbf.EXTRA
            orden = dbf.ORDEN

            li_gen = [(None, None)]

            # # Nombre del entrenamiento
            li_gen.append((_("Name") + ":", name))

            li_gen.append((_("Extra info.") + ":", extra))

            li_gen.append((FormLayout.Editbox(_("Order"), tipo=int, ancho=50), orden))

            resultado = FormLayout.fedit(li_gen, title=name, parent=self, anchoMinimo=560, icon=Iconos.Opciones())

            if resultado:
                accion, li_gen = resultado
                li_fieldsValor = (("NOMBRE", li_gen[0].strip()), ("EXTRA", li_gen[1]), ("ORDEN", li_gen[2]))
                self.grabaCampos(grid, recno, li_fieldsValor)

    def releer(self):
        self.dbf.leer()
        self.dbfT.leer()
        self.grid.refresh()
        self.gridT.refresh()
        QTUtil.refresh_gui()

    def importar(self):
        carpeta = os.path.dirname(self.configuration.ficheroBMT)
        fbm1 = SelectFiles.leeFichero(self, carpeta, "bm1", titulo=_("Import a training"))
        if fbm1:

            reg = Util.restore_pickle(fbm1)
            if hasattr(reg, "BMT_LISTA"):
                reg.BMT_LISTA = Util.var2zip(reg.BMT_LISTA)
                reg.HISTORIAL = Util.var2zip(reg.HISTORIAL)
                self.dbf.insertarReg(reg, siReleer=False)
                self.releer()
            else:
                QTUtil2.message_error(self, _X(_("Unable to read file %1"), fbm1))

    def entrenar(self):
        grid, dbf, recno = self.actual()
        if recno >= 0:
            dbf.goto(recno)
            if dbf.TOTAL > 0:
                w = WindowBMTtrain.WTrainBMT(self, dbf)
                w.exec_()
                self.releer()
            else:
                QTUtil2.message_error(self, _("No items left in this training"))

    def borrar(self):
        grid, dbf, recno = self.actual()
        li = grid.recnosSeleccionados()
        if len(li) > 0:
            tit = "<br><ul>"
            for x in li:
                dbf.goto(x)
                tit += "<li>%s %s</li>" % (dbf.NOMBRE, dbf.EXTRA)
            base = _("the following training")
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), base) + tit):
                um = QTUtil2.one_moment_please(self)
                dbf.remove_list_recnos(li)
                dbf.pack()
                self.releer()
                um.final()

    def grabaCampos(self, grid, row, li_fieldsValor):
        dbf = self.dbfT if grid.id == "T" else self.dbf
        reg = dbf.baseRegistro()
        for campo, valor in li_fieldsValor:
            setattr(reg, campo, valor)
        dbf.modificarReg(row, reg)
        dbf.commit()
        dbf.leer()
        grid.refresh()

    def grid_setvalue(self, grid, row, o_column, valor):  # ? necesario al haber delegados
        pass

    def grid_num_datos(self, grid):
        dbf = self.dbfT if grid.id == "T" else self.dbf
        return dbf.reccount()

    def grid_doble_click(self, grid, row, column):
        self.entrenar()

    def grid_dato(self, grid, row, o_column):
        dbf = self.dbfT if grid.id == "T" else self.dbf
        col = o_column.key

        dbf.goto(row)

        if col == "NOMBRE":
            return dbf.NOMBRE

        elif col == "ORDEN":
            return dbf.ORDEN if dbf.ORDEN else 0

        elif col == "STATE":
            return dbf.ESTADO

        elif col == "HECHOS":
            if grid.id == "T":
                return "%d" % dbf.TOTAL
            else:
                return "%d/%d" % (dbf.HECHOS, dbf.TOTAL)

        elif col == "PUNTOS":
            p = dbf.PUNTOS
            m = dbf.MAXPUNTOS
            if grid.id == "T" and m > 0:
                porc = p * 100 / m
                return "%d/%d=%d" % (p, m, porc) + "%"
            else:
                return "%d/%d" % (p, m)

        elif col == "EXTRA":
            return dbf.EXTRA

        elif col == "FFINAL":
            f = dbf.FFINAL
            return "%s-%s-%s" % (f[6:], f[4:6], f[:4]) if f else ""

        elif col == "TIME":
            s = dbf.SEGUNDOS
            if not s:
                s = 0
            m = s / 60
            s %= 60
            return "%d' %d\"" % (m, s) if m else '%d"' % s

        elif col == "REPETICIONES":
            return str(dbf.REPE)

    def read_dbf(self):
        self.dbf = self.bmt.read_dbf(False)
        self.dbfT = self.bmt.read_dbf(True)

    def nuevo(self):
        talpha = Controles.FontType("Chess Merida", self.configuration.x_menu_points + 4)

        def xopcion(menu, key, texto, icono, is_disabled=False):
            if "KP" in texto:
                # d = {"K": "n", "P": "i", "k": "N", "p": "I"}
                k2 = texto.index("K", 2)
                texto = texto[:k2] + texto[k2:].lower()
                # texton = ""
                # for c in texto:
                #     texton += d[c]
                menu.opcion(key, texto, icono, is_disabled, font_type=talpha)
            else:
                menu.opcion(key, texto, icono, is_disabled)

        # Elegimos el entrenamiento
        menu = QTVarios.LCMenu(self)
        self.procesador.entrenamientos.menu_fns(
            menu, _("Select the training positions you want to use as a base"), xopcion
        )
        resp = menu.lanza()
        if resp is None:
            return

        fns = resp[3:]
        with open(fns, "rt", encoding="utf-8", errors="ignore") as f:
            liFEN = []
            for linea in f:
                linea = linea.strip()
                if linea:
                    if "|" in linea:
                        linea = linea.split("|")[0]
                    liFEN.append(linea)
        nFEN = len(liFEN)
        if not nFEN:
            return

        name = os.path.basename(fns)[:-4]
        name = TrListas.dic_training().get(name, name)

        # Motor y vtime, cogemos los estandars de analysis
        file = self.configuration.file_param_analysis()
        dic = Util.restore_pickle(file)
        engine = self.configuration.x_tutor_clave
        vtime = self.configuration.x_tutor_mstime
        if dic:
            engine = dic.get("ENGINE", engine)
            vtime = dic.get("TIME", vtime)

        if not vtime:
            vtime = 3.0

        # Bucle para control de errores
        while True:
            # Datos
            li_gen = [(None, None)]

            # # Nombre del entrenamiento
            li_gen.append((_("Name") + ":", name))

            # # Tutor
            li = self.configuration.ayudaCambioTutor()
            li[0] = engine
            li_gen.append((_("Engine") + ":", li))

            # Decimas de segundo a pensar el tutor
            li_gen.append((_("Duration of engine analysis (secs)") + ":", vtime / 1000.0))

            li_gen.append((None, None))

            li_gen.append((FormLayout.Spinbox(_("From number"), 1, nFEN, 50), 1))
            li_gen.append((FormLayout.Spinbox(_("To number"), 1, nFEN, 50), nFEN if nFEN < 20 else 20))

            resultado = FormLayout.fedit(li_gen, title=name, parent=self, anchoMinimo=560, icon=Iconos.Opciones())

            if resultado:
                accion, li_gen = resultado

                name = li_gen[0]
                engine = li_gen[1]
                vtime = int(li_gen[2] * 1000)

                if not vtime or not name:
                    return

                dic = {"ENGINE": engine, "TIME": vtime}
                Util.save_pickle(file, dic)

                from_sq = li_gen[3]
                to_sq = li_gen[4]
                nDH = to_sq - from_sq + 1
                if nDH <= 0:
                    return
                break

            else:
                return

        # Analizamos todos, creamos las games, y lo salvamos
        confMotor = self.configuration.buscaRival(engine)
        confMotor.multiPV = 16
        xmanager = self.procesador.creaManagerMotor(confMotor, vtime, None, True)

        mensaje = _("Analyzing the move....")
        tmpBP = QTUtil2.BarraProgreso(self.procesador.main_window, name, mensaje, nDH).mostrar()

        cp = Position.Position()
        is_canceled = False

        bmt_lista = BMT.BMTLista()

        game = Game.Game()

        for n in range(from_sq - 1, to_sq):

            fen = liFEN[n]

            tmpBP.mensaje(mensaje + " %d/%d" % (n + 2 - from_sq, nDH))
            tmpBP.pon(n + 2 - from_sq)
            if tmpBP.is_canceled():
                is_canceled = True
                break

            mrm = xmanager.analiza(fen)

            cp.read_fen(fen)

            previa = 999999999
            nprevia = -1
            tniv = 0

            for rm in mrm.li_rm:
                if tmpBP.is_canceled():
                    is_canceled = True
                    break
                pts = rm.centipawns_abs()
                if pts != previa:
                    previa = pts
                    nprevia += 1
                tniv += nprevia
                rm.nivelBMT = nprevia
                rm.siElegida = False
                rm.siPrimero = False
                game.set_position(cp)
                game.read_pv(rm.pv)
                game.is_finished()
                rm.txtPartida = game.save()

            if is_canceled:
                break

            bmt_uno = BMT.BMTUno(fen, mrm, tniv, None)

            bmt_lista.nuevo(bmt_uno)

        xmanager.terminar()

        if not is_canceled:
            # Grabamos

            reg = self.dbf.baseRegistro()
            reg.ESTADO = "0"
            reg.NOMBRE = name
            reg.EXTRA = "%d-%d" % (from_sq, to_sq)
            reg.TOTAL = len(bmt_lista)
            reg.HECHOS = 0
            reg.PUNTOS = 0
            reg.MAXPUNTOS = bmt_lista.max_puntos()
            reg.FINICIAL = Util.dtos(Util.today())
            reg.FFINAL = ""
            reg.SEGUNDOS = 0
            reg.BMT_LISTA = Util.var2zip(bmt_lista)
            reg.HISTORIAL = Util.var2zip([])
            reg.REPE = 0

            reg.ORDEN = 0

            self.dbf.insertarReg(reg, siReleer=True)

        self.releer()
        tmpBP.cerrar()


def windowBMT(procesador):
    w = WBMT(procesador)
    w.exec_()
