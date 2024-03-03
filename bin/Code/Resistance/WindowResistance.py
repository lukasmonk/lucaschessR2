from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2


class WResistance(LCDialog.LCDialog):
    def __init__(self, owner, resistance):

        self.resistance = resistance

        # Dialogo ---------------------------------------------------------------
        icono = Iconos.Resistencia()
        titulo = _("Resistance Test")
        tipo = resistance.tipo
        if tipo:
            titulo += "-" + _("Blindfold chess")
            if tipo == "p1":
                titulo += "-" + _("Hide only our pieces")
            elif tipo == "p2":
                titulo += "-" + _("Hide only opponent pieces")
        extparam = "boxing"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)
        # self.setStyleSheet("QWidget { background: #AFC3D7 }")

        # Tool bar ---------------------------------------------------------------
        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Remove data"), Iconos.Borrar(), self.borrar),
            None,
            (_("Config"), Iconos.Configurar(), self.configurar),
        ]
        tb = Controles.TBrutina(self, li_acciones, background="#AFC3D7")

        # Texto explicativo ----------------------------------------------------
        self.lb = Controles.LB(self)
        self.set_textAyuda()
        self.lb.set_background("#F5F0CF")

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ENGINE", _("Engine"), 198)
        o_columns.nueva("WHITE", _("White"), 200, align_center=True)
        o_columns.nueva("BLACK", _("Black"), 200, align_center=True)

        self.grid = grid = Grid.Grid(self, o_columns, siSelecFilas=True, background=None)
        self.grid.coloresAlternados()
        self.register_grid(grid)

        # Layout
        lyB = Colocacion.V().controlc(self.lb).control(self.grid).margen(3)
        layout = Colocacion.V().control(tb).otro(lyB).margen(0)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=677, altoDefecto=562)

        self.grid.gotop()

        self.grid.setFocus()
        self.resultado = None

    def set_textAyuda(self):
        txt = self.resistance.rotuloActual(True)
        self.lb.set_text(
            '<center><b>%s<br><font color="red">%s</red></b></center>'
            % (txt, _("Double click in any cell to begin to play"))
        )

    def grid_num_datos(self, grid):
        return self.resistance.num_engines()

    def grid_dato(self, grid, row, o_column):
        key = o_column.key
        if key == "ENGINE":
            return self.resistance.dameEtiEngine(row)
        else:
            return self.resistance.dameEtiRecord(key, row)

    def grid_doble_click(self, grid, row, column):
        key = column.key
        if key != "ENGINE":
            self.play(key)

    def play(self, key):
        self.save_video()
        self.resultado = self.grid.recno(), key
        self.accept()

    def borrar(self):
        num_engine = self.grid.recno()
        if QTUtil2.pregunta(self, _X(_("Remove data from %1 ?"), self.resistance.dameEtiEngine(num_engine))):
            self.resistance.borraRegistros(num_engine)

    def terminar(self):
        self.save_video()
        self.accept()

    def configurar(self):
        seconds, puntos, maxerror = self.resistance.actual()

        separador = FormLayout.separador

        li_gen = [separador]

        config = FormLayout.Spinbox(_("Time engines think in seconds") + ":\n %s=5.0" % _("By default"), 1, 99999, 80)
        li_gen.append((config, seconds))

        li_gen.append(separador)

        config = FormLayout.Spinbox(_("Max lost centipawns in total") + ":\n %s= 100" % _("By default"), 10, 99999, 80)
        li_gen.append((config, puntos))

        li_gen.append(separador)

        config = FormLayout.Spinbox(
            _("Max lost centipawns in a single move")
            + ":\n%s= %s" % (_("By default"), _("0 = not consider this limit")),
            0,
            1000,
            80,
        )
        li_gen.append((config, maxerror))

        resultado = FormLayout.fedit(li_gen, title=_("Config"), parent=self, icon=Iconos.Configurar())
        if resultado:
            accion, li_resp = resultado
            seconds, puntos, maxerror = li_resp
            self.resistance.cambiaconfiguration(seconds, puntos, maxerror)
            self.set_textAyuda()
            self.grid.refresh()
            return li_resp[0]


def windowResistance(window, resistance):
    w = WResistance(window, resistance)
    if w.exec_():
        return w.resultado
    else:
        return None
