import os.path
import time

import FasterCode
from PySide2 import QtCore

import Code
from Code import Util
from Code.Base import Position
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL


class WControl(LCDialog.LCDialog):
    def __init__(self, procesador, path_bloque):

        LCDialog.LCDialog.__init__(
            self, procesador.main_window, _("The board at a glance"), Iconos.Gafas(), "visualizaBase"
        )

        self.procesador = procesador
        self.configuration = procesador.configuration

        self.path_bloque = path_bloque

        file = Util.opj(self.configuration.carpeta_results, os.path.basename(path_bloque) + "db")
        self.historico = UtilSQL.DictSQL(file)
        self.li_histo = self.calcListaHistorico()

        # Historico
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("SITE", _("Site"), 100, align_center=True)
        o_columns.nueva("DATE", _("Date"), 100, align_center=True)
        o_columns.nueva("LEVEL", _("Level"), 80, align_center=True)
        o_columns.nueva("TIME", _("Time used"), 80, align_center=True)
        o_columns.nueva("ERRORS", _("Errors"), 80, align_center=True)
        o_columns.nueva("INTERVAL", _("Interval"), 100, align_center=True)
        o_columns.nueva("POSITION", _("Position"), 80, align_center=True)
        o_columns.nueva("COLOR", _("Square color"), 80, align_center=True)
        o_columns.nueva("ISATTACKED", _("Is attacked?"), 80, align_center=True)
        o_columns.nueva("ISATTACKING", _("Is attacking?"), 80, align_center=True)
        self.ghistorico = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True)
        self.ghistorico.setMinimumWidth(self.ghistorico.anchoColumnas() + 20)

        # Tool bar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Play"), Iconos.Empezar(), self.play),
            None,
            (_("New"), Iconos.Nuevo(), self.new),
            None,
            (_("Remove"), Iconos.Borrar(), self.remove),
            None,
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        # Colocamos
        ly = Colocacion.V().control(self.tb).control(self.ghistorico).margen(3)

        self.setLayout(ly)

        self.register_grid(self.ghistorico)
        self.restore_video()
        self.ghistorico.gotop()

    def grid_num_datos(self, grid):
        return len(self.li_histo)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        key = self.li_histo[row]
        reg = self.historico[key]
        v = reg[col]
        if col == "DATE":
            v = Util.localDate(reg[col])
        elif col == "ERRORS":
            v = "%d" % v
        elif col == "TIME":
            if v > 60:
                m = v / 60
                s = v % 60
                v = "%d'%d\"" % (m, s)
            else:
                v = '%d"' % v
        elif col == "INTERVAL":
            v = '%d"' % v
            if reg["INTERVALPIECE"]:
                v = "x %s" % v
        elif col == "LEVEL":
            v = _("Finished") if v == 0 else str(v)
        elif col in ("POSITION", "COLOR", "ISATTACKED", "ISATTACKING"):
            v = _("Yes") if v else _("No")
        return v

    def calcListaHistorico(self):
        return self.historico.keys(si_ordenados=True, si_reverse=True)

    def terminar(self):
        self.save_video()
        self.historico.close()
        self.reject()

    def play(self):
        if not self.li_histo:
            return self.new()

        recno = self.ghistorico.recno()
        if recno >= 0:
            key = self.li_histo[recno]
            reg = self.historico[key]
            if reg["LEVEL"] > 0:
                return self.work(recno)

    def new(self):
        recno = self.ghistorico.recno()
        if recno >= 0:
            key = self.li_histo[recno]
            reg = self.historico[key]
            sitePre = reg["SITE"]
            intervaloPre = reg["INTERVAL"]
            intervaloPorPiezaPre = reg["INTERVALPIECE"]
            esatacadaPre = reg["ISATTACKED"]
            esatacantePre = reg["ISATTACKING"]
            posicionPre = reg["POSITION"]
            colorPre = reg["COLOR"]
        else:
            recno = 0
            sitePre = None
            intervaloPre = 3
            intervaloPorPiezaPre = True
            esatacadaPre = False
            esatacantePre = False
            posicionPre = False
            colorPre = False

        # Datos
        li_gen = [(None, None)]

        # # Site
        f = open(self.path_bloque)
        liData = [x.split("|") for x in f.read().split("\n")]
        f.close()
        liSites = []
        sitePreNum = -1
        for n, uno in enumerate(liData):
            site = uno[0]
            if site:
                if sitePre and site == sitePre:
                    sitePreNum = n
                liSites.append((site, n))
        liSites = sorted(liSites, key=lambda st: st[0])
        config = FormLayout.Combobox(_("Site"), liSites)
        if sitePreNum == -1:
            sitePreNum = liSites[0][0]
        li_gen.append((config, sitePreNum))

        li_gen.append((None, None))

        # # Intervals
        li_gen.append((None, _("Seconds of every glance") + ":"))
        li_gen.append((FormLayout.Spinbox(_("Second(s)"), 1, 100, 50), intervaloPre))

        liTypes = ((_("By piece"), True), (_("Time fixed"), False))
        config = FormLayout.Combobox(_("Type"), liTypes)
        li_gen.append((config, intervaloPorPiezaPre))

        li_gen.append((None, None))

        li_gen.append((None, _("Ask for") + ":"))
        li_gen.append((_("Position") + ":", posicionPre))
        li_gen.append((_("Square color") + ":", colorPre))
        li_gen.append((_("Is attacked?") + ":", esatacadaPre))
        li_gen.append((_("Is attacking?") + ":", esatacantePre))

        resultado = FormLayout.fedit(
            li_gen, title=_("Configuration"), parent=self, icon=Iconos.Gafas(), anchoMinimo=360
        )
        if resultado:
            accion, li_gen = resultado

            siteNum, intervalo, intervaloPorPieza, position, color, esatacada, esatacante = li_gen

            dicdatos = {}
            f = dicdatos["DATE"] = Util.today()
            dicdatos["FENS"] = liData[siteNum][1:]
            dicdatos["SITE"] = liData[siteNum][0]
            dicdatos["INTERVAL"] = intervalo
            dicdatos["INTERVALPIECE"] = intervaloPorPieza
            dicdatos["ISATTACKED"] = esatacada
            dicdatos["ISATTACKING"] = esatacante
            dicdatos["POSITION"] = position
            dicdatos["COLOR"] = color
            dicdatos["ERRORS"] = 0
            dicdatos["TIME"] = 0
            dicdatos["LEVEL"] = 1

            key = Util.dtosext(f)
            self.historico[key] = dicdatos
            self.li_histo.insert(0, key)
            self.ghistorico.refresh()
            self.ghistorico.gotop()

            self.work(recno)

    def work(self, recno):
        key = self.li_histo[recno]
        dicdatos = self.historico[key]

        w = WPlay(self, dicdatos)
        w.exec_()

        self.historico[key] = dicdatos
        self.ghistorico.refresh()

    def grid_doble_click(self, grid, row, column):
        key = self.li_histo[row]
        dicdatos = self.historico[key]
        if dicdatos["LEVEL"]:
            self.work(row)

    def remove(self):
        li = self.ghistorico.recnosSeleccionados()
        if len(li) > 0:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                um = QTUtil2.one_moment_please(self)
                for row in li:
                    key = self.li_histo[row]
                    del self.historico[key]
                self.historico.pack()
                self.li_histo = self.calcListaHistorico()
                um.final()
                self.ghistorico.refresh()


class WPlay(LCDialog.LCDialog):
    def __init__(self, owner, dicdatos):

        self.dicdatos = dicdatos

        site = dicdatos["SITE"]
        self.level = dicdatos["LEVEL"]
        self.intervalo = dicdatos["INTERVAL"]
        self.intervaloPorPieza = dicdatos["INTERVALPIECE"]
        self.esatacada = dicdatos["ISATTACKED"]
        self.esatacante = dicdatos["ISATTACKING"]
        self.position = dicdatos["POSITION"]
        self.color = dicdatos["COLOR"]
        self.errors = dicdatos["ERRORS"]
        self.time = dicdatos["TIME"]
        self.liFENs = dicdatos["FENS"]

        mas = "x" if self.intervaloPorPieza else ""
        titulo = '%s (%s%d")' % (site, mas, self.intervalo)

        super(WPlay, self).__init__(owner, titulo, Iconos.Gafas(), "visualplay")

        self.procesador = owner.procesador
        self.configuration = self.procesador.configuration

        # Tiempo en board
        intervaloMax = self.intervalo
        if self.intervaloPorPieza:
            intervaloMax *= 32

        # Board
        config_board = self.configuration.config_board("VISUALPLAY", 48)
        self.board = Board.Board(self, config_board)
        self.board.crea()

        lyT = Colocacion.V().control(self.board)

        self.gbBoard = Controles.GB(self, "", lyT)

        # entradas
        ly = Colocacion.G()

        self.posPosicion = None
        self.posColor = None
        self.posIsAttacked = None
        self.posIsAttacking = None

        lista = [_("Piece")]
        if self.position:
            lista.append(_("Position"))
        if self.color:
            lista.append(_("Square color"))
        if self.esatacada:
            lista.append(_("Is attacked?"))
        if self.esatacante:
            lista.append(_("Is attacking?"))
        self.liLB2 = []
        for col, eti in enumerate(lista):
            ly.control(Controles.LB(self, eti), 0, col + 1)
            lb2 = Controles.LB(self, eti)
            ly.control(lb2, 0, col + len(lista) + 2)
            self.liLB2.append(lb2)
        elementos = len(lista) + 1

        liComboPieces = []
        for c in "PNBRQKpnbrqk":
            liComboPieces.append(("", c, self.board.piezas.icono(c)))

        self.pmBien = Iconos.pmAceptarPeque()
        self.pmMal = Iconos.pmCancelarPeque()
        self.pmNada = Iconos.pmPuntoAmarillo()

        self.liBloques = []
        for x in range(32):
            row = x % 16 + 1
            colPos = elementos if x > 15 else 0

            unBloque = []
            self.liBloques.append(unBloque)

            # # Solucion
            lb = Controles.LB(self, "").ponImagen(self.pmNada)
            ly.control(lb, row, colPos)
            unBloque.append(lb)

            # # Piezas
            colPos += 1
            cb = Controles.CB(self, liComboPieces, "P")
            # cb.setStyleSheet("* { min-height:32px }")
            cb.setIconSize(QtCore.QSize(20, 20))

            ly.control(cb, row, colPos)
            unBloque.append(cb)

            if self.position:
                ec = Controles.ED(self, "").caracteres(2).controlrx("(|[a-h][1-8])").anchoFijo(24).align_center()
                colPos += 1
                ly.controlc(ec, row, colPos)
                unBloque.append(ec)

            if self.color:
                cl = QTVarios.TwoImages(Iconos.pmBlancas(), Iconos.pmNegras())
                colPos += 1
                ly.controlc(cl, row, colPos)
                unBloque.append(cl)

            if self.esatacada:
                isat = QTVarios.TwoImages(Iconos.pmAtacada().scaledToWidth(24), Iconos.pmPuntoNegro())
                colPos += 1
                ly.controlc(isat, row, colPos)
                unBloque.append(isat)

            if self.esatacante:
                at = QTVarios.TwoImages(Iconos.pmAtacante().scaledToWidth(24), Iconos.pmPuntoNegro())
                colPos += 1
                ly.controlc(at, row, colPos)
                unBloque.append(at)

        ly1 = Colocacion.H().otro(ly).relleno()
        ly2 = Colocacion.V().otro(ly1).relleno()
        self.gbSolucion = Controles.GB(self, "", ly2)

        f = Controles.TipoLetra("", 11, 80, False, False, False, None)

        bt = Controles.PB(self, _("Close"), self.terminar, plano=False).ponIcono(Iconos.MainMenu()).ponFuente(f)
        self.btBoard = (
            Controles.PB(self, _("Go to board"), self.activaBoard, plano=False).ponIcono(Iconos.Board()).ponFuente(f)
        )
        self.btComprueba = (
            Controles.PB(self, _("Test the solution"), self.compruebaSolucion, plano=False)
            .ponIcono(Iconos.Check())
            .ponFuente(f)
        )
        self.btGotoNextLevel = (
            Controles.PB(self, _("Go to next level"), self.gotoNextLevel, plano=False)
            .ponIcono(Iconos.GoToNext())
            .ponFuente(f)
        )
        ly0 = (
            Colocacion.H()
            .control(bt)
            .relleno()
            .control(self.btBoard)
            .control(self.btComprueba)
            .control(self.btGotoNextLevel)
        )

        lyBase = Colocacion.H().control(self.gbBoard).control(self.gbSolucion)

        layout = Colocacion.V().otro(ly0).otro(lyBase)

        self.setLayout(layout)

        self.restore_video()

        self.gotoNextLevel()

    def miraTiempo(self):
        if self.iniTime:
            t = int(time.time() - self.iniTime)
            self.iniTime = None
            self.dicdatos["TIME"] += t

    def terminar(self):
        self.miraTiempo()
        self.accept()

    def closeEvent(self, event):
        self.miraTiempo()

    def gotoNextLevel(self):
        label = _("Level %d") % self.level
        self.gbSolucion.setTitle(label)

        fen = self.liFENs[self.level - 1]

        cp = Position.Position()
        cp.read_fen(fen)
        cp.legal()
        self.board.set_side_bottom(cp.is_white)
        self.board.set_position(cp)

        mens = ""
        if cp.castles:
            if ("K" if cp.is_white else "k") in cp.castles:
                mens = "O-O"
            if ("Q" if cp.is_white else "q") in cp.castles:
                if mens:
                    mens += " + "
                mens += "O-O-O"
            if mens:
                mens = _("Castling moves possible") + ": " + mens
        if cp.en_passant != "-":
            mens += " " + _("En passant") + ": " + cp.en_passant
        self.rotuloBoard = _("White") if cp.is_white else _("Black")
        if mens:
            self.rotuloBoard += " " + mens

        self.cp = cp

        self.intervaloMax = self.intervalo
        if self.intervaloPorPieza:
            self.intervaloMax *= self.level + 2
        self.ponTiempo(self.intervaloMax)

        for x in range(32):
            bloque = self.liBloques[x]
            siVisible = x < self.level + 2
            for elem in bloque:
                elem.setVisible(siVisible)
            if siVisible:
                bloque[0].ponImagen(self.pmNada)
                pz = "K" if x == 0 else ("k" if x == 1 else "P")
                bloque[1].set_value(pz)
                pos = 1
                if self.position:
                    pos += 1
                    bloque[pos].set_text("")
                if self.color:
                    pos += 1
                    bloque[pos].valor(True)
                if self.esatacada:
                    pos += 1
                    bloque[pos].valor(False)
                if self.esatacante:
                    pos += 1
                    bloque[pos].valor(False)

        for lb in self.liLB2:
            lb.setVisible(self.level >= 16)

        self.activaBoard()
        QtCore.QTimer.singleShot(1000, self.compruebaTiempo)
        self.iniTime = time.time()

    def compruebaTiempo(self):
        t = round(time.time() - self.iniTimeBoard, 0)
        r = self.intervaloMax - int(t)

        if r <= 0:
            self.activaSolucion()
        else:
            self.ponTiempo(r)
            QtCore.QTimer.singleShot(1000, self.compruebaTiempo)

    def activaBoard(self):
        self.iniTimeBoard = time.time()
        self.gbSolucion.hide()
        self.btBoard.hide()
        self.btComprueba.hide()
        self.btGotoNextLevel.hide()
        self.compruebaTiempo()
        self.gbBoard.show()
        self.gbBoard.adjustSize()
        self.adjustSize()

    def activaSolucion(self):
        self.gbBoard.hide()
        self.btBoard.show()
        self.btComprueba.show()
        self.btGotoNextLevel.hide()
        self.gbSolucion.show()
        self.adjustSize()

    def compruebaSolucion(self):
        liSolucion = self.calculaSolucion()
        nErrores = 0
        for x in range(self.level + 2):
            bloque = self.liBloques[x]

            pieza = bloque[1].valor()
            pos = 1
            if self.position:
                pos += 1
                position = bloque[pos].texto()
            if self.color:
                pos += 1
                color = bloque[pos].valor()
            if self.esatacada:
                pos += 1
                atacada = bloque[pos].valor()
            if self.esatacante:
                pos += 1
                atacante = bloque[pos].valor()

            correcta = False
            for rsol in liSolucion:
                if rsol.comprobada:
                    continue
                if rsol.pieza != pieza:
                    continue
                if self.position:
                    if rsol.position != position:
                        continue
                if self.color:
                    if rsol.color != color:
                        continue
                if self.esatacada:
                    if rsol.atacada != atacada:
                        continue
                if self.esatacante:
                    if rsol.atacante != atacante:
                        continue
                correcta = True
                rsol.comprobada = True
                break

            bloque[0].ponImagen(self.pmBien if correcta else self.pmMal)
            if not correcta:
                nErrores += 1
        if nErrores == 0:
            self.miraTiempo()
            self.gbSolucion.show()
            self.ponTiempo(0)
            self.gbBoard.show()
            self.btComprueba.hide()
            self.btBoard.hide()
            self.level += 1
            if self.level > 32:
                self.level = 0
            else:
                self.btGotoNextLevel.show()
            self.dicdatos["LEVEL"] = self.level
        else:
            self.dicdatos["ERRORS"] += nErrores

    def ponTiempo(self, num):
        titulo = self.rotuloBoard
        if num:
            titulo += "[ %s ]" % num
        self.gbBoard.setTitle(titulo)

    def calculaSolucion(self):
        fenMB = self.cp.fen()
        fenOB = fenMB.replace(" w ", " b ") if "w" in fenMB else fenMB.replace(" b ", " w ")
        stAttacKing = set()
        stAttacKed = set()
        for fen in (fenMB, fenOB):
            FasterCode.set_fen(fen)
            liMV = FasterCode.get_exmoves()
            for mv in liMV:
                if mv.capture():
                    stAttacKing.add(mv.xfrom())
                    stAttacKed.add(mv.xto())

        liSolucion = []
        for position, pieza in self.cp.squares.items():
            if pieza:
                reg = Util.Record()
                reg.pieza = pieza
                reg.position = position

                lt = position[0]
                nm = int(position[1])
                iswhite = nm % 2 == 0
                if lt in "bdfh":
                    iswhite = not iswhite
                reg.color = iswhite

                reg.atacante = position in stAttacKing
                reg.atacada = position in stAttacKed
                reg.comprobada = False
                liSolucion.append(reg)
        return liSolucion


def windowVisualiza(procesador):
    w = WControl(procesador, Code.path_resource("IntFiles", "Visual/R50-01.vis"))
    w.exec_()
