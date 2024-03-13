import os
import shutil
import time

import Code
from Code import Util
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Swiss import WSwiss
from Code.Swiss import WSwissConfig, Swiss


class WSwisses(LCDialog.LCDialog):
    def __init__(self, w_parent):

        titulo = _("Swiss Tournaments")
        icono = Iconos.Swiss()
        extparam = "swisses"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        # Datos
        self.list_swisses = self.read()
        self.run_swiss = None

        # Toolbar
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Run"), Iconos.Play(), self.play),
            None,
            (_("Create"), Iconos.Nuevo(), self.crear),
            None,
            (_("Edit"), Iconos.Modificar(), self.modify),
            None,
            (_("Rename"), Iconos.Rename(), self.rename),
            None,
            (_("Copy"), Iconos.Copiar(), self.copiar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        # grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NAME", _("Name"), 300)
        o_columns.nueva("DATE", _("Date"), 180, align_center=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.register_grid(self.grid)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(8)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=500, altoDefecto=500)

        self.grid.gotop()

    def play(self):
        row = self.grid.recno()
        if row >= 0:
            swiss = self.get_swiss(row)
            if swiss.enough_opponents():
                self.run_swiss = swiss
                self.accept()
            else:
                QTUtil2.message_error(self, _("The opponents need to be configured correctly."))
                self.edit(swiss)

    @staticmethod
    def read():
        li = []
        carpeta = Code.configuration.folder_swisses()
        for entry in Util.listdir(carpeta):
            filename = entry.name
            if filename.lower().endswith(".swiss"):
                st = entry.stat()
                li.append((filename, st.st_ctime, st.st_mtime))

        li = sorted(li, key=lambda x: x[2], reverse=True)  # por ultima modificación y al reves

        st = set(x[0] for x in li)
        for entry in Util.listdir(carpeta):
            if entry.name.endswith(".work"):
                if entry.name[:-5] not in st:
                    Util.remove_file(entry.path)

        return li

    def refresh_lista(self):
        self.list_swisses = self.read()
        self.grid.refresh()

    def nom_swiss_pos(self, row):
        return self.list_swisses[row][0][:-6]

    def grid_num_datos(self, grid):
        return len(self.list_swisses)

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        name, fcreacion, fmanten = self.list_swisses[row]
        if column == "NAME":
            return name[:-6]
        elif column == "DATE":
            tm = time.localtime(fmanten)
            return "%d-%02d-%d, %2d:%02d" % (tm.tm_mday, tm.tm_mon, tm.tm_year, tm.tm_hour, tm.tm_min)

    def grid_doble_click(self, grid, row, column):
        self.play()

    def terminar(self):
        self.save_video()
        self.accept()

    def get_swiss(self, row):
        filename, tmc, tmm = self.list_swisses[row]
        return Swiss.Swiss(filename[:-6])

    def edit_name(self, previo):
        nom_swiss = QTUtil2.read_simple(self, _("Swiss Tournaments"), _("Name"), previo)
        if nom_swiss:
            path = Util.opj(Code.configuration.folder_swisses(), nom_swiss + ".swiss")
            if os.path.isfile(path):
                QTUtil2.message_error(self, _("The file %s already exist") % nom_swiss)
                return self.edit_name(nom_swiss)
        return nom_swiss

    def crear(self):
        nom_swiss = self.edit_name("")
        if nom_swiss:
            nom_swiss = Util.valid_filename(nom_swiss)
            swiss = Swiss.Swiss(nom_swiss)
            self.edit(swiss)
            self.refresh_lista()

    def edit(self, swiss):
        w = WSwissConfig.WSwissConfig(self, swiss)
        w.exec_()

    def modify(self):
        row = self.grid.recno()
        if row >= 0:
            swiss = self.get_swiss(row)
            self.edit(swiss)

    def rename(self):
        row = self.grid.recno()
        if row >= 0:
            nom_origen = self.nom_swiss_pos(row)
            nom_destino = self.edit_name(nom_origen)
            if nom_destino and nom_origen != nom_destino:
                path_origen = Util.opj(Code.configuration.folder_swisses(), "%s.swiss" % nom_origen)
                path_destino = Util.opj(Code.configuration.folder_swisses(), "%s.swiss" % nom_destino)
                shutil.move(path_origen, path_destino)
                self.refresh_lista()

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            name = self.nom_swiss_pos(row)
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), name)):
                path = Util.opj(Code.configuration.folder_swisses(), "%s.swiss" % name)
                os.remove(path)
                self.refresh_lista()

    def copiar(self):
        row = self.grid.recno()
        if row >= 0:
            nom_origen = self.nom_swiss_pos(row)
            nom_destino = self.edit_name(nom_origen)
            if nom_destino and nom_origen != nom_destino:
                path_origen = Util.opj(Code.configuration.folder_swisses(), "%s.swiss" % nom_origen)
                path_destino = Util.opj(Code.configuration.folder_swisses(), "%s.swiss" % nom_destino)
                shutil.copy(path_origen, path_destino)
                self.refresh_lista()


def play_swiss(parent, swiss):
    play_human = WSwiss.play_swiss(parent, swiss)
    if play_human:
        swiss, xmatch = play_human
        Code.procesador.play_swiss_human(swiss, xmatch)
        return True
    return False


def swisses(parent):
    while True:
        w = WSwisses(parent)
        if w.exec_():
            if w.run_swiss:
                if play_swiss(parent, w.run_swiss):
                    return
                continue
        return
