import collections
import os
import shutil

from PySide2 import QtCore, QtGui, QtSvg

import Code
from Code import Util
from Code.Base.Constantes import BLINDFOLD_CONFIG, BLINDFOLD_WHITE, BLINDFOLD_BLACK
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTVarios
from Code.Translations import TrListas


DEFAULT_PIECES = "Cburnett"


def is_only_board(name) -> bool:
    fich = Code.path_resource("Pieces", name, "only_board")
    return os.path.isfile(fich)


class ConjuntoPiezas:
    def __init__(self, name):
        self.name = name
        self.dicPiezas = self.leePiezas(name)

    def is_only_board(self):
        return is_only_board(self.name)

    @staticmethod
    def get_default():
        return ConjuntoPiezas(DEFAULT_PIECES)

    def leePiezas(self, name):
        try:
            dic = {}
            for pieza in "rnbqkpRNBQKP":
                fich = Code.path_resource("Pieces", name, "%s%s.svg" % ("w" if pieza.isupper() else "b", pieza.lower()))
                with open(fich, "rb") as f:
                    qb = QtCore.QByteArray(f.read())
                dic[pieza] = qb
            return dic
        except:
            return self.leePiezas(DEFAULT_PIECES)

    def render(self, pieza):
        return QtSvg.QSvgRenderer(self.dicPiezas[pieza])

    def widget(self, pieza):
        w = QtSvg.QSvgWidget()
        w.load(self.dicPiezas[pieza])
        return w

    def pixmap(self, pieza, tam=24):
        pm = QtGui.QPixmap(tam, tam)
        pm.fill(QtCore.Qt.transparent)
        render = self.render(pieza)
        painter = QtGui.QPainter()
        painter.begin(pm)
        render.render(painter)
        painter.end()
        return pm

    def label(self, owner, pieza, tam):
        pm = self.pixmap(pieza, tam)
        lb = Controles.LB(owner)
        lb.put_image(pm)
        lb.pieza = pieza
        lb.tam_pieza = tam
        return lb

    def change_label(self, lb, tam):
        if lb.tam_pieza != tam:
            pm = self.pixmap(lb.pieza, tam)
            lb.put_image(pm)

    def icono(self, pieza):
        icon = QtGui.QIcon(self.pixmap(pieza, 32))
        return icon

    def cursor(self, pieza):
        return QtGui.QCursor(self.pixmap(pieza))


class AllPieces:
    def __init__(self):
        self.dicConjuntos = {}

    def selecciona(self, name):
        if name in self.dicConjuntos:
            return self.dicConjuntos[name]
        else:
            return self.nuevo(name)

    def nuevo(self, name):
        self.dicConjuntos[name] = ConjuntoPiezas(name)
        return self.dicConjuntos[name]

    def icono(self, pieza, name, width=32):
        pm = self.pixmap(pieza, name, width)
        return QtGui.QIcon(pm)

    def pixmap(self, pieza, name, width):
        fich = Code.path_resource("Pieces", name, "%s%s.svg" % ("w" if pieza.isupper() else "b", pieza.lower()))
        try:
            with open(fich, "rb") as f:
                qb = QtCore.QByteArray(f.read())
        except FileNotFoundError:
            return self.icono(pieza, DEFAULT_PIECES)
        pm = QtGui.QPixmap(width, width)
        pm.fill(QtCore.Qt.transparent)
        render = QtSvg.QSvgRenderer(qb)
        painter = QtGui.QPainter()
        painter.begin(pm)
        render.render(painter)
        painter.end()
        return pm

    def default_icon(self, pieza, width=32):
        return self.icono(pieza, DEFAULT_PIECES, width)

    def default_pixmap(self, pieza, width):
        return self.pixmap(pieza, DEFAULT_PIECES, width)

    @staticmethod
    def save_all_png(name, px):
        if is_only_board(name):
            name = DEFAULT_PIECES
        folder_to_save = Code.configuration.folder_pieces_png()
        for pieza in "pnbrqk":
            for color in "wb":
                fich = Code.path_resource("Pieces", name, "%s%s.svg" % (color, pieza))
                with open(fich, "rb") as f:
                    qb = QtCore.QByteArray(f.read())
                pm = QtGui.QPixmap(px, px)
                pm.fill(QtCore.Qt.transparent)
                render = QtSvg.QSvgRenderer(qb)
                painter = QtGui.QPainter()
                painter.begin(pm)
                render.render(painter)
                painter.end()
                path = Util.opj(folder_to_save, f"{color}{pieza}.png")
                pm.save(path, "PNG")


HIDE, GREY, CHECKER, SHOW = range(4)


class BlindfoldConfig:
    def __init__(self, nom_pieces_ori, dicPiezas=None):
        self.nom_pieces_ori = nom_pieces_ori
        if dicPiezas is None:
            self.restore()
        else:
            self.dicPiezas = dicPiezas

    def ficheroBase(self, pz, siWhite):
        pz = pz.lower()
        if siWhite:
            pz_t = pz.upper()
        else:
            pz_t = pz
        tipo = self.dicPiezas[pz_t]
        if tipo == SHOW:
            pz = ("w" if siWhite else "b") + pz
            return Code.path_resource("Pieces", self.nom_pieces_ori, pz + ".svg")
        if tipo == HIDE:
            fich = "h"
        elif tipo == GREY:
            fich = "g"
        elif tipo == CHECKER:
            fich = "w" if siWhite else "b"
        return Code.path_resource("IntFiles/Svg", "blind_%s.svg" % fich)

    def restore(self):
        self.dicPiezas = Code.configuration.read_variables("BLINDFOLD")
        if not self.dicPiezas:
            for pieza in "rnbqkpRNBQKP":
                self.dicPiezas[pieza] = HIDE

    def save(self):
        dic: dict = Code.configuration.read_variables("BLINDFOLD")
        dic.update(self.dicPiezas)
        Code.configuration.write_variables("BLINDFOLD", dic)

    def list_saved(self):
        return [k[1:] for k in self.dicPiezas if k.startswith("_")]

    def remove(self, name):
        del self.dicPiezas["_" + name]
        Code.configuration.write_variables("BLINDFOLD", self.dicPiezas)

    def add_current(self, name):
        kdic = {k: v for k, v in self.dicPiezas.items() if not k.startswith("_")}
        self.dicPiezas["_" + name] = kdic
        Code.configuration.write_variables("BLINDFOLD", self.dicPiezas)

    def saved(self, name):
        return self.dicPiezas["_" + name]


class Blindfold(ConjuntoPiezas):
    def __init__(self, nom_pieces_ori, tipo=BLINDFOLD_CONFIG):
        self.name = "BlindFold"
        self.carpetaBF = Util.opj(Code.configuration.carpeta, "BlindFoldPieces")
        self.carpetaPZ = Code.path_resource("IntFiles")
        self.tipo = tipo
        self.reset(nom_pieces_ori)

    def leePiezas(self, name=None):  # name usado por compatibilidad
        dic = {}
        for pieza in "rnbqkpRNBQKP":
            fich = Util.opj(self.carpetaBF, "%s%s.svg" % ("w" if pieza.isupper() else "b", pieza.lower()))
            with open(fich, "rb") as f:
                qb = QtCore.QByteArray(f.read())
            dic[pieza] = qb
        return dic

    def reset(self, nom_pieces_ori):
        if self.tipo == BLINDFOLD_CONFIG:
            dicTPiezas = None
        else:
            w = b = HIDE
            if self.tipo == BLINDFOLD_WHITE:
                b = SHOW
            elif self.tipo == BLINDFOLD_BLACK:
                w = SHOW
            dicTPiezas = {}
            for pieza in "rnbqkp":
                dicTPiezas[pieza] = b
                dicTPiezas[pieza.upper()] = w
        self.configBF = BlindfoldConfig(nom_pieces_ori, dicPiezas=dicTPiezas)
        if not os.path.isdir(self.carpetaBF):
            Util.create_folder(self.carpetaBF)

        for siWhite in (True, False):
            for pieza in "rnbqkp":
                ori = self.configBF.ficheroBase(pieza, siWhite)
                bs = "w" if siWhite else "b"
                dest = Util.opj(self.carpetaBF, "%s%s.svg" % (bs, pieza))
                shutil.copy(ori, dest)

        self.dicPiezas = self.leePiezas()


class WBlindfold(LCDialog.LCDialog):
    def __init__(self, owner, nom_pieces_ori):

        titulo = _("Blindfold chess") + " - " + _("Configuration")
        icono = Iconos.Ojo()
        extparam = "wblindfold"
        LCDialog.LCDialog.__init__(self, owner, titulo, icono, extparam)

        self.config = BlindfoldConfig(nom_pieces_ori)
        self.nom_pieces_ori = nom_pieces_ori

        lbWhite = Controles.LB(self, _("White")).set_font_type(peso=75, puntos=10)
        lbBlack = Controles.LB(self, _("Black")).set_font_type(peso=75, puntos=10)

        self.dicWidgets = collections.OrderedDict()
        self.dicImgs = {}

        li_options = ((_("Hide"), HIDE), (_("Green"), GREY), (_("Checker"), CHECKER), (_("Show"), SHOW))
        dicNomPiezas = TrListas.dic_nom_pieces()

        def haz(pz):
            tpW = self.config.dicPiezas[pz.upper()]
            tpB = self.config.dicPiezas[pz]
            lbPZw = Controles.LB(self)
            cbPZw = Controles.CB(self, li_options, tpW).capture_changes(self.reset)
            lbPZ = Controles.LB(self, dicNomPiezas[pz.upper()]).set_font_type(peso=75, puntos=10)
            lbPZb = Controles.LB(self)
            cbPZb = Controles.CB(self, li_options, tpB).capture_changes(self.reset)
            self.dicWidgets[pz] = [lbPZw, cbPZw, lbPZ, lbPZb, cbPZb, None, None]

        for pz in "kqrbnp":
            haz(pz)

        btAllW = Controles.PB(self, _("All White"), self.allWhite, plano=False)
        self.cbAll = Controles.CB(self, li_options, HIDE)
        btAllB = Controles.PB(self, _("All Black"), self.allBlack, plano=False)

        btSwap = Controles.PB(self, _("Swap"), self.swap, plano=False)

        li_acciones = (
            (_("Save"), Iconos.Grabar(), "grabar"),
            None,
            (_("Cancel"), Iconos.Cancelar(), "cancelar"),
            None,
            (_("Configurations"), Iconos.Opciones(), "configurations"),
            None,
        )
        tb = Controles.TB(self, li_acciones)

        ly = Colocacion.G()
        ly.controlc(lbWhite, 0, 1).controlc(lbBlack, 0, 3)
        row = 1
        for pz in "kqrbnp":
            lbPZw, cbPZw, lbPZ, lbPZb, cbPZb, tipoW, tipoB = self.dicWidgets[pz]
            ly.control(cbPZw, row, 0)
            ly.controlc(lbPZw, row, 1)
            ly.controlc(lbPZ, row, 2)
            ly.controlc(lbPZb, row, 3)
            ly.control(cbPZb, row, 4)
            row += 1

        ly.filaVacia(row, 20)
        row += 1

        ly.controld(btAllW, row, 0, 1, 2)
        ly.control(self.cbAll, row, 2)
        ly.control(btAllB, row, 3, 1, 2)
        ly.controlc(btSwap, row + 1, 0, 1, 5)
        ly.margen(20)

        layout = Colocacion.V().control(tb).otro(ly)

        self.setLayout(layout)

        self.reset()

    def process_toolbar(self):
        getattr(self, self.sender().key)()

    def closeEvent(self):
        self.save_video()

    def grabar(self):
        self.save_video()
        self.config.save()
        self.accept()

    def cancelar(self):
        self.save_video()
        self.reject()

    def configurations(self):
        menu = QTVarios.LCMenu(self)
        li_saved = self.config.list_saved()
        for name in li_saved:
            menu.opcion((True, name), name, Iconos.PuntoAzul())
        menu.separador()
        menu.opcion((True, None), _("Save current configuration"), Iconos.PuntoVerde())
        if li_saved:
            menu.separador()
            menudel = menu.submenu(_("Remove"), Iconos.Delete())
            for name in li_saved:
                menudel.opcion((False, name), name, Iconos.PuntoNegro())

        resp = menu.lanza()
        if resp is None:
            return

        si, cual = resp

        if si:
            if cual:
                dpz = self.config.saved(cual)
                for pz in "kqrbnp":
                    lbPZw, cbPZw, lbPZ, lbPZb, cbPZb, tipoW, tipoB = self.dicWidgets[pz]
                    cbPZw.set_value(dpz[pz.upper()])
                    cbPZb.set_value(dpz[pz])
                self.reset()
            else:
                li_gen = [(None, None)]
                li_gen.append((_("Name") + ":", ""))

                resultado = FormLayout.fedit(
                    li_gen,
                    title=_("Save current configuration"),
                    parent=self,
                    anchoMinimo=460,
                    icon=Iconos.TutorialesCrear(),
                )
                if resultado is None:
                    return None

                accion, li_resp = resultado
                name = li_resp[0].strip()
                if not name:
                    return None
                self.config.add_current(name)
        else:
            self.config.remove(cual)

    # def configurations1(self):
    #     dic = Code.configuration.read_variables("BLINDFOLD")
    #     dicConf = collections.OrderedDict()
    #     for k in dic:
    #         if k.startswith("_"):
    #             cl = k[1:]
    #             dicConf[cl] = dic[k]
    #
    #     menu = QTVarios.LCMenu(self)
    #     for k in dicConf:
    #         menu.opcion((True, k), k, Iconos.PuntoAzul())
    #     menu.separador()
    #     menu.opcion((True, None), _("Save current configuration"), Iconos.PuntoVerde())
    #     if dicConf:
    #         menu.separador()
    #         menudel = menu.submenu(_("Remove"), Iconos.Delete())
    #         for k in dicConf:
    #             menudel.opcion((False, k), k, Iconos.PuntoNegro())
    #
    #     resp = menu.lanza()
    #     if resp is None:
    #         return
    #
    #     si, cual = resp
    #
    #     if si:
    #         if cual:
    #             dpz = dic["_" + cual]
    #             for pz in "kqrbnp":
    #                 lbPZw, cbPZw, lbPZ, lbPZb, cbPZb, tipoW, tipoB = self.dicWidgets[pz]
    #                 cbPZw.set_value(dpz[pz.upper()])
    #                 cbPZb.set_value(dpz[pz])
    #             self.reset()
    #         else:
    #             li_gen = [(None, None)]
    #             li_gen.append((_("Name") + ":", ""))
    #
    #             resultado = FormLayout.fedit(
    #                 li_gen,
    #                 title=_("Save current configuration"),
    #                 parent=self,
    #                 anchoMinimo=460,
    #                 icon=Iconos.TutorialesCrear(),
    #             )
    #             if resultado is None:
    #                 return None
    #
    #             accion, li_resp = resultado
    #             name = li_resp[0].strip()
    #             if not name:
    #                 return None
    #             dic["_%s" % name] = self.config.dicPiezas
    #             Code.configuration.write_variables("BLINDFOLD", dic)
    #     else:
    #         del dic["_%s" % cual]
    #         Code.configuration.write_variables("BLINDFOLD", dic)

    def allWhite(self):
        tp = self.cbAll.valor()
        for pzB in "rnbqkp":
            lbPZw, cbPZw, lbPZ, lbPZb, cbPZb, tipoW, tipoB = self.dicWidgets[pzB]
            cbPZw.set_value(tp)
        self.reset()

    def allBlack(self):
        tp = self.cbAll.valor()
        for pzB in "rnbqkp":
            lbPZw, cbPZw, lbPZ, lbPZb, cbPZb, tipoW, tipoB = self.dicWidgets[pzB]
            cbPZb.set_value(tp)
        self.reset()

    def swap(self):
        for pzB in "rnbqkp":
            lbPZw, cbPZw, lbPZ, lbPZb, cbPZb, tipoW, tipoB = self.dicWidgets[pzB]
            tpB = cbPZb.valor()
            tpW = cbPZw.valor()
            cbPZb.set_value(tpW)
            cbPZw.set_value(tpB)
        self.reset()

    def reset(self):
        for pzB in "kqrbnp":
            lbPZw, cbPZw, lbPZ, lbPZb, cbPZb, tipoW, tipoB = self.dicWidgets[pzB]
            tipoNv = cbPZw.valor()
            if tipoW != tipoNv:
                pzW = pzB.upper()
                self.config.dicPiezas[pzW] = tipoNv
                self.dicWidgets[pzB][5] = tipoNv  # tiene que ser pzB que esta en misnusculas
                fich = self.config.ficheroBase(pzB, True)
                if fich in self.dicImgs:
                    pm = self.dicImgs[fich]
                else:
                    pm = QTVarios.fsvg2pm(fich, 32)
                    self.dicImgs[fich] = pm
                lbPZw.put_image(pm)
            tipoNv = cbPZb.valor()
            if tipoB != tipoNv:
                self.config.dicPiezas[pzB] = tipoNv
                self.dicWidgets[pzB][6] = tipoNv
                fich = self.config.ficheroBase(pzB, False)
                if fich in self.dicImgs:
                    pm = self.dicImgs[fich]
                else:
                    pm = QTVarios.fsvg2pm(fich, 32)
                    self.dicImgs[fich] = pm
                lbPZb.put_image(pm)
