import webbrowser

import Code
from Code.QT import Colocacion
from Code.QT import Grid, Columnas, Delegados
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WConfAnalysis(LCDialog.LCDialog):
    def __init__(self, owner, manager):
        titulo = _("Analysis configuration parameters")
        icono = Iconos.ConfAnalysis()
        extparam = "configuration_analysis"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.manager = manager
        self.configuration = Code.configuration

        self.dic_eval_default = self.configuration.dic_eval_default
        self.dic_eval = self.configuration.read_eval()
        self.dic_eval_keys = self.configuration.dic_eval_keys()
        self.li_keys = list(self.dic_eval_keys.keys())

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("KEY", _("Name"), 160, align_center=True)
        o_columns.nueva("VALUE", _("Value"), 160, edicion=Delegados.LineaTexto(self), align_center=True)
        o_columns.nueva("DEFAULT", _("By default"), 80, align_center=True)
        o_columns.nueva("MIN", _("Minimum"), 80, align_center=True)
        o_columns.nueva("MAX", _("Maximum"), 80, align_center=True)
        o_columns.nueva("TYPE", _("Type"), 80, align_center=True)
        self.grid_keys = Grid.Grid(self, o_columns, xid="keys", siSelecFilas=False, is_editable=True)
        self.grid_keys.setFixedWidth(self.grid_keys.anchoColumnas() + 20)

        tb = QTVarios.LCTB(self)
        tb.new(_("Quit"), Iconos.FinPartida(), self.close)
        tb.new(_("By default"), Iconos.Defecto(), self.default)
        tb.new(_("Help"), Iconos.AyudaGR(), self.ayuda)

        ly = Colocacion.V().control(tb).control(self.grid_keys)
        self.setLayout(ly)

        self.restore_video()

    def close(self):
        self.save_video()
        LCDialog.LCDialog.close(self)

    def closeEvent(self, event):
        self.save_video()

    @staticmethod
    def ayuda():
        url = "https://lucaschess.blogspot.com/2022/10/setting-analysis-parameters.html"
        webbrowser.open(url)

    def default(self):
        if QTUtil2.pregunta(self, _("Are you sure you want to set the default configuration?")):
            for key, value in self.dic_eval_default.items():
                setattr(self.configuration, "x_eval_%s" % key, value)
            self.configuration.graba()
            self.dic_eval = self.configuration.read_eval()
            self.grid_keys.refresh()
            if self.manager:
                self.manager.refresh_analysis()

    def grid_num_datos(self, grid):
        return len(self.li_keys)

    def grid_dato(self, grid, row, o_column):
        field = o_column.key
        key = self.li_keys[row]
        if field == "KEY":
            return key
        else:
            xfrom, xto, xtype = self.dic_eval_keys[key]
            if field in ("VALUE", "DEFAULT"):
                v = self.dic_eval[key] if field == "VALUE" else self.dic_eval_default[key]
                if xtype == "int":
                    return str(int(v))
                else:
                    return "%0.02f" % v
            if field == "MIN":
                return str(xfrom)
            if field == "MAX":
                return str(xto)
            if field == "TYPE":
                return xtype

    def grid_setvalue(self, grid, row, o_column, valor):
        key = self.li_keys[row]
        try:
            valor = float(valor)
        except ValueError:
            return

        xfrom, xto, xtype = self.dic_eval_keys[key]
        if xtype == "int":
            valor = int(valor)

        if valor > xto or valor < xfrom:
            return

        setattr(self.configuration, "x_eval_" + key, valor)
        self.dic_eval[key] = valor
        self.configuration.graba()
        if self.manager:
            self.manager.refresh_analysis()
