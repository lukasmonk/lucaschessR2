import gettext
_ = gettext.gettext
import atexit
from PySide2 import QtCore

from Code import Util
from Code.Analysis import Analysis
from Code.Base import Game
from Code.Board import Board
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WJuicio(LCDialog.LCDialog):
    def __init__(self, manager, xengine, nombreOP, position, mrm, rmObj, rmUsu, analysis, is_competitive=None):
        self.is_competitive = manager.is_competitive if is_competitive is None else is_competitive
        self.nombreOP = nombreOP
        self.position = position
        self.rmObj = rmObj
        self.rmUsu = rmUsu
        self.mrm = mrm
        self.analysis = analysis
        self.siAnalisisCambiado = False
        self.xengine = xengine
        self.manager = manager

        self.list_rm, self.posOP = self.do_lirm()

        titulo = _("Analysis")
        icono = Iconos.Analizar()
        extparam = "jzgm"
        LCDialog.LCDialog.__init__(self, manager.main_window, titulo, icono, extparam)

        self.colorNegativo = QTUtil.qtColorRGB(255, 0, 0)
        self.colorImpares = QTUtil.qtColorRGB(231, 244, 254)

        self.lbComentario = Controles.LB(self, "").ponTipoLetra(puntos=10).align_center()

        config_board = manager.configuration.config_board("JUICIO", 32)
        self.board = Board.Board(self, config_board)
        self.board.crea()
        self.board.set_side_bottom(position.is_white)

        liMas = ((_("Close"), "close", Iconos.AceptarPeque()),)
        lyBM, tbBM = QTVarios.lyBotonesMovimiento(
            self, "", siLibre=False, icon_size=24, siMas=manager.continueTt, liMasAcciones=liMas
        )

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("POSREAL", "#", 40, align_center=True)
        o_columns.nueva("JUGADAS", "%d %s" % (len(self.list_rm), _("Moves")), 120, align_center=True)
        o_columns.nueva("PLAYER", _("Player"), 120)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)

        lyT = Colocacion.V().control(self.board).otro(lyBM).control(self.lbComentario)

        # Layout
        layout = Colocacion.H().otro(lyT).control(self.grid)

        self.setLayout(layout)

        self.grid.setFocus()

        self.grid.goto(self.posOP, 0)
        self.is_moving_time = False

        self.ponPuntos()

    def difPuntos(self):
        return self.rmUsu.puntosABS_5() - self.rmObj.puntosABS_5()

    def difPuntosMax(self):
        return self.mrm.mejorMov().puntosABS_5() - self.rmUsu.puntosABS_5()

    def ponPuntos(self):
        pts = self.difPuntos()
        if pts > 0:
            txt = _("Centipawns won %d") % pts
            color = "green"
        elif pts < 0:
            txt = _("Lost centipawns %d") % (-pts,)
            color = "red"
        else:
            txt = ""
            color = "black"
        self.lbComentario.set_text(txt)
        self.lbComentario.set_foreground(color)

    def process_toolbar(self):
        accion = self.sender().key
        if accion == "close":
            self.siMueveTiempo = False
            self.accept()
        elif accion == "MoverAdelante":
            self.mueve(n_saltar=1)
        elif accion == "MoverAtras":
            self.mueve(n_saltar=-1)
        elif accion == "MoverInicio":
            self.mueve(is_base=True)
        elif accion == "MoverFinal":
            self.mueve(siFinal=True)
        elif accion == "MoverTiempo":
            self.move_timed()
        elif accion == "MoverMas":
            self.mueveMas()
        elif accion == "MoverLibre":
            self.mueveLibre()

    def grid_num_datos(self, grid):
        return len(self.list_rm)

    def do_lirm(self):
        li = []
        posOP = 0
        nombrePlayer = _("You")
        posReal = 0
        ultPts = -99999999
        for pos, rm in enumerate(self.mrm.li_rm):
            pv1 = rm.pv.split(" ")[0]
            from_sq = pv1[:2]
            to_sq = pv1[2:4]
            promotion = pv1[4] if len(pv1) == 5 else ""

            pgn = self.position.pgn_translated(from_sq, to_sq, promotion)
            if pgn is None:
                continue
            a = Util.Record()
            a.rm = rm
            a.texto = "%s (%s)" % (pgn, rm.abrTextoBase())
            p = a.centipawns_abs = rm.centipawns_abs()
            if p != ultPts:
                ultPts = p
                posReal += 1

            siOP = rm.pv == self.rmObj.pv
            siUsu = rm.pv == self.rmUsu.pv
            if siOP and siUsu:
                txt = _("Both")
                posOP = pos
            elif siOP:
                txt = self.nombreOP
                posOP = pos
            elif siUsu:
                txt = nombrePlayer
            else:
                txt = ""
            a.player = txt

            a.is_selected = siOP or siUsu
            if a.is_selected or not self.is_competitive:
                if siOP:
                    posOP = len(li)
                a.posReal = posReal
                li.append(a)

        return li, posOP

    def grid_bold(self, grid, row, column):
        return self.list_rm[row].is_selected

    def grid_dato(self, grid, row, o_column):
        if o_column.key == "PLAYER":
            return self.list_rm[row].player
        elif o_column.key == "POSREAL":
            return self.list_rm[row].posReal
        else:
            return self.list_rm[row].texto

    def grid_color_texto(self, grid, row, o_column):
        return None if self.list_rm[row].centipawns_abs >= 0 else self.colorNegativo

    def grid_color_fondo(self, grid, row, o_column):
        if row % 2 == 1:
            return self.colorImpares
        else:
            return None

    def grid_cambiado_registro(self, grid, row, column):
        self.game = Game.Game(self.position)
        self.game.read_pv(self.list_rm[row].rm.pv)
        self.maxMoves = len(self.game)
        self.mueve(si_inicio=True)

        self.grid.setFocus()

    def mueve(self, si_inicio=False, n_saltar=0, siFinal=False, is_base=False):
        if n_saltar:
            pos = self.posMueve + n_saltar
            if 0 <= pos < self.maxMoves:
                self.posMueve = pos
            else:
                return False
        elif si_inicio:
            self.posMueve = 0
        elif is_base:
            self.posMueve = -1
        elif siFinal:
            self.posMueve = self.maxMoves - 1
        if len(self.game):
            move = self.game.move(self.posMueve if self.posMueve > -1 else 0)
            if is_base:
                self.board.set_position(move.position_before)
            else:
                self.board.set_position(move.position)
                self.board.put_arrow_sc(move.from_sq, move.to_sq)
        return True

    def move_timed(self):
        if self.is_moving_time:
            self.is_moving_time = False
            return
        self.is_moving_time = True
        self.mueve(is_base=True)
        self.mueveTiempoWork()

    def mueveTiempoWork(self):
        if self.is_moving_time:
            if not self.mueve(n_saltar=1):
                self.is_moving_time = False
                return
            QtCore.QTimer.singleShot(1000, self.mueveTiempoWork)

    def mueveMas(self):
        mrm = self.manager.analyze_state()

        rmUsuN, pos = mrm.buscaRM(self.rmUsu.movimiento())
        if rmUsuN is None:
            um = QTUtil2.analizando(self)
            self.manager.analyze_end()
            rmUsuN = self.xengine.valora(self.position, self.rmUsu.from_sq, self.rmUsu.to_sq, self.rmUsu.promotion)
            mrm.agregaRM(rmUsuN)
            self.manager.analyze_begin()
            um.final()

        self.rmUsu = rmUsuN

        rmObjN, pos = mrm.buscaRM(self.rmObj.movimiento())
        if rmObjN is None:
            um = QTUtil2.analizando(self)
            self.manager.analyze_end()
            rmObjN = self.xengine.valora(self.position, self.rmObj.from_sq, self.rmObj.to_sq, self.rmObj.promotion)
            pos = mrm.agregaRM(rmObjN)
            self.manager.analyze_begin()
            um.final()

        self.rmObj = rmObjN
        self.analysis = self.mrm, pos
        self.siAnalisisCambiado = True

        self.mrm = mrm

        self.ponPuntos()
        self.list_rm, self.posOP = self.do_lirm()
        self.grid.refresh()

    def mueveLibre(self):
        move = self.game.move(self.posMueve)
        pts = self.list_rm[self.grid.recno()].rm.texto()
        Analysis.AnalisisVariations(self, self.xengine, move, self.position.is_white, pts)
