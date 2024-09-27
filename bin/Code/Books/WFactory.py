import datetime
import os
import os.path
import shutil

import Code
from Code import Util
from Code.Books import DBPolyglot, WPolyglot
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WFactoryPolyglots(LCDialog.LCDialog):
    def __init__(self, procesador):
        self.procesador = procesador
        self.configuration = procesador.configuration
        self.resultado = None

        self.index_polyglots = DBPolyglot.IndexPolyglot()

        self.list_db = self.index_polyglots.list()

        LCDialog.LCDialog.__init__(
            self, procesador.main_window, _("Polyglot book factory"), Iconos.FactoryPolyglot(), "factorypolyglots"
        )

        o_columnas = Columnas.ListaColumnas()
        o_columnas.nueva("NAME", _("Name"), 200)
        o_columnas.nueva("MTIME", _("Last modification"), 160, align_center=True)
        o_columnas.nueva("SIZE", _("Moves"), 100, align_right=True)
        self.glista = Grid.Grid(self, o_columnas, siSelecFilas=True, siSeleccionMultiple=True)

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Edit"), Iconos.Modificar(), self.edit),
            None,
            (_("New"), Iconos.Nuevo(), self.new),
            None,
            (_("Copy"), Iconos.Copiar(), self.copy),
            None,
            (_("Rename"), Iconos.Modificar(), self.renombrar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Update"), Iconos.Reiniciar(), self.update),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        ly = Colocacion.V().control(tb).control(self.glista).margen(4)
        self.setLayout(ly)

        self.register_grid(self.glista)
        self.restore_video(anchoDefecto=self.glista.anchoColumnas() + 20, altoDefecto=324)

        self.glista.gotop()

    def edit(self):
        recno = self.glista.recno()
        if recno >= 0:
            self.run_edit(self.list_db[recno]["FILENAME"])

    def grid_doble_click(self, grid, row, o_columna):
        self.edit()

    def run_edit(self, filename):
        self.resultado = Util.opj(Code.configuration.folder_polyglots_factory(), filename)
        self.save_video()
        self.accept()

    def get_new_path(self, name):
        while True:
            name = QTUtil2.read_simple(self, _("New polyglot book"), _("Name"), name)
            if name:
                path = Util.opj(self.configuration.folder_polyglots_factory(), name + ".lcbin")
                if os.path.isfile(path):
                    QTUtil2.message_error(self, "%s\n%s" % (_("This file already exists"), path))
                else:
                    return os.path.realpath(path)
            else:
                return None

    def new(self):
        path = self.get_new_path("")
        if path:
            with DBPolyglot.DBPolyglot(path):  # To create the file
                pass
            self.update(soft=True)
            self.run_edit(path)

    def path_db(self, filename):
        return Util.opj(Code.configuration.folder_polyglots_factory(), filename)

    def copy(self):
        recno = self.glista.recno()
        if recno >= 0:
            path = self.get_new_path(self.list_db[recno]["FILENAME"][:-6])
            if path:
                folder = Code.configuration.folder_polyglots_factory()
                shutil.copy(self.path_db(self.list_db[recno]["FILENAME"]), Util.opj(folder, path))
                self.update()
                self.glista.refresh()

    def renombrar(self):
        recno = self.glista.recno()
        if recno >= 0:
            reg = self.list_db[recno]
            path = self.get_new_path(reg["FILENAME"][:-6])
            if path:
                os.rename(self.path_db(reg["FILENAME"]), path)
                self.update()
                self.glista.refresh()

    def borrar(self):
        li = self.glista.recnosSeleccionados()
        if len(li) > 0:
            mens = _("Do you want to delete all selected records?")
            mens += "\n"
            for num, row in enumerate(li, 1):
                mens += "\n%d. %s" % (num, self.list_db[row]["FILENAME"][:-6])
            if QTUtil2.pregunta(self, mens):
                li.sort(reverse=True)
                for row in li:
                    Util.remove_file(self.path_db(self.list_db[row]["FILENAME"]))
                self.update(soft=True)
                self.glista.refresh()

    def grid_num_datos(self, grid):
        return len(self.list_db)

    def grid_dato(self, grid, row, o_columna):
        col = o_columna.key

        reg = self.list_db[row]
        if col == "MTIME":
            return Util.localDateT(datetime.datetime.fromtimestamp(reg["MTIME"]))
        elif col == "NAME":
            return reg["FILENAME"][:-6]
        elif col == "SIZE":
            return "{:,}".format(reg["SIZE"]).replace(",", ".")

    def update(self, soft=False):
        if soft:
            self.list_db = self.index_polyglots.update_soft()
        else:
            self.list_db = self.index_polyglots.update_hard(self)
        self.glista.refresh()
        self.glista.gotop()

    def closeEvent(self, event):  # Cierre con X
        self.save_video()

    def terminar(self):
        self.save_video()
        self.accept()


def polyglots_factory(procesador):
    w = WFactoryPolyglots(procesador)
    return w.resultado if w.exec_() else None


def edit_polyglot(procesador, path_dbbin):
    w = WPolyglot.WPolyglot(procesador.main_window, procesador.configuration, path_dbbin)
    w.exec_()
