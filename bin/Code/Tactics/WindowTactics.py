from PySide2 import QtWidgets

from Code import Util
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


def consultaHistorico(main_window, tactica, icono):
    w = WHistoricoTacticas(main_window, tactica, icono)
    return w.resultado if w.exec_() else None


class WHistoricoTacticas(LCDialog.LCDialog):
    def __init__(self, main_window, tactica, icono):

        LCDialog.LCDialog.__init__(self, main_window, tactica.title, icono, "histoTacticas")

        self.li_histo = tactica.historico()
        self.tactica = tactica
        self.resultado = None

        # Historico
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("REFERENCE", _("Reference"), 120, align_center=True)
        o_columns.nueva("FINICIAL", _("Start date"), 120, align_center=True)
        o_columns.nueva("FFINAL", _("End date"), 120, align_center=True)
        o_columns.nueva("TIME", "%s - %s:%s" % (_("Days"), _("Hours"), _("Minutes")), 120, align_center=True)
        o_columns.nueva("POSICIONES", _("Num. puzzles"), 100, align_center=True)
        o_columns.nueva("SECONDS", _("Working time"), 100, align_center=True)
        o_columns.nueva("ERRORS", _("Errors"), 100, align_center=True)
        self.ghistorico = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.ghistorico.setMinimumWidth(self.ghistorico.anchoColumnas() + 20)

        # Tool bar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), "terminar"),
            (_("Train"), Iconos.Empezar(), "entrenar"),
            (_("New"), Iconos.Nuevo(), "nuevo"),
            (_("Remove"), Iconos.Borrar(), "borrar"),
        )
        self.tb = Controles.TB(self, li_acciones)
        accion = "nuevo" if tactica.finished() else "entrenar"
        self.pon_toolbar("terminar", accion, "borrar")

        # Colocamos
        lyTB = Colocacion.H().control(self.tb).margen(0)
        ly = Colocacion.V().otro(lyTB).control(self.ghistorico).margen(3)

        self.setLayout(ly)

        self.register_grid(self.ghistorico)
        self.restore_video(siTam=False)

        self.ghistorico.gotop()

    def grid_num_datos(self, grid):
        return len(self.li_histo)

    def grid_doble_click(self, grid, row, o_column):
        if row == 0 and not self.tactica.finished():
            self.entrenar()

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        reg = self.li_histo[row]
        if col == "FINICIAL":
            fecha = reg["FINICIAL"]
            return Util.localDateT(fecha)
        elif col == "FFINAL":
            fecha = reg["FFINAL"]
            if fecha:
                return Util.localDateT(fecha)
            else:
                return "..."
        elif col == "TIME":
            fi = reg["FINICIAL"]
            ff = reg["FFINAL"]
            if not ff:
                ff = Util.today()
            dif = ff - fi
            t = int(dif.total_seconds())
            h = t // 3600
            m = (t - h * 3600) // 60
            d = h // 24
            h -= d * 24
            return "%d - %d:%02d" % (d, h, m)
        elif col == "POSICIONES":
            if "POS" in reg:
                posiciones = reg["POS"]
                if row == 0:
                    current_position = self.tactica.current_position()
                    if current_position is not None and current_position < posiciones:
                        return "%d/%d" % (current_position, posiciones)
                    else:
                        return str(posiciones)
                else:
                    return str(posiciones)
            return "-"
        elif col == "SECONDS":
            seconds = reg.get("SECONDS", None)
            if row == 0 and not seconds:
                seconds = self.tactica.segundosActivo()
            if seconds:
                hours = int(seconds / 3600)
                seconds -= hours * 3600
                minutes = int(seconds / 60)
                seconds -= minutes * 60
                return "%02d:%02d:%02d" % (hours, minutes, int(seconds))
            else:
                return "-"

        elif col == "ERRORS":
            if row == 0 and not self.tactica.finished():
                errors = self.tactica.erroresActivo()
            else:
                errors = reg.get("ERRORS", None)
            if errors is None:
                return "-"
            else:
                return "%d" % errors

        elif col == "REFERENCE":
            if row == 0 and not self.tactica.finished():
                reference = self.tactica.referenciaActivo()
            else:
                reference = reg.get("REFERENCE", "")
            return reference

    def process_toolbar(self):
        getattr(self, self.sender().key)()

    def terminar(self):
        self.save_video()
        self.reject()

    def nuevo(self):
        self.entrenar()

    def entrenar(self):
        if self.tactica.finished():
            menu = QTVarios.LCMenu(self)
            menu.opcion("auto", _("Default settings"), Iconos.PuntoAzul())
            menu.separador()
            menu.opcion("manual", _("Manual configuration"), Iconos.PuntoRojo())

            n = self.ghistorico.recno()
            if n >= 0:
                reg = self.li_histo[n]
                if "PUZZLES" in reg:
                    menu.separador()
                    menu.opcion("copia%d" % n, _("Copy configuration from current register"), Iconos.PuntoVerde())

            resp = menu.lanza()
            if not resp:
                return
            self.resultado = resp
        else:
            self.resultado = "seguir"
        self.save_video()
        self.accept()

    def borrar(self):
        li = self.ghistorico.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                self.tactica.borraListaHistorico(li)
                self.li_histo = self.tactica.historico()
        self.ghistorico.gotop()
        self.ghistorico.refresh()
        accion = "nuevo" if self.tactica.finished() else "entrenar"
        self.pon_toolbar("terminar", accion, "borrar")

    def pon_toolbar(self, *li_acciones):

        self.tb.clear()
        for k in li_acciones:
            self.tb.dic_toolbar[k].setVisible(True)
            self.tb.dic_toolbar[k].setEnabled(True)
            self.tb.addAction(self.tb.dic_toolbar[k])
            self.tb.addSeparator()

        self.tb.li_acciones = li_acciones
        self.tb.update()


class WConfTactics(QtWidgets.QWidget):
    def __init__(self, owner, tactica, ncopia=None):
        QtWidgets.QWidget.__init__(self)

        self.owner = owner
        self.tacticaINI = tactica
        if ncopia is not None:
            reg_historico = tactica.historico()[ncopia]
        else:
            reg_historico = None

        # Total por ficheros
        self.liFTOTAL = tactica.calculaTotales()
        total = sum(self.liFTOTAL)

        # N. puzzles
        if reg_historico:
            num = reg_historico["PUZZLES"]
        else:
            num = tactica.puzzles
        if not num or num > total:
            num = total

        lb_puzzles = Controles.LB(self, _("Max number of puzzles in each block") + ": ")
        self.sb_puzzles = Controles.SB(self, num, 1, total)

        # Reference
        lb_reference = Controles.LB(self, _("Reference") + ": ")
        self.ed_reference = Controles.ED(self)

        # Iconos
        ico_mas = Iconos.Add()
        ico_menos = Iconos.Delete()
        ico_cancel = Iconos.CancelarPeque()
        ico_reset = Iconos.MoverAtras()

        def tb_gen(prev):
            li_acciones = (
                (_("Add"), ico_mas, "%s_add" % prev),
                (_("Delete"), ico_menos, "%s_delete" % prev),
                None,
                (_("Delete all"), ico_cancel, "%s_delete_all" % prev),
                None,
                (_("Reset"), ico_reset, "%s_reset" % prev),
                None,
            )
            tb = Controles.TB(self, li_acciones, icon_size=16, with_text=False)
            return tb

        f = Controles.TipoLetra(peso=75)

        # Repeticiones de cada puzzle
        if reg_historico:
            self.liJUMPS = reg_historico["JUMPS"][:]
        else:
            self.liJUMPS = tactica.jumps[:]
        tb = tb_gen("jumps")
        o_col = Columnas.ListaColumnas()
        o_col.nueva("NUMBER", _("Repetition"), 80, align_center=True)
        o_col.nueva(
            "JUMPS_SEPARATION", _("Separation"), 80, align_center=True, edicion=Delegados.LineaTexto(siEntero=True)
        )
        self.grid_jumps = Grid.Grid(self, o_col, siSelecFilas=True, is_editable=True, xid="j")
        self.grid_jumps.setMinimumWidth(self.grid_jumps.anchoColumnas() + 20)
        ly = Colocacion.V().control(tb).control(self.grid_jumps)
        gb_jumps = Controles.GB(self, _("Repetitions of each puzzle"), ly).ponFuente(f)
        self.grid_jumps.gotop()

        # Repeticion del bloque
        if reg_historico:
            self.liREPEAT = reg_historico["REPEAT"][:]
        else:
            self.liREPEAT = tactica.repeat[:]
        tb = tb_gen("repeat")
        o_col = Columnas.ListaColumnas()
        o_col.nueva("NUMBER", _("Block"), 40, align_center=True)
        self.liREPEATtxt = (_("Original"), _("Random"), _("Previous"))
        o_col.nueva("REPEAT_ORDER", _("Order"), 100, align_center=True, edicion=Delegados.ComboBox(self.liREPEATtxt))
        self.grid_repeat = Grid.Grid(self, o_col, siSelecFilas=True, is_editable=True, xid="r")
        self.grid_repeat.setMinimumWidth(self.grid_repeat.anchoColumnas() + 20)
        ly = Colocacion.V().control(tb).control(self.grid_repeat)
        gb_repeat = Controles.GB(self, _("Blocks"), ly).ponFuente(f)
        self.grid_repeat.gotop()

        # Penalizaciones
        if reg_historico:
            self.liPENAL = reg_historico["PENALIZATION"][:]
        else:
            self.liPENAL = tactica.penalization[:]
        tb = tb_gen("penal")
        o_col = Columnas.ListaColumnas()
        o_col.nueva("NUMBER", _("N."), 20, align_center=True)
        o_col.nueva(
            "PENAL_POSITIONS", _("Positions"), 100, align_center=True, edicion=Delegados.LineaTexto(siEntero=True)
        )
        o_col.nueva("PENAL_%", _("Affected"), 100, align_center=True)
        self.grid_penal = Grid.Grid(self, o_col, siSelecFilas=True, is_editable=True, xid="p")
        self.grid_penal.setMinimumWidth(self.grid_penal.anchoColumnas() + 20)
        ly = Colocacion.V().control(tb).control(self.grid_penal)
        gb_penal = Controles.GB(self, _("Penalties"), ly).ponFuente(f)
        self.grid_penal.gotop()

        # ShowText
        if reg_historico:
            self.liSHOWTEXT = reg_historico["SHOWTEXT"][:]
        else:
            self.liSHOWTEXT = tactica.showtext[:]
        tb = tb_gen("show")
        o_col = Columnas.ListaColumnas()
        self.liSHOWTEXTtxt = (_("No"), _("Yes"))
        o_col.nueva("NUMBER", _("N."), 20, align_center=True)
        o_col.nueva(
            "SHOW_VISIBLE", _("Visible"), 100, align_center=True, edicion=Delegados.ComboBox(self.liSHOWTEXTtxt)
        )
        o_col.nueva("SHOW_%", _("Affected"), 100, align_center=True)
        self.grid_show = Grid.Grid(self, o_col, siSelecFilas=True, is_editable=True, xid="s")
        self.grid_show.setMinimumWidth(self.grid_show.anchoColumnas() + 20)
        ly = Colocacion.V().control(tb).control(self.grid_show)
        gbShow = Controles.GB(self, _("Show the reference associated with each puzzle"), ly).ponFuente(f)
        self.grid_show.gotop()

        # Reinforcement
        if reg_historico:
            self.reinforcement_errors = reg_historico["REINFORCEMENT_ERRORS"]
            self.reinforcement_cycles = reg_historico["REINFORCEMENT_CYCLES"]
        else:
            self.reinforcement_errors = tactica.reinforcement_errors
            self.reinforcement_cycles = tactica.reinforcement_cycles

        lb_r_errors = Controles.LB(self, _("Accumulated errors to launch reinforcement") + ": ")
        li_opciones = [(_("Disable"), 0), ("5", 5), ("10", 10), ("15", 15), ("20", 20)]
        self.cb_reinf_errors = Controles.CB(self, li_opciones, self.reinforcement_errors)
        lb_r_cycles = Controles.LB(self, _("Cycles") + ": ")
        self.sb_reinf_cycles = Controles.SB(self, self.reinforcement_cycles, 1, 10)
        ly = (
            Colocacion.H()
            .control(lb_r_errors)
            .control(self.cb_reinf_errors)
            .espacio(30)
            .control(lb_r_cycles)
            .control(self.sb_reinf_cycles)
        )
        gb_reinforcement = Controles.GB(self, _("Reinforcement"), ly).ponFuente(f)

        self.chb_advanced = Controles.CHB(self, _("Advanced mode"), False).ponFuente(f)
        ly_gb_adv = Colocacion.H().control(gb_reinforcement).espacio(20).control(self.chb_advanced)

        # Files
        if reg_historico:
            self.liFILES = reg_historico["FILESW"][:]
        else:
            self.liFILES = []
            for num, (fich, w, d, h) in enumerate(tactica.filesw):
                if not d or d < 1:
                    d = 1
                if not h or h > self.liFTOTAL[num] or h < 1:
                    h = self.liFTOTAL[num]
                if d > h:
                    d, h = h, d
                self.liFILES.append([fich, w, d, h])
        o_col = Columnas.ListaColumnas()
        o_col.nueva("FILE", _("File"), 220, align_center=True)
        o_col.nueva("WEIGHT", _("Weight"), 100, align_center=True, edicion=Delegados.LineaTexto(siEntero=True))
        o_col.nueva("TOTAL", _("Total"), 100, align_center=True)
        o_col.nueva("FROM", _("From"), 100, align_center=True, edicion=Delegados.LineaTexto(siEntero=True))
        o_col.nueva("TO", _("To"), 100, align_center=True, edicion=Delegados.LineaTexto(siEntero=True))
        self.grid_files = Grid.Grid(self, o_col, siSelecFilas=True, is_editable=True, xid="f")
        self.grid_files.setMinimumWidth(self.grid_files.anchoColumnas() + 20)
        ly = Colocacion.V().control(self.grid_files)
        gb_files = Controles.GB(self, _("FNS files"), ly).ponFuente(f)
        self.grid_files.gotop()

        # Layout
        ly_reference = Colocacion.H().control(lb_reference).control(self.ed_reference)
        ly_puzzles = Colocacion.H().control(lb_puzzles).control(self.sb_puzzles)
        ly = Colocacion.G()
        ly.otro(ly_puzzles, 0, 0).otro(ly_reference, 0, 1)
        ly.filaVacia(1, 5)
        ly.controld(gb_jumps, 2, 0).control(gb_penal, 2, 1)
        ly.filaVacia(3, 5)
        ly.controld(gb_repeat, 4, 0)
        ly.control(gbShow, 4, 1)
        ly.filaVacia(5, 5)
        ly.otro(ly_gb_adv, 6, 0, 1, 2)
        ly.filaVacia(6, 5)
        ly.control(gb_files, 7, 0, 1, 2)

        layout = Colocacion.V().espacio(10).otro(ly)

        self.setLayout(layout)

        self.grid_repeat.gotop()

    def process_toolbar(self):
        getattr(self, self.sender().key)()

    def grid_num_datos(self, grid):
        xid = grid.id
        if xid == "j":
            return len(self.liJUMPS)
        if xid == "r":
            return len(self.liREPEAT)
        if xid == "p":
            return len(self.liPENAL)
        if xid == "s":
            return len(self.liSHOWTEXT)
        if xid == "f":
            return len(self.liFILES)

    def etiPorc(self, row, numFilas):
        if numFilas == 0:
            return "100%"
        p = 100.0 / numFilas
        de = p * row
        a = p * (row + 1)
        return "%d%%  -  %d%%" % (int(de), int(a))

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        if col == "NUMBER":
            return str(row + 1)
        if col == "JUMPS_SEPARATION":
            return str(self.liJUMPS[row])
        elif col == "REPEAT_ORDER":
            n = self.liREPEAT[row]
            if row == 0:
                if n == 2:
                    self.liREPEAT[0] = 0
                    n = 0
            return self.liREPEATtxt[n]
        elif col == "PENAL_POSITIONS":
            return str(self.liPENAL[row])
        elif col == "PENAL_%":
            return self.etiPorc(row, len(self.liPENAL))
        elif col == "SHOW_VISIBLE":
            n = self.liSHOWTEXT[row]
            return self.liSHOWTEXTtxt[n]
        elif col == "SHOW_%":
            return self.etiPorc(row, len(self.liSHOWTEXT))
        elif col == "FILE":
            return self.liFILES[row][0]
        elif col == "WEIGHT":
            return str(self.liFILES[row][1])
        elif col == "TOTAL":
            return str(self.liFTOTAL[row])
        elif col == "FROM":
            return str(self.liFILES[row][2])
        elif col == "TO":
            return str(self.liFILES[row][3])

    def grid_setvalue(self, grid, row, o_column, valor):
        xid = grid.id
        if xid == "j":
            self.liJUMPS[row] = int(valor)
        elif xid == "r":
            self.liREPEAT[row] = self.liREPEATtxt.index(valor)
        elif xid == "p":
            self.liPENAL[row] = int(valor)
        elif xid == "s":
            self.liSHOWTEXT[row] = self.liSHOWTEXTtxt.index(valor)
        elif xid == "f":
            col = o_column.key
            n = int(valor)
            if col == "WEIGHT":
                if n > 0:
                    self.liFILES[row][1] = n
            elif 0 < n <= self.liFTOTAL[row]:
                if col == "FROM":
                    if n <= self.liFILES[row][3]:
                        self.liFILES[row][2] = n
                elif col == "TO":
                    if n >= self.liFILES[row][2]:
                        self.liFILES[row][3] = n

    def resultado(self):
        tactica = self.tacticaINI
        tactica.puzzles = int(self.sb_puzzles.valor())
        tactica.reference = self.ed_reference.texto().strip()
        tactica.jumps = self.liJUMPS
        tactica.repeat = self.liREPEAT
        tactica.penalization = self.liPENAL
        tactica.showtext = self.liSHOWTEXT
        tactica.filesw = self.liFILES
        tactica.reinforcement_errors = self.cb_reinf_errors.valor()
        tactica.reinforcement_cycles = self.sb_reinf_cycles.valor()
        tactica.advanced = self.chb_advanced.valor()
        return tactica

    def jumps_add(self):
        n = len(self.liJUMPS)
        if n == 0:
            x = 3
        else:
            x = self.liJUMPS[-1] * 2
        self.liJUMPS.append(x)
        self.grid_jumps.refresh()
        self.grid_jumps.goto(n, 0)

    def jumps_delete(self):
        x = self.grid_jumps.recno()
        if x >= 0:
            del self.liJUMPS[x]
            self.grid_jumps.refresh()
            n = len(self.liJUMPS)
            if n:
                self.grid_jumps.goto(x if x < n else n - 1, 0)
                self.grid_jumps.refresh()

    def jumps_delete_all(self):
        self.liJUMPS = []
        self.grid_jumps.refresh()

    def jumps_reset(self):
        self.liJUMPS = self.tacticaINI.jumps[:]
        self.grid_jumps.gotop()
        self.grid_jumps.refresh()

    def repeat_add(self):
        n = len(self.liREPEAT)
        self.liREPEAT.append(0)
        self.grid_repeat.goto(n, 0)

    def repeat_delete(self):
        x = self.grid_repeat.recno()
        n = len(self.liREPEAT)
        if x >= 0 and n > 1:
            del self.liREPEAT[x]
            self.grid_repeat.refresh()
            x = x if x < n else n - 1
            self.grid_repeat.goto(x, 0)
            self.grid_repeat.refresh()

    def repeat_delete_all(self):
        self.liREPEAT = [0]
        self.grid_repeat.refresh()

    def repeat_reset(self):
        self.liREPEAT = self.tacticaINI.repeat[:]
        self.grid_repeat.gotop()
        self.grid_repeat.refresh()

    def penal_add(self):
        n = len(self.liPENAL)
        if n == 0:
            x = 1
        else:
            x = self.liPENAL[-1] + 1
        self.liPENAL.append(x)
        self.grid_penal.refresh()
        self.grid_penal.goto(n, 0)

    def penal_delete(self):
        x = self.grid_penal.recno()
        if x >= 0:
            del self.liPENAL[x]
            self.grid_penal.refresh()
            n = len(self.liPENAL)
            if n:
                self.grid_penal.goto(x if x < n else n - 1, 0)
                self.grid_penal.refresh()

    def penal_delete_all(self):
        self.liPENAL = []
        self.grid_penal.refresh()

    def penal_reset(self):
        self.liPENAL = self.tacticaINI.penalization[:]
        self.grid_penal.gotop()
        self.grid_penal.refresh()

    def show_add(self):
        n = len(self.liSHOWTEXT)
        self.liSHOWTEXT.append(1)
        self.grid_show.goto(n, 0)

    def show_delete(self):
        x = self.grid_show.recno()
        n = len(self.liSHOWTEXT)
        if x >= 0 and n > 1:
            del self.liSHOWTEXT[x]
            self.grid_show.refresh()
            x = x if x < n else n - 1
            self.grid_show.goto(x, 0)
            self.grid_show.refresh()

    def show_delete_all(self):
        self.liSHOWTEXT = [1]
        self.grid_show.refresh()

    def show_reset(self):
        self.liSHOWTEXT = self.tacticaINI.showtext[:]
        self.grid_show.gotop()
        self.grid_show.refresh()


class WEditaTactica(LCDialog.LCDialog):
    def __init__(self, owner, tactica, ncopia):

        LCDialog.LCDialog.__init__(
            self, owner, _X(_("Configuration of %1"), tactica.title), Iconos.Tacticas(), "editTactica"
        )

        self.tactica = tactica

        li_acciones = (
            (_("Accept"), Iconos.Aceptar(), "aceptar"),
            None,
            (_("Cancel"), Iconos.Cancelar(), "cancelar"),
            None,
            (_("Help"), Iconos.AyudaGR(), "get_help"),
            None,
        )
        tb = Controles.TB(self, li_acciones)

        self.wtactic = WConfTactics(self, tactica, ncopia)

        layout = Colocacion.V().control(tb).control(self.wtactic)
        self.setLayout(layout)
        # self.restore_video()

    def process_toolbar(self):
        self.save_video()
        accion = self.sender().key
        if accion == "aceptar":
            self.accept()

        elif accion == "cancelar":
            self.reject()

        elif accion == "get_help":
            self.get_help()

    def get_help(self):
        menu = QTVarios.LCMenu(self)

        nico = QTVarios.rondoColores()

        for opcion, txt in (
            (self.remove_jumps, _("Without repetitions of each puzzle")),
            (self.remove_repeat, _("Without repetitions of block")),
            (self.remove_penalization, _("Without penalties")),
        ):
            menu.opcion(opcion, txt, nico.otro())
            menu.separador()

        resp = menu.lanza()
        if resp:
            resp()

    def remove_jumps(self):
        self.wtactic.jumps_delete_all()

    def remove_repeat(self):
        self.wtactic.repeat_delete_all()

    def remove_penalization(self):
        self.wtactic.penal_delete_all()


def edit1tactica(owner, tactica, ncopia):
    w = WEditaTactica(owner, tactica, ncopia)
    if w.exec_():
        tresp = w.wtactic.resultado()

        tactica.puzzles = tresp.puzzles
        tactica.jumps = tresp.jumps
        tactica.repeat = tresp.repeat
        tactica.penalization = tresp.penalization
        tactica.showtext = tresp.showtext
        tactica.advanced = tresp.advanced
        tactica.remove_reinforcement()

        return True
    else:
        return False
