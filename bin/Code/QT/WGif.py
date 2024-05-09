import os

from PIL import Image
from PySide2 import QtCore

import Code
from Code import Util
from Code.Board import Board2
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios, FormLayout
from Code.QT import LCDialog, QTUtil2


class WGif(LCDialog.LCDialog):
    def __init__(self, owner, game):
        self.title = _("Save as GIF file")
        LCDialog.LCDialog.__init__(self, owner, self.title, Iconos.GIF(), "GIF")

        self.configuration = Code.configuration
        self.game = game

        self.canceled = False

        conf_board = self.configuration.config_board("GIF", 64)

        self.board = Board2.BoardEstatico(self, conf_board)
        self.board.crea()

        li_acciones = ((_("Save"), Iconos.GIF(), self.begin), (_("Cancel"), Iconos.Cancelar(), self.cancel))
        self.tb = QTVarios.LCTB(self, li_acciones, style=QtCore.Qt.ToolButtonTextBesideIcon, icon_size=32)
        self.show_tb(self.begin, self.cancel)

        self.lb_pos = Controles.LB("").set_font_type(puntos=32).anchoFijo(240).align_right()

        ly_arr = Colocacion.H().control(self.tb).control(self.lb_pos).margen(0)

        ly = Colocacion.V().otro(ly_arr).control(self.board).margen(3)
        self.setLayout(ly)

        self.restore_video()
        self.adjustSize()

        self.board.set_position(self.game.first_position)

        self.lb_pos.set_text(f"0/{len(self.game)}")

        self.li_frames = []

    def cancel(self):
        self.canceled = True
        self.reject()

    def save_board(self):
        path_png = Code.configuration.ficheroTemporal("png")
        self.board.save_as_img(path_png)
        self.li_frames.append(Image.open(path_png))

    def begin(self):

        key = "GIF"
        dic_vars = Code.configuration.read_variables(key)

        form = FormLayout.FormLayout(self, self.title, Iconos.GIF(), anchoMinimo=640)

        form.separador()

        path = dic_vars.get("PATH", Util.opj(Code.configuration.carpeta, "Example.gif"))
        form.file(_("Save as"), "gif", True, path)
        form.separador()

        seconds = dic_vars.get("SECONDS", 1.0)
        form.float(_("Number of seconds between moves"), seconds)
        form.separador()

        loop = dic_vars.get("LOOP", True)
        form.checkbox(_("Infinite loop"), loop)
        form.separador()

        arrows = dic_vars.get("ARROWS", False)
        form.checkbox(_("Arrows"), arrows)
        form.separador()

        resp = form.run()
        if not resp:
            return
        accion, li_resp = resp
        path_gif, seconds, loop, arrows = li_resp

        if Util.exist_file(path_gif):
            yn = QTUtil2.question_withcancel(
                self,
                _X(_("The file %1 already exists, what do you want to do?"), os.path.basename(path_gif)),
                si=_("Overwrite"),
                no=_("Choose another"),
            )
            if yn is None:
                return
            if not yn:
                return self.begin()

        self.show_tb(self.cancel)

        self.save_board()
        for num, move in enumerate(self.game.li_moves, 1):
            self.lb_pos.set_text(f"{num}/{len(self.game)}")
            self.board.set_position(move.position)
            if arrows:
                self.board.put_arrow_sc(move.from_sq, move.to_sq)
            self.save_board()
            QTUtil.refresh_gui()
            if self.canceled:
                self.reject()
                return
        if self.canceled:
            return

        self.li_frames[0].save(path_gif, format='GIF', append_images=self.li_frames[1:], save_all=True,
                               duration=seconds * 1000, loop=0 if loop else 1)

        dic_vars["PATH"] = path_gif
        dic_vars["SECONDS"] = seconds
        dic_vars["LOOP"] = loop
        dic_vars["ARROWS"] = arrows

        Code.configuration.write_variables(key, dic_vars)

        self.accept()

        Code.startfile(path_gif)

    def show_tb(self, *lista):
        for opc in self.tb.dic_toolbar:
            self.tb.set_action_visible(opc, opc in lista)
        QTUtil.refresh_gui()

    def pulsada_celda(self, x):  # Compatibility
        pass
