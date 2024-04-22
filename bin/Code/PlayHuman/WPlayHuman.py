import Code
from Code.Base.Constantes import GT_HUMAN
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WPlayHuman(LCDialog.LCDialog):
    def __init__(self):
        self.procesador = procesador = Code.procesador

        LCDialog.LCDialog.__init__(self, procesador.main_window, _("Play human vs human"), Iconos.HumanHuman(),
                                   "humanhuman")

        self.configuration = procesador.configuration
        font = Controles.FontType(puntos=self.configuration.x_font_points)

        self.dic = {}

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        self.lb_white = Controles.LB2P(self, _("White")).set_font(font)
        self.ed_white = Controles.ED(self, "").anchoMaximo(250).set_font(font)

        self.lb_black = Controles.LB2P(self, _("Black")).set_font(font)
        self.ed_black = Controles.ED(self, "").anchoMaximo(250).set_font(font)

        ly_players = Colocacion.G()
        ly_players.controld(self.lb_white, 0, 0).control(self.ed_white, 0, 1)
        ly_players.controld(self.lb_black, 1, 0).control(self.ed_black, 1, 1)

        gb_players = Controles.GB(self, _("Players"), ly_players)
        self.configuration.set_property(gb_players, "1")

        self.lb_minutos = Controles.LB(self, _("Total minutes") + ":").set_font(font)
        self.ed_minutos = Controles.ED(self).tipoFloat(10.0).set_font(font).anchoFijo(50*Code.factor_big_fonts)
        self.ed_segundos, self.lb_segundos = QTUtil2.spinbox_lb(
            self, 0, -999, 999, max_width=54*Code.factor_big_fonts, etiqueta=_("Seconds added per move"), fuente=font
        )
        ly_h = Colocacion.H()
        ly_h.control(self.lb_minutos).control(self.ed_minutos).espacio(30)
        ly_h.control(self.lb_segundos).control(self.ed_segundos).relleno()

        self.chb_tiempo = Controles.GB(self, _("Activate the time control"), ly_h)
        self.chb_tiempo.setCheckable(True)
        self.chb_tiempo.setChecked(True)
        self.configuration.set_property(self.chb_tiempo, "1")
        self.chb_tiempo.setMinimumWidth(440)
        self.chb_tiempo.setFont(font)

        ly = Colocacion.V()
        ly.control(tb)
        ly.control(gb_players)
        ly.control(self.chb_tiempo)

        if Code.eboard:
            self.chb_eboard = Controles.CHB(
                self, "%s: %s" % (_("Activate e-board"), self.configuration.x_digital_board), False
            ).set_font(font)
            ly.control(self.chb_eboard)

        # self.chb_analysis_bar = Controles.CHB(self, _("Activate the Analysis Bar"), False).set_font(font)
        # ly.control(self.chb_analysis_bar)

        self.chb_autorotate = Controles.CHB(self, _("Auto-rotate board"),
                                            Code.configuration.get_auto_rotate(GT_HUMAN)).set_font(font)
        ly.control(self.chb_autorotate)

        self.setLayout(ly)

        self.restore_video()

        self.var_to_save = "human_human"
        dic = self.configuration.read_variables(self.var_to_save)
        if dic:
            self.restore_dic(dic)

    def save_dic(self):
        Code.configuration.set_auto_rotate(GT_HUMAN, self.chb_autorotate.valor())
        return {
            "WHITE": self.ed_white.texto(),
            "BLACK": self.ed_black.texto(),
            "WITHTIME": self.chb_tiempo.isChecked(),
            "MINUTES": self.ed_minutos.textoFloat(),
            "SECONDS": self.ed_segundos.value(),
            "ACTIVATE_EBOARD": self.chb_eboard.valor() if Code.eboard else False,
            # "ANALYSIS_BAR": self.chb_analysis_bar.valor(),
        }

    def restore_dic(self, dic):
        dg = dic.get
        self.ed_white.set_text(dg("WHITE", ""))
        self.ed_black.set_text(dg("BLACK", ""))

        self.ed_minutos.ponFloat(float(dg("MINUTES", 10.0)))
        self.ed_segundos.setValue(dg("SECONDS", 0))
        self.chb_tiempo.setChecked(dg("WITHTIME", False))
        if Code.eboard:
            self.chb_eboard.set_value(dg("ACTIVATE_EBOARD", False))
        # self.chb_analysis_bar.set_value(dg("ANALYSIS_BAR", False))
        self.chb_autorotate.set_value(dg("AUTO_ROTATE", False))

    def aceptar(self):
        self.dic = self.save_dic()
        self.configuration.write_variables(self.var_to_save, self.dic)
        self.save_video()
        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()


def play_human():
    w = WPlayHuman()
    if w.exec_():
        return w.dic
    else:
        return None
