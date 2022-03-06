from PySide2 import QtSvg, QtCore

from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Routes import Routes


class WTranssiberian(LCDialog.LCDialog):
    def __init__(self, procesador):

        route = self.route = Routes.Transsiberian(procesador.configuration)

        titulo = "%s (%d)" % (_("Transsiberian Railway"), route.level)
        icono = Iconos.Train()
        extparam = "transsiberian"
        LCDialog.LCDialog.__init__(self, procesador.main_window, titulo, icono, extparam)

        self.procesador = procesador
        wsvg = QtSvg.QSvgWidget()
        x = self.route.get_txt().encode("utf-8")
        wsvg.load(QtCore.QByteArray(x))
        wsvg.setFixedSize(762, 762.0 * 658.0 / 1148.0)
        lySVG = Colocacion.H().relleno(1).control(wsvg).relleno(1)

        # Title
        lbTit = self.LINE(_("Moscow"), _("Vladivostok"), 14, 500).altoFijo(26)
        lbKM = self.KM(route.total_km, 12, 500).altoFijo(26)
        self.set_style("White", "#33322C", lbTit, lbKM)
        lbKMdone = self.KM(route.km, 12, 500).altoFijo(26)
        self.set_border(lbKMdone)
        lyTitle = Colocacion.H().control(lbTit).control(lbKM).control(lbKMdone)

        if route.is_ended():
            self.init_ended(route, lyTitle, lySVG)
        else:
            self.init_working(route, lyTitle, lySVG)

        self.restore_video(siTam=False)

    def LINE(self, st_from, st_to, puntos, peso=50):
        return Controles.LB(_("From %s to %s") % (st_from, st_to)).align_center().ponTipoLetra(puntos=puntos, peso=peso)

    def KM(self, km, puntos, peso=50):
        return Controles.LB(Routes.km_mi(km, self.route.is_miles)).align_center().ponTipoLetra(puntos=puntos, peso=peso).anchoFijo(100)

    def set_border(self, *lb):
        for l in lb:
            l.setStyleSheet("QWidget { border-style: groove; border-width: 2px; border-color: LightSlateGray ;}")

    def set_style(self, fore, back, *lb):
        if fore:
            style = "QWidget { color: %s; background-color: %s}" % (fore, back)
        else:
            style = "QWidget { background-color: %s}" % back
        for l in lb:
            l.setStyleSheet(style)

    def init_working(self, route, lyTitle, lySVG):

        # Line
        line = route.get_line()
        tt = route.tool_tip_line()
        lbTip = Controles.LB(_("Stage") + " %d/%d" % (line.stage, route.num_stages)).ponTipoLetra(puntos=11).anchoFijo(120).align_center()
        lbTip.setToolTip(tt)
        lbTit = self.LINE(line.st_from.name, line.st_to.name, 11)
        lbTit.setToolTip(tt)
        lbKM = self.KM(line.km, 11)
        self.set_style("Black", "Cornsilk", lbTip, lbTit, lbKM)
        lbKM.setToolTip(tt)
        lbKMdone = self.KM(line.km_done(route.km), 11)
        self.set_border(lbKMdone)
        lyLine = Colocacion.H().control(lbTip).control(lbTit).control(lbKM).control(lbKMdone)

        # Track
        st_from, st_to = route.get_track()
        tt = route.tool_tip_track()
        lbTip = (
            Controles.LB(_("Track") + " %d/%d" % (route.num_track, line.num_stations)).ponTipoLetra(puntos=11).anchoFijo(120).align_center()
        )
        lbTip.setToolTip(tt)
        lbTit = self.LINE(st_from.name, st_to.name, 11)
        lbTit.setToolTip(tt)
        lbKM = self.KM(st_to.km - st_from.km, 11)
        lbKM.setToolTip(tt)
        self.set_style("Black", "#E6DFC6", lbTip, lbTit, lbKM)
        lbKMdone = self.KM(route.km - st_from.km, 11)
        self.set_border(lbKMdone)
        lyTrack = Colocacion.H().control(lbTip).control(lbTit).control(lbKM).control(lbKMdone)

        # State
        lbTip = Controles.LB(_("State")).ponTipoLetra(puntos=11, peso=200).anchoFijo(120).align_center()
        lbTit = Controles.LB(route.mens_state()).ponTipoLetra(puntos=11, peso=200).align_center()
        self.set_style("White", "#B2AE9A", lbTip, lbTit)
        lyState = Colocacion.H().control(lbTip).control(lbTit)

        # Next task
        texto, color = route.next_task()
        lbTip = Controles.LB(_("Next task")).ponTipoLetra(puntos=11, peso=500).anchoFijo(120).align_center()
        lbTit = Controles.LB(texto).ponTipoLetra(puntos=11, peso=500).align_center()
        self.set_style("White", color, lbTip, lbTit)
        lyTask = Colocacion.H().control(lbTip).control(lbTit)

        tb = QTVarios.LCTB(self, with_text=True, icon_size=32)
        tb.new(_("Play"), Iconos.Empezar(), self.play)
        tb.new(_("Config"), Iconos.Configurar(), self.config)
        tb.new(_("Close"), Iconos.MainMenu(), self.mainMenu)
        tb.setFixedWidth(206)
        lbTim = Controles.LB("%s: %s" % (_("Time"), route.time())).ponTipoLetra(puntos=11, peso=500).align_center().anchoFijo(206)
        lbTim.setToolTip(
            "%s %s\n%s %s\n%s %s\n%s %s"
            % (
                route.time(),
                _("Total"),
                route.time(Routes.PLAYING),
                _("Playing"),
                route.time(Routes.BETWEEN),
                _("Tactics"),
                route.time(Routes.ENDING),
                _("Endings"),
            )
        )

        self.set_style("White", color, lbTit)
        self.set_style("White", "#B2AE9A", lbTim)
        lyStTa = Colocacion.V().otro(lyState).otro(lyTask)
        lyTB = Colocacion.V().control(lbTim).control(tb)
        lyAll = Colocacion.H().otro(lyStTa).otro(lyTB)

        ly = Colocacion.V().otro(lyTitle).otro(lySVG).otro(lyLine).otro(lyTrack).otro(lyAll).relleno(1)
        self.setLayout(ly)

    def init_ended(self, route, lyTitle, lySVG):
        def ly(rt, va):
            lbrt = Controles.LB(rt).ponTipoLetra(puntos=11).align_center()
            lbva = Controles.LB(va).ponTipoLetra(puntos=11).align_center()
            self.set_style("Black", "#B2AE9A", lbrt)
            self.set_border(lbva)
            return Colocacion.H().control(lbrt).control(lbva)

        lyDB = ly(_("Starting date"), route.date_begin)
        lyDE = ly(_("Ending date"), route.date_end)

        tb = QTVarios.LCTB(self, with_text=True, icon_size=32)
        tb.new(_("Config"), Iconos.Configurar(), self.config)
        tb.new(_("Close"), Iconos.MainMenu(), self.mainMenu)

        lyTT = ly(_("Total time"), route.time())
        lyTP = ly(_("Playing"), route.time(Routes.PLAYING))
        lyTC = ly(_("Tactics"), route.time(Routes.BETWEEN))
        lyTE = ly(_("Endings"), route.time(Routes.ENDING))

        lyT = Colocacion.V().otro(lyTT).otro(lyTP).otro(lyTC).otro(lyTE)

        lyD = Colocacion.V().otro(lyDB).otro(lyDE).control(tb)

        lyT_D = Colocacion.H().otro(lyT).otro(lyD)

        ly = Colocacion.V().otro(lyTitle).otro(lySVG).otro(lyT_D).relleno(1)
        self.setLayout(ly)

    def play(self):
        self.accept()
        self.procesador.playRoute(self.route)

    def mainMenu(self):
        self.reject()

    def config(self):
        menu = QTVarios.LCMenu(self)
        smenu = menu.submenu(_("Change the unit of measurement"), Iconos.Measure())
        is_miles = self.route.is_miles
        dico = {True: Iconos.Aceptar(), False: Iconos.PuntoVerde()}
        dkey = {True: None, False: "k"}
        smenu.opcion(dkey[not is_miles], _("Kilometres"), dico[not is_miles], is_disabled=not is_miles)
        smenu.opcion(dkey[is_miles], _("Miles (internally works in km)"), dico[is_miles], is_disabled=is_miles)

        menu.separador()
        smenu = menu.submenu(_("Tactics"), Iconos.Tacticas())
        dkey = {True: None, False: "g"}
        go_fast = self.route.go_fast
        smenu.opcion(dkey[not go_fast], _("Stop after solving"), dico[not go_fast], is_disabled=not go_fast)
        smenu.opcion(dkey[go_fast], _("Jump to the next after solving"), dico[go_fast], is_disabled=go_fast)

        if self.route.km:
            menu.separador()
            menu.opcion("rst", _("Return to the starting point"), Iconos.Delete())

        menu.separador()
        smenu = menu.submenu(_("Change level"), Iconos.Modificar())
        rondo = QTVarios.rondoPuntos()
        level = self.route.level
        for lv in range(1, 6):
            if lv != level:
                smenu.opcion("l%d" % lv, "%s %d" % (_("Level"), lv), rondo.otro())

        resp = menu.lanza()
        if resp:
            if resp == "rst":
                if QTUtil2.pregunta(self, _("Are you sure?")):
                    self.route.reset()
                else:
                    return
            elif resp == "k":
                self.route.change_measure()
            elif resp == "g":
                self.route.change_go_fast()
                return
            elif resp.startswith("l"):
                if QTUtil2.pregunta(self, _("Change level") + "\n" + _("Are you sure?")):
                    self.route.write_with_level()
                    n = int(resp[1])
                    self.route.set_level(n)
            self.reject()
            train_train(self.procesador)


def train_train(procesador):
    w = WTranssiberian(procesador)
    w.exec_()
