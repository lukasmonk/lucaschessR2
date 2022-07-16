from PySide2 import QtWidgets, QtCore

import Code
from Code import XRun
from Code.Base.Constantes import RESULT_WIN_WHITE, RESULT_DRAW, RESULT_WIN_BLACK
from Code.Base import Game
from Code.Databases import DBgames
from Code.Leagues import LeaguesWork
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL

NONE, PLAY_HUMAN, REINIT = range(3)


class WLeague(LCDialog.LCDialog):
    def __init__(self, w_parent, league):

        titulo = "%s - %s %d" % (league.name(), _("Season"), league.get_current_season() + 1)
        icono = Iconos.League()
        extparam = "league"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.league = league
        self.season = league.read_season()
        self.li_panels = self.season.gen_panels()
        self.dic_xid_name = self.league.dic_names()
        self.terminated = False
        self.play_human = None
        self.result = NONE
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_matchs)

        self.color_win = QTUtil.qtColor("#007aae")
        self.color_lost = QTUtil.qtColor("#f47378")
        self.color_white = QTUtil.qtColor("white")

        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Launch a worker"), Iconos.Lanzamiento(), self.launch_worker),
            None,
            (_("Update"), Iconos.Update(), self.update_matchs),
            None,
            (_("Utilities"), Iconos.Utilidades(), self.utilities),
            None,
        )
        self.tb = QTVarios.LCTB(self, li_acciones)

        self.tab = Controles.Tab(self).ponTipoLetra(puntos=10).set_position("S")
        font = Controles.TipoLetra(puntos=10)

        self.li_grids_divisions = []
        ly = Colocacion.H()
        li_nom_divisions = [_("First Division"), _("Second Division"), _("Third Division")]
        tr = Controles.Tab(self).ponTipoLetra(puntos=10).set_position("S")
        for division in range(3):
            o_col = Columnas.ListaColumnas()
            o_col.nueva("ORDER", "", 40, align_center=True)
            o_col.nueva("OPPONENT", _("Opponent"), 200)
            o_col.nueva("PTS", _("Pts ||Points/score"), 50, align_center=True)
            o_col.nueva("PL", _("GP ||Games played"), 40, align_center=True)
            o_col.nueva("WIN", _("W ||Games won"), 50, align_center=True)
            o_col.nueva("DRAW", _("D ||Games drawn"), 50, align_center=True)
            o_col.nueva("LOST", _("L ||Games lost"), 50, align_center=True)
            # o_col.nueva("TB", _("TB||Tie-break"), 50, align_center=True)
            o_col.nueva("ACT_ELO", _("Current ELO"), 90, align_center=True)
            o_col.nueva("DIF_ELO", "∆", 60, align_center=True)
            o_col.nueva("INI_ELO", _("Initial ELO"), 90, align_center=True)
            grid = Grid.Grid(self, o_col, xid="CLASSIFICATION%d" % division, siSelecFilas=True)
            grid.setFont(font)
            self.register_grid(grid)
            self.li_grids_divisions.append(grid)
            tr.addTab(grid, li_nom_divisions[division])
        ly.control(tr)

        w = QtWidgets.QWidget(self)
        w.setLayout(ly)
        self.tab.addTab(w, "")
        self.tab.setIconSize(QtCore.QSize(32, 32))
        self.tab.ponIcono(0, Iconos.Classification())

        self.li_grids_journeys = []
        for journey in range(18):
            ly = Colocacion.H()
            tr = Controles.Tab(self).ponTipoLetra(puntos=10).set_position("S")
            for division in range(3):
                o_col = Columnas.ListaColumnas()
                o_col.nueva("WHITE", _("White"), 240, align_center=True)
                o_col.nueva("BLACK", _("Black"), 240, align_center=True)
                o_col.nueva("RESULT", _("Result"), 240, align_center=True)
                grid = Grid.Grid(self, o_col, xid="J%dD%d" % (journey, division), altoFila=48, siSelecFilas=True)
                self.register_grid(grid)
                self.li_grids_journeys.append(grid)
                grid.setFont(font)
                tr.addTab(grid, li_nom_divisions[division])
            ly.control(tr)

            w = QtWidgets.QWidget(self)
            w.setLayout(ly)
            self.tab.addTab(w, str(journey + 1))

        self.current_journey = self.season.get_current_journey()
        self.tab.ponIcono(self.current_journey + 1, Iconos.Journey())

        layout = Colocacion.V().control(self.tb).control(self.tab).margen(8)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=784, altoDefecto=460)

        self.update_matchs()

    def grid_num_datos(self, grid):
        if grid in self.li_grids_divisions:
            return 10
        return 5

    def grid_dato_division(self, num_division, row, nom_column):
        if nom_column == "ORDER":
            return str(row + 1)
        d_panel = self.li_panels[num_division][row]
        if nom_column == "OPPONENT":
            return self.dic_xid_name[d_panel["XID"]]
        if nom_column == "DIF_ELO":
            dif = d_panel["ACT_ELO"] - d_panel["INI_ELO"]
            if dif == 0:
                return "-"
            if dif > 0:
                return "+%d" % dif
            else:
                return "%d" % dif
        return str(d_panel[nom_column])

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        if grid in self.li_grids_divisions:
            division = self.li_grids_divisions.index(grid)
            return self.grid_dato_division(division, row, column)
        else:
            xid = grid.id
            j, d = xid[1:].split("D")
            journey = int(j)
            division = int(d)
            match = self.season.match(division, journey, row)
            if column == "RESULT":
                result = match.result
                if result is None:
                    if match.is_human_vs_engine(self.league):
                        return _("Double click to play") if journey == self.current_journey else "-"
                    if match.is_human_vs_human(self.league):
                        return _("Double click to edit") if journey == self.current_journey else "-"
                    return "-"
                else:
                    return result
            if column == "WHITE":
                return self.dic_xid_name[match.xid_white]
            else:
                return self.dic_xid_name[match.xid_black]

    def grid_doble_click(self, grid, row, o_column):
        if grid in self.li_grids_divisions:
            pass
        else:
            xid = grid.id
            j, d = xid[1:].split("D")
            journey = int(j)
            division = int(d)
            match = self.season.match(division, journey, row)
            if match.result:
                game = self.season.get_game_match(match)
                if game:
                    game = Code.procesador.manager_game(self, game, True, False, None)
                    if game:
                        self.season.put_match_done(game)
                        grid.refresh()

            elif match.is_human_vs_engine(self.league):
                self.play_human = self.league, match, division
                self.result = PLAY_HUMAN
                self.accept()

            elif match.is_human_vs_human(self.league):
                game = Game.Game()
                game.set_tag("Site", Code.lucas_chess)
                game.set_tag("Event", self.league.name())
                game.set_tag("Season", str(self.league.current_num_season + 1))
                game.set_tag("Division", str(division + 1))
                game.set_tag("White", self.league.opponent_by_xid(match.xid_white).name())
                game.set_tag("Black", self.league.opponent_by_xid(match.xid_black).name())
                panel = self.li_panels[division]
                elo_white = elo_black = 0
                for elem in panel:
                    if elem["XID"] == match.xid_white:
                        elo_white = elem["ACT_ELO"]
                    elif elem["XID"] == match.xid_black:
                        elo_black = elem["ACT_ELO"]
                game.set_tag("WhiteElo", str(elo_white))
                game.set_tag("BlackElo", str(elo_black))

                menu = QTVarios.LCMenu(self)
                menu.opcion(RESULT_DRAW, RESULT_DRAW, Iconos.Tablas())
                menu.separador()
                menu.opcion(RESULT_WIN_WHITE, RESULT_WIN_WHITE, Iconos.Blancas())
                menu.separador()
                menu.opcion(RESULT_WIN_BLACK, RESULT_WIN_BLACK, Iconos.Negras())
                resp = menu.lanza()
                if resp is None:
                    return
                game.set_tag("Result", resp)

                while True:
                    game_resp = Code.procesador.manager_game(self, game, True, False, None)
                    if game_resp:
                        game_resp.check()
                        if game.resultado() in (RESULT_WIN_BLACK, RESULT_DRAW, RESULT_WIN_WHITE):
                            match.result = game.resultado()
                            self.season.put_match_done(match, game)
                            self.update_matchs()
                            grid.refresh()
                            return
                        else:
                            QTUtil2.message_error(self, _("The game must have a valid result tag"))
                            game = game_resp
                    else:
                        return

    def grid_color_texto(self, grid, row, o_column):
        if grid in self.li_grids_divisions:
            if self.season.is_finished():
                if row < 3:
                    return self.color_win
                if row > 6:
                    return self.color_lost

    def grid_color_fondo(self, grid, row, o_column):
        if grid in self.li_grids_divisions and self.season.is_finished() and (row < 3 or row > 6):
            return self.color_white

    def grid_bold(self, grid, row, o_column):
        return grid in self.li_grids_divisions and self.season.is_finished() and (row < 3 or row > 6)

    def update_matchs(self):
        if self.terminated:
            return
        journey = self.current_journey
        if self.season.is_finished():
            self.timer.stop()
            self.season.test_next()
            self.tb.setAccionVisible(self.update_matchs, False)
            self.tb.setAccionVisible(self.launch_worker, False)
            return
        changed = False
        for division in range(3):
            for nmatch in range(5):
                match = self.season.match(division, journey, nmatch)
                if match.result is None:
                    with UtilSQL.DictRawSQL(self.league.path(), "SEASON_%d" % self.league.current_num_season) as db:
                        game_saved = db[match.xid]
                        if game_saved is not None:
                            game = Game.Game()
                            game.restore(game_saved)
                            match.result = game.result
                            changed = True

        if changed:
            self.season.save()
            self.show_current_season()

        if self.timer:
            lw = LeaguesWork.LeaguesWork(self.league)
            if lw.num_working_matchs():
                self.timer.stop()
                self.timer.start(10000)
            else:
                self.timer.stop()
                self.timer.start(60000)

        if not self.season.is_pendings_matchs():
            self.current_journey = self.season.new_journey(self.league)
            self.tab.ponIcono(self.current_journey, None)
            self.tab.ponIcono(self.current_journey + 1, Iconos.Journey())
            return

    def show_current_season(self):
        journey = self.current_journey
        self.li_panels = self.season.gen_panels()
        for grid in self.li_grids_divisions:
            grid.refresh()
        for grid in self.li_grids_journeys[: journey + 1]:
            grid.refresh()

    def terminar(self):
        self.terminated = True
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.save_video()
        self.accept()

    def closeEvent(self, event):
        self.terminated = True
        if self.timer:
            self.timer.stop()
            self.timer = None

    def launch_worker(self):
        self.update_matchs()
        lw = LeaguesWork.LeaguesWork(self.league)
        journey_work, season_work = lw.get_journey_season()
        current_journey = self.season.get_current_journey()
        if journey_work != current_journey or self.league.current_num_season != season_work:
            lw.put_league()
        if lw.num_pending_matchs():
            XRun.run_lucas("-league", self.league.name())

    def utilities(self):
        menu = QTVarios.LCMenu(self)
        li_seasons = self.season.list_seasons()
        if len(li_seasons) > 1:
            submenu = menu.submenu(_("Change the active season"))
            for num_season in li_seasons:
                if self.season.num_season != num_season:
                    submenu.opcion(str(num_season), str(num_season + 1))
        menu.separador()
        submenu = menu.submenu(_("Save all games to a database"), Iconos.DatabaseMas())
        QTVarios.menuDB(submenu, Code.configuration, True, indicador_previo="dbf_", remove_autosave=True)
        menu.separador()

        resp = menu.lanza()
        if resp is None:
            return

        if resp.startswith("dbf_"):
            um = QTUtil2.unMomento(self, _("Working..."))
            li_games = self.season.list_games()
            database = resp[4:]
            db = DBgames.DBgames(database)
            for game in li_games:
                db.insert(game)
            db.close()
            um.final()
            if len(li_games):
                QTUtil2.mensajeTemporal(self, _("Saved") + " [%d]" % len(li_games), 1.8)

        else:
            num_season = int(resp)
            self.league.set_current_season(num_season)
            self.result = REINIT
            self.accept()


def play_league(parent, league):
    w = WLeague(parent, league)
    if w.exec_():
        if w.result == PLAY_HUMAN:
            return w.play_human
        elif w.result == REINIT:
            return play_league(parent, league)
