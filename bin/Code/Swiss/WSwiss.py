import collections

from PySide2 import QtWidgets, QtCore

import Code
from Code import XRun, Util
from Code.Base import Game
from Code.Base.Constantes import RESULT_WIN_WHITE, RESULT_DRAW, RESULT_WIN_BLACK
from Code.Databases import DBgames, WDB_Games
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL
from Code.Swiss import SwissWork, Swiss

NONE, PLAY_HUMAN, REINIT = range(3)


class WSwiss(LCDialog.LCDialog):
    def __init__(self, w_parent, swiss: Swiss.Swiss):

        self.swiss: Swiss.Swiss = swiss
        self.season = swiss.read_season()
        titulo = swiss.name()
        icono = Iconos.Swiss()
        extparam = "swiss"
        LCDialog.LCDialog.__init__(self, w_parent, titulo, icono, extparam)

        self.panel_classification, self.dic_xid_order = self.season.gen_panel_classification()
        self.panel_crosstabs = self.season.gen_panel_crosstabs()
        self.li_sorted_opponents = self.season.list_sorted_opponents()
        self.mix_panels()

        self.current_journey = self.season.get_last_journey()
        self.li_matches = self.season.get_all_matches_last_journey()
        self.max_journeys = self.swiss.max_journeys()
        self.dic_xid_name = self.swiss.dic_names()
        self.terminated = False
        self.play_human = None
        self.result = NONE
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_matches)

        self.num_workers_launched = 0

        self.grid_crosstabs = self.grid_classification = None

        self.color_win = Code.dic_qcolors["WLEAGUE_WIN"]
        self.color_lost = Code.dic_qcolors["WLEAGUE_LOST"]
        self.color_noresult = Code.dic_qcolors["WLEAGUE_NORESULT"]
        self.color_draw = Code.dic_qcolors["WLEAGUE_DRAW"]

        self.tb = QTVarios.LCTB(self)

        self.tab = Controles.Tab(self).ponTipoLetra(puntos=10).set_position("S")
        self.tab.dispatchChange(self.tab_changed)
        font = Controles.TipoLetra(puntos=10)

        self.grid_games = None

        sw = "◻  "
        sb = "◼  "
        o_col = Columnas.ListaColumnas()
        o_col.nueva("NAME", _("Player"), 150)
        o_col.nueva("PTS", _("Pts ||Points/score"), 50, align_center=True)
        o_col.nueva("PL", _("GP ||Games played"), 40, align_center=True)
        o_col.nueva("WIN", _("W ||Games won"), 50, align_center=True)
        o_col.nueva("DRAW", _("D ||Games drawn"), 50, align_center=True)
        o_col.nueva("LOST", _("L ||Games lost"), 50, align_center=True)
        o_col.nueva("ACT_ELO", _("Current ELO"), 90, align_center=True)
        o_col.nueva("DIF_ELO", "∆", 60, align_center=True)
        o_col.nueva("INI_ELO", _("Initial ELO"), 90, align_center=True)
        for num_op in range(len(self.panel_classification)):
            o_col.nueva("w%d" % num_op, sw + str(num_op + 1), 40, align_center=True)
            o_col.nueva("b%d" % num_op, sb + str(num_op + 1), 40, align_center=True)

        self.grid_classification = Grid.Grid(self, o_col, xid="CLASSIF", with_header_vertical=True)
        self.grid_classification.setFont(font)

        self.tab.addTab(self.grid_classification, _("Classification"))
        self.tab.setIconSize(QtCore.QSize(32, 32))
        self.tab.ponIcono(0, Iconos.Classification())

        # CROSSTABS ----------------------------------------------------------------------------------------------------
        ly = Colocacion.H()
        o_col = Columnas.ListaColumnas()
        o_col.nueva("ORDER", _("Order"), 30, align_center=True)
        for opponent in self.li_sorted_opponents:
            o_col.nueva(opponent.xid, opponent.name(), 30, align_center=True)
        self.grid_crosstabs = Grid.Grid(
            self,
            o_col,
            xid="CROSSTABS",
            siSelecFilas=False,
            cab_vertical_font=180,
            with_header_vertical=True,
        )
        self.grid_crosstabs.setFont(font)
        self.grid_crosstabs.set_headervertical_alinright()
        # self.register_grid(grid)
        ly.control(self.grid_crosstabs)

        w = QtWidgets.QWidget(self)
        w.setLayout(ly)

        self.tab.addTab(w, _("Crosstabs"))
        self.tab.setIconSize(QtCore.QSize(32, 32))
        self.tab.ponIcono(1, Iconos.Crosstable())

        # Matches -----------------------------------------------------------------------------------------------------
        o_col = Columnas.ListaColumnas()
        o_col.nueva("WHITE", _("White"), 240)
        o_col.nueva("BLACK", _("Black"), 240)
        o_col.nueva("RESULT", _("Result"), 180, align_center=True)
        self.grid_matches = Grid.Grid(self, o_col, siSelecFilas=True)
        self.register_grid(self.grid_matches)
        self.grid_matches.setFont(font)

        self.dic_order = {}

        tbj = QTVarios.LCTB(self, with_text=False, icon_size=24, style=QtCore.Qt.ToolButtonIconOnly)
        tbj.new("", Iconos.MoverInicio(), self.journey_first, False)
        tbj.new("", Iconos.MoverAtras(), self.journey_previous, False)
        tbj.new("", Iconos.Journey(), self.journey_active, False)
        tbj.new("", Iconos.MoverAdelante(), self.journey_next, False)
        tbj.new("", Iconos.MoverFinal(), self.journey_last, False)

        fontd = Controles.TipoLetra(puntos=12)

        lb_journey = Controles.LB(self, _("Matchday") + ": ").ponFuente(fontd)
        self.sb_journey = Controles.SB(self, self.current_journey + 1, 1, self.max_journeys).ponFuente(fontd)
        self.sb_journey.setFixedWidth(50)
        self.sb_journey.capture_changes(self.change_sb)
        lb_info_journey = Controles.LB(self, "/ %d" % self.max_journeys).ponFuente(fontd)

        self.lb_active = (
            Controles.LB(self, _("CURRENT MATCHDAY"))
            .ponFuente(Controles.TipoLetra(puntos=16, peso=400))
            .align_center()
            .anchoMinimo(400)
        )
        self.lb_active.setStyleSheet(
            "color: %s;background: %s;padding-left:5px;padding-right:5px;" % ("white", "#437FBC")
        )

        ly0 = (
            Colocacion.H()
            .espacio(8)
            .control(lb_journey)
            .control(self.sb_journey)
            .control(lb_info_journey)
            .control(tbj)
            .relleno()
            .control(self.lb_active)
            .relleno()
        )
        ly = Colocacion.V().otro(ly0).control(self.grid_matches)

        w = QtWidgets.QWidget(self)
        w.setLayout(ly)
        self.tab.addTab(w, _("Matches"))

        # Games -----------------------------------------------------------------------------------------------------
        lb_journey = Controles.LB2P(self, _("Journey"))
        self.cb_cjourney = Controles.CB(self, [], None).capture_changes(self.filter_games)
        lb_player = Controles.LB2P(self, _("Player"))
        self.cb_player = Controles.CB(self, [], None).capture_changes(self.filter_games)
        lb_white = Controles.LB2P(self, _("White"))
        self.cb_white = Controles.CB(self, [], None).capture_changes(self.filter_games)
        lb_black = Controles.LB2P(self, _("Black"))
        self.cb_black = Controles.CB(self, [], None).capture_changes(self.filter_games)
        lb_result = Controles.LB2P(self, _("Result"))
        self.cb_result = Controles.CB(self, [], None).capture_changes(self.filter_games)
        ly_filter = Colocacion.H()
        ly_filter.control(lb_journey).control(self.cb_cjourney).relleno()
        ly_filter.control(lb_white).control(self.cb_white).relleno()
        ly_filter.control(lb_black).control(self.cb_black).relleno()
        ly_filter.control(lb_player).control(self.cb_player).relleno()
        ly_filter.control(lb_result).control(self.cb_result).relleno()

        o_col = Columnas.ListaColumnas()
        o_col.nueva("NUMBER", _("N."), 35, align_center=True)
        o_col.nueva("CJOURNEY", _("Journey"), 60, align_center=True)
        o_col.nueva("WHITE", _("White"), 240)
        o_col.nueva("BLACK", _("Black"), 240)
        o_col.nueva("RESULT", _("Result"), 180, align_center=True)
        self.grid_games = Grid.Grid(self, o_col, siSelecFilas=True)
        self.register_grid(self.grid_games)
        self.grid_games.setFont(font)
        self.li_matches_played = []  # se determinan al entrar en la pestaña de Games
        self.li_matches_played_all = []

        ly = Colocacion.V().otro(ly_filter).control(self.grid_games)

        w = QtWidgets.QWidget(self)
        w.setLayout(ly)
        self.tab.addTab(w, _("All games played"))

        layout = Colocacion.V().control(self.tb).control(self.tab).margen(8)
        self.setLayout(layout)

        self.restore_video(siTam=True, anchoDefecto=784, altoDefecto=460)

        self.update_matches()

        self.set_journey_if_active()

        self.grid_classification.resizeColumnToContents(0)

    def tab_changed(self):
        if self.tab.current_position() == 3:
            st_cjourneys = set()
            st_white = set()
            st_black = set()
            st_players = set()
            st_results = set()
            # dic_raw_games = self.season.dic_raw_games()
            self.li_matches_played_all = []
            for journey in range(self.season.get_last_journey() + 1):
                li_matches = []
                match: Swiss.Match
                for match in self.season.get_all_matches(journey):
                    if match.result:
                        match.journey = journey
                        match.cjourney = str(journey + 1)
                        st_cjourneys.add(match.cjourney)
                        match.white_name = self.dic_xid_name[match.xid_white]
                        st_white.add(match.white_name)
                        st_players.add(match.white_name)
                        match.black_name = self.dic_xid_name[match.xid_black]
                        st_black.add(match.black_name)
                        st_players.add(match.black_name)
                        li_matches.append(match)
                        st_results.add(match.result)
                self.li_matches_played_all.extend(li_matches)
            self.adjust_filter_games(st_cjourneys, st_white, st_black, st_players, st_results)
            self.filter_games()

    def adjust_filter_games(self, st_cjourneys, st_white, st_black, st_players, st_results):
        def one(st, cb):
            lir = [(_("All"), None)]
            for value in sorted(list(st)):
                lir.append((value, value))
            cb.rehacer(lir, cb.valor())

        one(st_cjourneys, self.cb_cjourney)
        one(st_white, self.cb_white)
        one(st_black, self.cb_black)
        one(st_players, self.cb_player)
        one(st_results, self.cb_result)

    def filter_games(self):
        li = []
        filter_cjourney = self.cb_cjourney.valor()
        filter_white = self.cb_white.valor()
        filter_black = self.cb_black.valor()
        filter_player = self.cb_player.valor()
        filter_result = self.cb_result.valor()
        match: Swiss.Match
        for match in self.li_matches_played_all:
            if filter_cjourney and match.cjourney != filter_cjourney:
                continue
            if filter_white and match.white_name != filter_white:
                continue
            if filter_black and match.black_name != filter_black:
                continue
            if filter_player and match.white_name != filter_player and match.black_name != filter_player:
                continue
            if filter_result and match.result != filter_result:
                continue
            li.append(match)
        self.li_matches_played = li
        self.grid_games.refresh()
        self.grid_games.gotop()

    def config(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(
            "continue",
            _("Launch new workers when a matchday ends"),
            Iconos.Unchecked() if self.season.stop_work_journey else Iconos.Checked(),
        )
        resp = menu.lanza()
        if resp:
            self.season.stop_work_journey = not self.season.stop_work_journey
            self.season.save()

    def set_journey_if_active(self):
        if self.season.is_finished():
            active = False
        else:
            antes = self.current_journey
            self.current_journey = self.season.get_last_journey()
            if antes != self.current_journey:
                self.update_matches()
                lw = SwissWork.SwissWork(self.swiss)
                lw.put_swiss()
                if self.pending_matches() and not self.season.stop_work_journey:
                    for x in range(self.num_workers_launched):
                        XRun.run_lucas("-swiss", self.swiss.name())
            active = self.current_journey == self.sb_journey.valor() - 1
        self.lb_active.setVisible(active)

        self.set_toolbar()

    def set_toolbar(self):
        self.tb.clear()
        self.tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        if not self.season.is_finished():
            self.tb.new(_("Launch a worker"), Iconos.Lanzamiento(), self.launch_worker)
            self.tb.new(_("Update"), Iconos.Update(), self.update_matches)
        self.tb.new(_("Export"), Iconos.Export8(), self.export)
        li_seasons = self.swiss.list_seasons()
        ok = len(li_seasons) > 1 or self.season.is_finished()
        if ok:
            self.tb.new(_("Seasons"), Iconos.Season(), self.seasons)
        self.tb.new(_("Config"), Iconos.Configurar(), self.config)

    def set_journey(self, pos):
        if 0 < pos <= self.max_journeys:
            self.sb_journey.setValue(pos)
            self.li_matches = self.season.get_all_matches_journey(pos - 1)
            self.grid_matches.refresh()
            self.set_journey_if_active()

    def change_sb(self):
        pos = self.sb_journey.valor()
        self.li_matches = self.season.get_all_matches_journey(pos - 1)
        self.set_journey_if_active()
        self.grid_matches.refresh()

    def journey_first(self):
        self.set_journey(1)

    def journey_last(self):
        self.set_journey(self.max_journeys)

    def journey_previous(self):
        self.set_journey(self.sb_journey.valor() - 1)

    def journey_next(self):
        self.set_journey(self.sb_journey.valor() + 1)

    def journey_active(self):
        self.set_journey(self.current_journey + 1)

    def grid_num_datos(self, grid):
        if grid == self.grid_classification:
            return len(self.panel_classification)
        elif grid == self.grid_crosstabs:
            return len(self.panel_crosstabs) + 1
        elif grid == self.grid_games:
            return len(self.li_matches_played) if self.li_matches_played else 0
        else:
            return len(self.li_matches)

    def grid_dato(self, grid, row, o_column):
        column = o_column.key
        if grid == self.grid_classification:
            return self.grid_dato_classification(row, column)
        elif grid == self.grid_crosstabs:
            return self.grid_dato_crosstab(row, column)

        elif grid == self.grid_games:
            if column == "NUMBER":
                return str(row + 1)
            return self.grid_dato_games(row, column)

        else:
            xmatch = self.li_matches[row]
            if column == "RESULT":
                result = xmatch.result
                if result is None:
                    active = self.current_journey == self.sb_journey.valor() - 1
                    if xmatch.is_human_vs_engine(self.swiss):
                        return _("Double click to play") if active else "-"
                    if xmatch.is_human_vs_human(self.swiss):
                        return _("Double click to edit") if active else "-"
                    return "-"
                else:
                    return result
            if column == "WHITE":
                return self.dic_xid_name[xmatch.xid_white]
            elif column == "BLACK":
                return self.dic_xid_name[xmatch.xid_black]

    def grid_color_fondo(self, grid, row, o_column):
        if grid == self.grid_crosstabs:
            column = o_column.key
            return self.grid_color_fondo_crosstabs(row, column)

    def grid_doubleclick_header(self, grid, col):
        if grid == self.grid_matches:
            key = col.key
            order_prev = self.dic_order.get(key, False)
            self.dic_order[key] = order = not order_prev

            li = [(self.grid_dato(grid, row, col), xmatch) for row, xmatch in enumerate(self.li_matches)]
            li.sort(key=lambda x: x[0], reverse=not order)
            self.li_matches = [xmatch for dato, xmatch in li]

        elif grid == self.grid_classification:
            key_order = "D", col.key
            order_next = self.dic_order.get(key_order, 0) + 1
            if order_next > 2:
                order_next = 0
            self.dic_order[key_order] = order_next

            li_panel = self.panel_classification
            if order_next == 0:
                li_panel.sort(key=lambda x: x["ORDER"])
            else:
                if col.key == "DIF_ELO":
                    li_panel.sort(key=lambda x: x["ACT_ELO"] - x["INI_ELO"], reverse=order_next == 2)

                elif col.key[0] in "wb":

                    def xsort(dic):
                        x = dic[col.key]
                        if x in ("", "-"):
                            return -1.0
                        else:
                            return float(x)

                    li_panel.sort(key=xsort, reverse=order_next == 2)

                else:
                    li_panel.sort(key=lambda x: x[col.key], reverse=order_next == 2)

        elif grid == self.grid_crosstabs:
            if col.key != "ORDER":
                return

            key_order = "C", "H"
            pos_order = self.dic_order.get(key_order, 0)
            pos_order += 1
            if pos_order > 2:
                pos_order = 0
            self.dic_order[key_order] = pos_order

            def order_classification(x):
                return self.dic_xid_order[x.xid]

            def order_classification_v(x):
                return -self.dic_xid_order[x.xid]

            def order_alphabetically(x):
                return self.dic_xid_name[x.xid]

            if pos_order == 0:
                func_order = order_alphabetically
            elif pos_order == 1:
                func_order = order_classification
            else:
                func_order = order_classification_v

            self.li_sorted_opponents.sort(key=func_order)

        elif grid == self.grid_games:
            keyg = col.key + "G"

            order_prev = self.dic_order.get(keyg, False)
            self.dic_order[keyg] = order = not order_prev
            self.li_matches.sort(key=lambda x: x[col.key], reverse=not order)

        grid.refresh()
        grid.gotop()

    def grid_doubleclick_header_vertical(self, grid, row):
        if grid == self.grid_classification:
            self.grid_doble_click(grid, row, None)
        elif grid == self.grid_crosstabs:
            if row == 0:
                key_order = "C", "V"
                pos_order = self.dic_order.get(key_order, 0)
                pos_order += 1
                if pos_order > 2:
                    pos_order = 0
                self.dic_order[key_order] = pos_order

                def order_classification(x):
                    return self.dic_xid_order[x.key] if x.key != "ORDER" else 0

                def order_classification_v(x):
                    return -self.dic_xid_order[x.key] if x.key != "ORDER" else -999999

                def order_alphabetically(x):
                    return self.dic_xid_name[x.key] if x.key != "ORDER" else "      "

                if pos_order == 0:
                    func_order = order_alphabetically
                elif pos_order == 1:
                    func_order = order_classification
                else:
                    func_order = order_classification_v

                li_columnas = grid.oColumnasR.li_columns
                li_columnas.sort(key=func_order)
                grid.refresh()

    def grid_dato_classification(self, row, nom_column):
        d_panel = self.panel_classification[row]
        if nom_column == "DIF_ELO":
            dif = d_panel["ACT_ELO"] - d_panel["INI_ELO"]
            if dif == 0:
                return "-"
            if dif > 0:
                return "+%d" % dif
            else:
                return "%d" % dif
        if nom_column == "PTS":
            cpts = "%0.02f" % d_panel[nom_column]
            while cpts.endswith("0"):
                cpts = cpts[:-1]
            if cpts.endswith("."):
                cpts = cpts[:-1]
            return cpts
        if nom_column == "NAME":
            return self.dic_xid_name[d_panel["XID"]]
        return str(d_panel[nom_column])

    def grid_dato_crosstab(self, row, nom_column):
        other_xid = nom_column
        if row == 0:
            if nom_column == "ORDER":
                return ""
            else:
                return str(self.dic_xid_order[other_xid])
        op_xid = self.li_sorted_opponents[row - 1].xid
        if op_xid == other_xid:
            return ""
        if nom_column == "ORDER":
            return str(self.dic_xid_order[op_xid])

        result = self.panel_crosstabs[op_xid][other_xid]
        if result is None:
            return ""
        if result == RESULT_DRAW:
            return _("D ||Games drawn")
        if result == RESULT_WIN_WHITE:
            return _("W ||White")
        else:
            return _("B ||Black")

    def grid_dato_games(self, row, nom_column):
        match = self.li_matches_played[row]
        if nom_column == "CJOURNEY":
            return match.cjourney
        if nom_column == "WHITE":
            return match.white_name
        if nom_column == "BLACK":
            return match.black_name
        if nom_column == "RESULT":
            return match.result

    def grid_get_header_vertical(self, grid, col):
        if grid == self.grid_crosstabs:
            if col == 0:
                return _("Order")
            return self.li_sorted_opponents[col - 1].name()

        elif grid == self.grid_classification:
            d_panel = self.panel_classification[col]
            return " %2d " % self.dic_xid_order[d_panel["XID"]]

    def grid_color_fondo_crosstabs(self, row, nom_column):
        if nom_column == "ORDER" or row == 0:
            return
        other_xid = nom_column
        op_xid = self.li_sorted_opponents[row - 1].xid
        if op_xid == other_xid:
            return
        result = self.panel_crosstabs[op_xid][other_xid]
        if result is None:
            return self.color_noresult
        if result == RESULT_DRAW:
            return self.color_draw
        if result == RESULT_WIN_WHITE:
            return self.color_win
        else:
            return self.color_lost

    def consult_matches(self, grid, row):
        d_panel = self.panel_classification[row]
        xid_engine = d_panel["XID"]
        li_matches_played = self.season.get_all_matches_opponent(xid_engine)
        if len(li_matches_played) == 0:
            return
        self.select_match(li_matches_played, xid_engine)

    def select_match(self, li_matches, xid_engine):
        win = _("Win")
        draw = _("Draw")
        lost = _("Loss")
        dic = collections.defaultdict(list)
        dicon = {0: Iconos.Rojo(), 5: Iconos.Naranja(), 10: Iconos.Azul(), 15: Iconos.Verde(), 20: Iconos.Magenta()}
        for xmatch in li_matches:
            white = self.dic_xid_name[xmatch.xid_white]
            black = self.dic_xid_name[xmatch.xid_black]
            result = xmatch.result
            if xmatch.xid_white == xid_engine:
                icon = Iconos.Blancas()
                opponent = black
                cresult = win if result == RESULT_WIN_WHITE else (lost if result == RESULT_WIN_BLACK else draw)
            else:
                icon = Iconos.Negras()
                opponent = white
                cresult = win if result == RESULT_WIN_BLACK else (lost if result == RESULT_WIN_WHITE else draw)
            dic[opponent].append((xmatch, icon, cresult))

        menu = QTVarios.LCMenu(self)
        menu.ponTipoLetra(name=Code.font_mono, puntos=10)

        li_names = list(dic.keys())
        li_names.sort()

        for opponent in li_names:
            li = dic[opponent]
            pt = 0
            for xmatch, icon, cresult in li:
                if cresult == win:
                    pt += 10
                elif cresult == draw:
                    pt += 5
            submenu = menu.submenu(opponent, dicon.get(pt, Iconos.PuntoNegro()))
            for xmatch, icon, cresult in li:
                submenu.opcion(xmatch, cresult, icon)
            menu.separador()
        xmatch = menu.lanza()
        if xmatch:
            self.show_match_done(xmatch)

    def consult_matches_classification(self, grid, row):
        xmatch = self.li_matches[row]
        if xmatch.result:
            self.show_match_done(xmatch)
            grid.refresh()

        elif xmatch.is_human_vs_engine(self.swiss):
            self.play_human = self.swiss, xmatch
            self.result = PLAY_HUMAN
            self.accept()

        elif xmatch.is_human_vs_human(self.swiss):
            game = Game.Game()
            game.set_tag("Site", Code.lucas_chess)
            game.set_tag("Event", self.swiss.name())
            game.set_tag("Season", str(self.swiss.current_num_season + 1))
            game.set_tag("White", self.swiss.opponent_by_xid(xmatch.xid_white).name())
            game.set_tag("Black", self.swiss.opponent_by_xid(xmatch.xid_black).name())
            panel = self.panel_classification
            elo_white = elo_black = 0
            for elem in panel:
                if elem["XID"] == xmatch.xid_white:
                    elo_white = elem["ACT_ELO"]
                elif elem["XID"] == xmatch.xid_black:
                    elo_black = elem["ACT_ELO"]
            game.set_tag("WhiteElo", str(elo_white))
            game.set_tag("BlackElo", str(elo_black))

            game_resp = Code.procesador.manager_game(self, game, True, False, None)
            if game_resp:
                game_resp.verify()

                result = game.resultado()
                if result not in (RESULT_WIN_BLACK, RESULT_DRAW, RESULT_WIN_WHITE):
                    result = QTVarios.get_result_game(self)
                    if result is None:
                        return
                    game.set_tag("RESULT", result)

                xmatch.result = game.resultado()
                self.season.put_match_done(xmatch, game)
                self.update_matches()
                grid.refresh()

    def consult_matches_crosstabs(self, grid, row, other_xid):
        if other_xid == "ORDER" or row == 0:
            return
        op_xid = self.li_sorted_opponents[row - 1].xid
        li_matches_played = self.season.get_all_matches_opponent(op_xid)
        if other_xid == op_xid:
            self.select_match(li_matches_played, op_xid)
            return
        xmatch: Swiss.Match
        for xmatch in li_matches_played:
            if other_xid == xmatch.xid_black:
                self.show_match_done(xmatch)

    def grid_right_button(self, grid, row, col, modif):
        self.grid_doble_click(grid, row, col)

    def grid_doble_click(self, grid, row, o_column):
        if grid == self.grid_classification:
            nom_column = o_column.key if o_column else None
            if nom_column and nom_column[0] in "wb":
                is_white = nom_column.startswith("w")
                row_other = int(nom_column[1:])
                d_panel = self.panel_classification[row]
                if d_panel[nom_column] == "-":
                    return

                xid = d_panel["XID"]
                d_panel_other = self.panel_classification[row_other]
                xid_other = d_panel_other["XID"]
                if not is_white:
                    xid, xid_other = xid_other, xid
                xmatch = self.season.get_match(xid, xid_other)
                if xmatch:
                    self.show_match_done(xmatch)
                return

            else:
                self.consult_matches(grid, row)

        elif grid == self.grid_classification:
            self.consult_matches_crosstabs(grid, row, o_column.key)

        elif grid == self.grid_games:
            match = self.li_matches[row]
            xmatch = Swiss.Match(match.xid_white, match.xid_black)
            xmatch.xid = match.xid
            self.show_match_done(xmatch)

        else:
            self.consult_matches_classification(grid, row)

    def show_match_done(self, xmatch):
        game = self.season.get_game_match(xmatch)
        if game:
            game = Code.procesador.manager_game(self, game, True, False, None)
            if game:
                if xmatch.is_human_vs_human(self.swiss):
                    result = game.resultado()
                    if result in (RESULT_WIN_WHITE, RESULT_WIN_BLACK, RESULT_DRAW):
                        xmatch.result = result
                self.season.put_match_done(xmatch, game)
                self.show_current_season()

    def update_matches(self):
        if self.terminated:
            return
        journey = self.current_journey
        if self.season.is_finished():
            self.journey_first()
            self.timer.stop()
            self.season.test_next()
            self.set_toolbar()
            return
        if not self.season.is_pendings_matches(journey):
            self.season.create_matches_day()
            journey += 1
            self.set_journey(journey)

        changed = False
        for xmatch in self.season.get_all_matches(journey):
            if xmatch.result is None:
                with UtilSQL.DictRawSQL(self.swiss.path(), "SEASON_%d" % self.swiss.current_num_season) as db:
                    game_saved = db[xmatch.xid]
                    if game_saved is not None:
                        game = Game.Game()
                        game.restore(game_saved)
                        xmatch.result = game.result
                        changed = True

        if changed:
            self.swiss.save()
            self.show_current_season()

        self.set_journey_if_active()

        if self.timer:
            lw = SwissWork.SwissWork(self.swiss)
            if lw.num_working_matches():
                self.timer.stop()
                self.timer.start(10000)
            else:
                self.timer.stop()
                self.timer.start(10000)

    def show_current_season(self):
        self.panel_classification, self.dic_xid_order = self.season.gen_panel_classification()
        self.panel_crosstabs = self.season.gen_panel_crosstabs()
        self.li_sorted_opponents = self.season.list_sorted_opponents()
        self.mix_panels()
        self.grid_classification.refresh()
        self.grid_matches.refresh()

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

    def pending_matches(self):
        lw = SwissWork.SwissWork(self.swiss)
        if lw.num_pending_matches() > 0:
            return True

        resp = False
        for xmatch in self.li_matches:
            if not xmatch.result:
                resp = True
                lw.add_match_zombie(xmatch)
        return resp

    def launch_worker(self):
        cores = Util.cpu_count()
        if cores < 2:
            resp = 1

        else:
            rondo = QTVarios.rondoPuntos()

            menu = QTVarios.LCMenu(self)
            menu.opcion(1, _("Launch one worker"), Iconos.Lanzamiento())
            menu.separador()

            submenu = menu.submenu(_("Launch some workers"), Iconos.Lanzamientos())

            for x in range(2, cores+1):
                submenu.opcion(x, str(x), rondo.otro())

            resp = menu.lanza()

        if resp:
            self.update_matches()
            lw = SwissWork.SwissWork(self.swiss)
            journey_work, season_work = lw.get_journey_season()
            current_journey = self.season.get_last_journey()
            if journey_work != current_journey or self.swiss.current_num_season != season_work:
                lw.put_swiss()
            if self.pending_matches():
                for x in range(resp):
                    XRun.run_lucas("-swiss", self.swiss.name())
                self.num_workers_launched = resp
            else:
                QTUtil2.message(self, _("There are no pending matches in the current matchday"))

    def export(self):
        menu = QTVarios.LCMenu(self)
        submenu = menu.submenu(_("Save all games to a database"), Iconos.DatabaseMas())
        QTVarios.menuDB(submenu, Code.configuration, True, indicador_previo="dbf_", remove_autosave=True, siNew=True)
        menu.separador()

        resp = menu.lanza()
        if resp is None:
            return

        if resp.startswith("dbf_"):
            self.export_to_database(resp)

    def export_to_database(self, dbf):
        if dbf.endswith(":n"):
            database = WDB_Games.new_database(self, Code.configuration)
            if database is None:
                return
        else:
            database = dbf[4:]

        filter_games = self.tab.current_position() == 3

        dic_raw_games = None

        if filter_games:
            total_games = len(self.li_matches)
        else:
            dic_raw_games = self.season.dic_raw_games()
            total_games = len(dic_raw_games)

        pb = QTUtil2.BarraProgreso(self, _("Generating the list of games to save"), "", total_games, 500)
        pb.mostrar()

        li_games = []
        if filter_games:
            for pos, dic in enumerate(self.li_matches, 1):
                pb.pon(pos)
                if pb.is_canceled():
                    return
                xmatch = Swiss.Match(dic["XID_WHITE"], dic["XID_BLACK"])
                xmatch.xid = dic["XID"]
                g = self.season.get_game_match(xmatch)
                li_games.append(g)
        else:
            for pos, (key, saved) in enumerate(dic_raw_games.items(), 1):
                if key in ("CURRENT_JOURNEY", "STOP_WORK_JOURNEY", "LI_MATCHSDAYS"):
                    continue
                pb.pon(pos)
                if pb.is_canceled():
                    return
                try:
                    g = Game.Game()
                    g.restore(saved)
                    li_games.append(g)
                except TypeError:
                    pass
        pb.close()

        pb = QTUtil2.BarraProgreso(self, _("Save all games to a database"), "", len(li_games), 500)
        pb.mostrar()
        db = DBgames.DBgames(database)
        nsaved = 0
        nerror = 0
        total = len(li_games)
        for pos, game in enumerate(li_games, 1):
            pb.pon(pos)
            if pb.is_canceled():
                break
            resp = db.insert(game)
            if resp.ok:
                nsaved += 1
            else:
                nerror += 1
        db.close()
        pb.close()
        if total > 0:
            if nerror:
                explanation = _("The database did not allow %d duplicate games to be recorded").replace(
                    "%d", str(nerror)
                )
            else:
                explanation = None
            QTUtil2.message(
                self,
                _("Saved") + " %d" % nsaved,
                explanation=explanation,
            )

    def mix_panels(self):
        for pos, un_elem in enumerate(self.panel_classification):
            for pos_otro, otro_elem in enumerate(self.panel_classification):
                for side in ("w", "b"):
                    key = "%s%d" % (side, pos_otro)
                    if pos == pos_otro:
                        valor = ""
                    else:
                        xid = un_elem["XID"]
                        other_xid = self.panel_classification[pos_otro]["XID"]
                        if side == "b":
                            xid, other_xid = other_xid, xid
                        result = self.panel_crosstabs[xid][other_xid]
                        if result is None:
                            valor = "-"
                        else:
                            if result == RESULT_DRAW:
                                valor = self.swiss.score_draw
                            elif result == RESULT_WIN_WHITE:
                                valor = self.swiss.score_win if side == "w" else self.swiss.score_lost
                            else:
                                valor = self.swiss.score_lost if side == "w" else self.swiss.score_win
                            cs = "%0.02f" % valor
                            while cs.endswith("0"):
                                cs = cs[:-1]
                            if cs.endswith("."):
                                cs = cs[:-1]
                            valor = cs
                    un_elem[key] = valor

    def seasons(self):
        li_seasons = self.swiss.list_seasons()
        if len(li_seasons) > 1:
            rondo = QTVarios.rondoPuntos()
            menu = QTVarios.LCMenu(self)
            submenu = menu.submenu(_("Change the active season"), Iconos.Season())
            for num_season in li_seasons:
                if self.season.num_season != num_season:
                    submenu.opcion(str(num_season), str(num_season + 1), rondo.otro())
                    submenu.separador()

            resp = menu.lanza()
            if resp is None:
                return

            num_season = int(resp)
            self.swiss.set_current_season(num_season)
            self.result = REINIT
            self.accept()


def play_swiss(parent, swiss):
    w = WSwiss(parent, swiss)
    if w.exec_():
        if w.result == PLAY_HUMAN:
            return w.play_human
        elif w.result == REINIT:
            return play_swiss(parent, swiss)
