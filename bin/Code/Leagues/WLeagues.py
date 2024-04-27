import os
import shutil
import time

import Code
from Code import Util
from Code.Leagues import WLeagueConfig, WLeague, Leagues
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios


class WLeagues(LCDialog.LCDialog):
    def __init__(self, w_parent):

        titulo = _("Chess leagues")
        icono = Iconos.League()
        extparam = "leagues"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        # Datos
        self.list_leagues = self.read()
        self.run_league = None

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
            league = self.get_league(row)
            if league.enough_opponents():
                self.run_league = league
                self.accept()
            else:
                QTUtil2.message_error(self, _("The opponents need to be configured correctly."))
                self.edit(league)

    @staticmethod
    def read():
        li = []
        carpeta = Code.configuration.folder_leagues()
        for entry in Util.listdir(carpeta):
            filename = entry.name
            if filename.lower().endswith(".league"):
                st = entry.stat()
                li.append((filename, st.st_ctime, st.st_mtime))

        li = sorted(li, key=lambda x: x[2], reverse=True)  # por ultima modificación y al reves
        return li

    def refresh_lista(self):
        self.list_leagues = self.read()
        self.grid.refresh()

    def nom_league_pos(self, row):
        return self.list_leagues[row][0][:-7]

    def grid_num_datos(self, grid):
        return len(self.list_leagues)

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        name, fcreacion, fmanten = self.list_leagues[row]
        if column == "NAME":
            return name[:-7]
        elif column == "DATE":
            tm = time.localtime(fmanten)
            return "%d-%02d-%d, %2d:%02d" % (tm.tm_mday, tm.tm_mon, tm.tm_year, tm.tm_hour, tm.tm_min)

    def grid_doble_click(self, grid, row, column):
        self.play()

    def terminar(self):
        self.save_video()
        self.accept()

    def get_league(self, row):
        filename, tmc, tmm = self.list_leagues[row]
        return Leagues.League(filename[:-7])

    def edit_name(self, previo):
        name = QTUtil2.read_simple(self, _("Chess leagues"), _("Name"), previo)
        if name:
            nom_league = Util.valid_filename(name.strip())
            if nom_league:
                path = Util.opj(Code.configuration.folder_leagues(), nom_league + ".league")
                if os.path.isfile(path):
                    QTUtil2.message_error(self, _("The file %s already exist") % nom_league)
                    return self.edit_name(nom_league)
            return nom_league

    def crear(self):
        nom_league = self.edit_name("")
        if nom_league:
            nom_league = Util.valid_filename(nom_league)
            league = Leagues.League(nom_league)
            self.edit(league)
            self.refresh_lista()

    def edit(self, league):
        w = WLeagueConfig.WLeagueConfig(self, league)
        w.exec_()

    def modify(self):
        row = self.grid.recno()
        if row >= 0:
            league = self.get_league(row)
            self.edit(league)

    def rename(self):
        row = self.grid.recno()
        if row >= 0:
            nom_origen = self.nom_league_pos(row)
            nom_destino = self.edit_name(nom_origen)
            if nom_destino and nom_origen != nom_destino:
                path_origen = Util.opj(Code.configuration.folder_leagues(), "%s.league" % nom_origen)
                path_destino = Util.opj(Code.configuration.folder_leagues(), "%s.league" % nom_destino)
                shutil.move(path_origen, path_destino)
                self.refresh_lista()

    def borrar(self):
        row = self.grid.recno()
        if row >= 0:
            name = self.nom_league_pos(row)
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), name)):
                path = Util.opj(Code.configuration.folder_leagues(), "%s.league" % name)
                os.remove(path)
                self.refresh_lista()

    def copiar(self):
        row = self.grid.recno()
        if row >= 0:
            nom_origen = self.nom_league_pos(row)
            nom_destino = self.edit_name(nom_origen)
            if nom_destino and nom_origen != nom_destino:
                path_origen = Util.opj(Code.configuration.folder_leagues(), f"{nom_origen}.league")
                path_destino = Util.opj(Code.configuration.folder_leagues(), f"{nom_destino}.league")
                shutil.copy(path_origen, path_destino)
                self.refresh_lista()


def play_league(parent, league):
    play_human = WLeague.play_league(parent, league)
    if play_human:
        league, xmatch, division = play_human
        Code.procesador.play_league_human(league, xmatch, division)
        return True
    return False


def leagues(parent):
    while True:
        w = WLeagues(parent)
        if w.exec_():
            if w.run_league:
                if play_league(parent, w.run_league):
                    return
                continue
        return
