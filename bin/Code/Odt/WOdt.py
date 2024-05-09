import os

from PySide2 import QtCore

import Code
from Code.Board import Board2
from Code.Odt import Odt
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios
from Code.QT import LCDialog
from Code.QT import SelectFiles


def path_saveas_odt(owner, name):
    configuration = Code.configuration
    key_var = "ODT"
    dic = configuration.read_variables(key_var)
    folder = dic.get("FOLDER_SAVE", configuration.carpeta)
    carpeta = "%s/%s.odt" % (folder, name)

    path = SelectFiles.salvaFichero(owner, _("File to save"), carpeta, "odt", True)
    if path:
        dic["FOLDER_SAVE"] = os.path.dirname(path)
        configuration.write_variables(key_var, dic)
    return path


class WOdt(LCDialog.LCDialog):
    def __init__(self, owner, path_odt):
        title = "%s: %s" % (_("Export to"), path_odt)
        LCDialog.LCDialog.__init__(self, owner, title, Iconos.ODT(), "ODT")

        self.configuration = Code.configuration
        self.path_odt = path_odt
        self.odt_doc = None

        self.owner = owner
        self.routine = None

        self.canceled = False

        conf_board = self.configuration.config_board("ODT", 64)

        self.board = Board2.BoardEstatico(self, conf_board)
        self.board.crea()

        li_acciones = ((_("Export"), Iconos.ODT(), self.begin), (_("Cancel"), Iconos.Cancelar(), self.cancel))
        self.tb = QTVarios.LCTB(self, li_acciones, style=QtCore.Qt.ToolButtonTextBesideIcon, icon_size=32)
        self.show_tb(self.begin, self.cancel)

        self.lb_pos = Controles.LB("").set_font_type(puntos=32).anchoFijo(240).align_right()
        self.lb_pos.hide()

        ly_arr = Colocacion.H().control(self.tb).control(self.lb_pos).margen(0)

        ly = Colocacion.V().otro(ly_arr).control(self.board).margen(3)
        self.setLayout(ly)

        self.restore_video()
        self.adjustSize()

    def cancel(self):
        self.canceled = True
        self.reject()

    def set_cpos(self, txt):
        self.lb_pos.set_text(txt)

    def begin(self):
        self.show_tb(self.cancel)
        self.lb_pos.show()

        while self.routine(self):
            QTUtil.refresh_gui()
            if self.canceled:
                self.reject()
                return

        self.accept()

    def create_document(self, title, landscape, margins=None):
        self.odt_doc = Odt.ODT()
        if landscape:
            self.odt_doc.landscape()
        self.odt_doc.set_header(title)
        if margins:
            top, bottom, left, right = margins
            self.odt_doc.margins(top, bottom, left, right)
        return self.odt_doc

    def show_tb(self, *lista):
        for opc in self.tb.dic_toolbar:
            self.tb.set_action_visible(opc, opc in lista)
        QTUtil.refresh_gui()

    def set_routine(self, routine):
        self.routine = routine

    def pulsada_celda(self, x):  # Compatibility
        pass
