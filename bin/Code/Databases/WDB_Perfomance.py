import csv
import os
import webbrowser

from PySide2 import QtGui, QtCore, QtWidgets

import Code
from Code.QT import Colocacion, Controles
from Code.QT import Columnas
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil, QTUtil2
from Code.QT import QTVarios
from Code.QT import SelectFiles

li_fide = [-800, -677, -589, -538, -501, -470, -444, -422, -401, -383, -366, -351, -336, -322, -309, -296, -284, -273,
           -262, -251, -240, -230, -220, -211, -202, -193, -184, -175, -166, -158, -149, -141, -133, -125, -117, -110,
           -102, -95, -87, -80, -72, -65, -57, -50, -43, -36, -29, -21, -14, -7, 0, 7, 14, 21, 29, 36, 43, 50, 57, 65,
           72, 80, 87, 95, 102, 110, 117, 125, 133, 141, 149, 158, 166, 175, 184, 193, 202, 211, 220, 230, 240, 251,
           262, 273, 284, 296, 309, 322, 336, 351, 366, 383, 401, 422, 444, 470, 501, 538, 589, 677, 800]


class Perfomance:
    def __init__(self):
        self.dic_elo_player = {"W": [], "B": []}
        self.dic_elo_opponents = {"W": [], "B": []}
        self.dic_results = {"W": [], "B": []}

    def avg_elo_player(self):
        li_both = self.dic_elo_player["W"] + self.dic_elo_player["B"]
        return int(round(sum(li_both) / len(li_both))) if len(li_both) > 0 else 0

    def with_data(self):
        return len(self.dic_elo_opponents["W"]) + len(self.dic_elo_opponents["B"]) > 0

    def add_game(self, is_white: bool, elo: int, opponent_elo: int, result: float):
        color = "W" if is_white else "B"
        self.dic_elo_player[color].append(elo)
        self.dic_elo_opponents[color].append(opponent_elo)
        self.dic_results[color].append(result)

    def datos_base(self, is_white):
        if is_white is None:
            elo_opponents = self.dic_elo_opponents["W"] + self.dic_elo_opponents["B"]
            results = self.dic_results["W"] + self.dic_results["B"]
        else:
            color = "W" if is_white else "B"
            elo_opponents = self.dic_elo_opponents[color]
            results = self.dic_results[color]
        return elo_opponents, results

    def mathematical_method(self, is_white):
        elo_opponents, results = self.datos_base(is_white)
        num_games = len(elo_opponents)
        if num_games == 0:
            return ""
        sum_results = sum(results)
        if sum_results == 0:
            return max(round(sum(elo_opponents) / num_games - 800), 0)  # Límite inferior práctico
        if sum_results == num_games:
            return round(sum(elo_opponents) / num_games + 800)  # Límite superior práctico

        def expected_score(opponent_ratings, own_rating: float) -> float:
            """How many points we expect to score in a tourney with these opponents"""
            return sum(1 / (1 + 10 ** ((opponent_rating - own_rating) / 400)) for opponent_rating in opponent_ratings)

        score = sum(results)
        mid = 0

        lo, hi = 0, 4000

        while hi - lo > 0.00001:
            mid = (lo + hi) / 2

            if expected_score(elo_opponents, mid) < score:
                lo = mid
            else:
                hi = mid

        return round(mid)

    def fide_method(self, is_white):
        elo_opponents, results = self.datos_base(is_white)
        num_games = len(elo_opponents)
        if num_games == 0:
            return ""

        score = sum(results)
        porc = round(score * 100.0 / num_games)

        avg = sum(elo_opponents) / num_games

        return round(li_fide[porc] + avg)

    def linear_method(self, is_white):
        elo_opponents, results = self.datos_base(is_white)
        if len(elo_opponents) == 0:
            return ""

        num_games = len(elo_opponents)
        score = sum(results)
        porc = score * 100.0 / num_games

        avg = sum(elo_opponents) / num_games

        return round(avg + 8 * porc - 400)

    def according_method(self, tipo, is_white):
        if tipo == "FIDE":
            elo = self.fide_method(is_white)
        elif tipo == "MATH":
            elo = self.mathematical_method(is_white)
        else:
            elo = self.linear_method(is_white)
        return elo

    def str_according_method(self, tipo, is_white):
        elo = self.according_method(tipo, is_white)
        return "" if elo is None else str(elo)

    def int_according_method(self, tipo, is_white):
        elo = self.according_method(tipo, is_white)
        return 0 if elo is None or elo == "" else elo

    def str_score(self):
        wb = self.dic_results["W"] + self.dic_results["B"]
        if len(wb) == 0:
            return ""

        def xcalc(li_results):
            num = len(li_results)
            if num == 0:
                return "      "
            s = sum(li_results)
            return f"{s:.1f}/{num}"

        cw = xcalc(self.dic_results["W"])
        cb = xcalc(self.dic_results["B"])
        cwb = xcalc(wb)
        return f"{cwb} - {cw} - {cb}"

    def str_scorep(self):
        if len(self.dic_results["W"]) + len(self.dic_results["B"]) == 0:
            return ""

        def xcalc(li_results):
            num = len(li_results)
            if num == 0:
                return "      "
            s = sum(li_results) * 100.0 / num
            return f"{s:5.1f}"

        cw = xcalc(self.dic_results["W"])
        cb = xcalc(self.dic_results["B"])
        cwb = xcalc(self.dic_results["W"] + self.dic_results["B"])
        return f"{cwb} -{cw} -{cb}"

    def int_scorep(self):
        num = len(self.dic_results["W"]) + len(self.dic_results["B"])
        w = sum(self.dic_results["W"])
        b = sum(self.dic_results["B"])
        return (w + b) * 10000 / num + (w + b)

    def int_score(self):
        w = sum(self.dic_results["W"])
        b = sum(self.dic_results["B"])
        return (w + b) * 1000 - len(self.dic_results["W"]) - len(self.dic_results["B"])

    def str_results(self):
        def calc(li_results):
            w = d = ls = 0
            for result in li_results:
                if result == 1:
                    w += 1
                elif result == 0.5:
                    d += 1
                else:
                    ls += 1
            return f"{w}/{d}/{ls}"

        return (f'{calc(self.dic_results["W"] + self.dic_results["B"])} - '
                f'{calc(self.dic_results["W"])} - {calc(self.dic_results["B"])}')

    def int_results(self):
        w = d = ls = 0
        for result in (self.dic_results["W"] + self.dic_results["B"]):
            if result == 1:
                w += 1
            elif result == 0.5:
                d += 1
            else:
                ls += 1
        return w * 1000000 + d * 1000 + ls

    def str_opponents(self):
        w_op = len(self.dic_elo_opponents["W"])
        b_op = len(self.dic_elo_opponents["B"])
        if w_op + b_op == 0:
            return ""

        def xround(valor, elementos):
            if elementos == 0:
                return "     "
            x = valor / elementos
            ix = int(x)
            decimal = x - ix
            if decimal >= 0.5:
                ix += 1
            return f"{ix:4d}"

        w = xround(sum(self.dic_elo_opponents["W"]), w_op)
        b = xround(sum(self.dic_elo_opponents["B"]), b_op)
        wb = xround(sum(self.dic_elo_opponents["W"]) + sum(self.dic_elo_opponents["B"]), w_op + b_op)

        return f"{wb} - {w} - {b}"

    def int_opponents(self, is_white):
        w_op = len(self.dic_elo_opponents["W"])
        b_op = len(self.dic_elo_opponents["B"])
        if w_op + b_op == 0:
            return 0
        if is_white is None:
            wb = (sum(self.dic_elo_opponents["W"]) + sum(self.dic_elo_opponents["B"])) // (w_op + b_op)
        elif is_white:
            wb = sum(self.dic_elo_opponents["W"]) // w_op if w_op else 0
        else:
            wb = sum(self.dic_elo_opponents["B"]) // b_op if b_op else 0

        return wb


class WPerfomance(QtWidgets.QWidget):

    def __init__(self, wb_database, wb_games, db_games):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database
        self.wb_games = wb_games
        self.db_games = db_games

        self.dic_players = None

        self.li_players = []

        self.tipo = "FIDE"
        self.key_vars = "PERFOMANCE"
        self.configuration = Code.configuration
        dic = self.configuration.read_variables(self.key_vars)
        self.tipo = dic.get("TIPO", "FIDE")

        self.last_col = "player"
        self.last_reverse = False

        self.lb_tipo = Controles.LB(self).align_center().set_font_type(puntos=24, peso=500).set_background("lightgray")

        def ayuda():
            url = "https://lucaschess.blogspot.com/2025/05/performance-rating-of-list-of-games.html"
            webbrowser.open(url)

        self.tb = QTVarios.LCTB(self)
        self.tb.new(_("Close"), Iconos.MainMenu(), self.wb_database.tw_terminar)
        self.tb.new(_("Config"), Iconos.Configurar(), self.configurar)
        self.tb.new(_("Export"), Iconos.Export8(), self.export)
        self.tb.new(_("Help"), Iconos.AyudaGR(), ayuda)




        awb = f'{_("All")} - {_("White")} - {_("Black")}'
        perf = _("Perfomance")
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("__num__", _("N."), 50, align_center=True)
        o_columns.nueva("player", _("Player"), 190, align_center=True)
        o_columns.nueva("elo", _("Avg Elo"), 80, align_center=True)
        o_columns.nueva("WB", perf, 100, align_center=True)
        o_columns.nueva("W", perf + "\n" + _("White"), 90, align_center=True)
        o_columns.nueva("B", perf + "\n" + _("Black"), 90, align_center=True)
        o_columns.nueva("scorep", "%" + _("Score") + "\n" + awb, 150, align_center=True)
        o_columns.nueva("score", _("Score") + "\n" + awb, 170, align_center=True)
        o_columns.nueva("results", _("Results") + "\n" + _("Wins") + "/" + _("Draws") + "/" + _("Losses"), 190,
                        align_center=True)
        o_columns.nueva("opponent", _("Avg Opponent") + "\n" + awb, 150, align_center=True)

        font_metrics = QtGui.QFontMetrics(self.font())
        alto_cabecera = font_metrics.height() * 2 + 6

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, altoCabecera=alto_cabecera)

        ly = Colocacion.V().control(self.tb).control(self.lb_tipo).control(self.grid).margen(1)

        self.setLayout(ly)

        self.show_type()

    def actualiza(self):
        li_regs = self.wb_games.grid.recnosSeleccionados()
        if len(li_regs) == 1:
            li_regs = range(self.db_games.reccount())
        with QTUtil2.OneMomentPlease(self, with_cancel=True) as omp:
            dic_players = {}
            for recno in li_regs:
                if omp.is_canceled():
                    break
                white = self.db_games.field(recno, "WHITE")
                black = self.db_games.field(recno, "BLACK")
                if not white or not black:
                    continue
                try:
                    white_elo = int(self.db_games.field(recno, "WHITEELO"))
                except (TypeError, ValueError):
                    continue
                try:
                    black_elo = int(self.db_games.field(recno, "BLACKELO"))
                except (TypeError, ValueError):
                    continue

                if white_elo == 0 or black_elo == 0:
                    continue

                cresult = self.db_games.field(recno, "RESULT")
                if cresult == "1-0":
                    result_w, result_b = 1, 0
                elif cresult == "0-1":
                    result_w, result_b = 0, 1
                elif cresult == "1/2-1/2":
                    result_w, result_b = 0.5, 0.5
                else:
                    continue

                if white not in dic_players:
                    dic_players[white] = Perfomance()
                perfomance = dic_players[white]
                perfomance.add_game(True, white_elo, black_elo, result_w)
                if black not in dic_players:
                    dic_players[black] = Perfomance()
                perfomance = dic_players[black]
                perfomance.add_game(False, black_elo, white_elo, result_b)

            if omp.is_canceled():
                return

        if dic_players:
            self.dic_players = dic_players
            self.li_players = [player for player, perf in self.dic_players.items() if perf.with_data()]
            self.li_players.sort(key=lambda x: x.upper())
            self.grid.refresh()

        else:
            self.dic_players = None
            self.li_players = []
            self.grid.refresh()
            mens = _("The performance rating can not be calculated.")
            mens += "<br>" + _(
                "In order to make the calculations it is necessary that each game contains the fields: Result, WhiteElo and BlackElo.")
            QTUtil2.message_error(self, mens)

    def show_type(self):
        if self.tipo == "FIDE":
            label = _("Fide method")
        elif self.tipo == "MATH":
            label = _("Mathematical method")
        else:
            label = _("Linear method")
        self.lb_tipo.set_text(label)

    def configurar(self):
        menu = QTVarios.LCMenu(self)
        if self.tipo != "FIDE":
            menu.opcion(self.fide, _("Fide method"), Iconos.FideBuilding())
        if self.tipo != "MATH":
            menu.opcion(self.mathematical, _("Mathematical method"), Iconos.Math())
        if self.tipo != "LINEAR":
            menu.opcion(self.linear, _("Linear method"), Iconos.Linear())
        resp = menu.lanza()
        if resp:
            resp()

    def change_tipo(self, tipo):
        self.tipo = tipo
        self.show_type()
        self.grid.refresh()
        dic = self.configuration.read_variables(self.key_vars)
        dic["TIPO"] = self.tipo
        self.configuration.write_variables(self.key_vars, dic)

    def fide(self):
        self.change_tipo("FIDE")

    def mathematical(self):
        self.change_tipo("MATH")

    def linear(self):
        self.change_tipo("LINEAR")

    def grid_num_datos(self, grid):
        return len(self.li_players)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        player = self.li_players[row]
        if col == "player":
            return player
        if col == "__num__":
            return str(row + 1)

        perfomance: Perfomance = self.dic_players[self.li_players[row]]
        if col == "elo":
            return str(perfomance.avg_elo_player())
        if col == "WB":
            return perfomance.str_according_method(self.tipo, None)
        if col == "W":
            return perfomance.str_according_method(self.tipo, True)
        if col == "B":
            return perfomance.str_according_method(self.tipo, False)
        if col == "scorep":
            return perfomance.str_scorep()
        if col == "score":
            return perfomance.str_score()
        if col == "opponent":
            return perfomance.str_opponents()
        if col == "results":
            return perfomance.str_results()
        return None

    def grid_doubleclick_header(self, grid, o_column):
        col = o_column.key
        if col == "__num__":
            return

        def element(player):
            perfomance: Perfomance = self.dic_players[player]
            if col == "WB":
                return perfomance.int_according_method(self.tipo, None) * 10000 + perfomance.int_opponents(None)
            if col == "W":
                return perfomance.int_according_method(self.tipo, True) * 10000 + perfomance.int_opponents(True)
            if col == "B":
                return perfomance.int_according_method(self.tipo, False) * 10000 + perfomance.int_opponents(False)
            if col == "score":
                return perfomance.int_score()
            if col == "scorep":
                return perfomance.int_scorep()
            if col == "opponent":
                return perfomance.int_opponents(None)
            if col == "results":
                return perfomance.int_results()
            if col == "player":
                return player.upper()
            if col == "elo":
                return perfomance.avg_elo_player()

        reset = False

        if col == self.last_col:
            if o_column.head.endswith(" -"):
                reset = True
            self.last_reverse = not self.last_reverse

        else:
            self.last_reverse = False
            self.last_col = col

        for column in self.grid.o_columns.li_columns:
            if column.head.endswith((" +", " -")):
                column.head = column.head.replace(" +", "").replace(" -", "")

        if reset:
            col = "player"
            self.li_players.sort(key=element)
            self.last_reverse = False
            self.last_col = col
        else:
            o_column.head = o_column.head + (" -" if self.last_reverse else " +")
            self.li_players.sort(key=element, reverse=self.last_reverse)
        self.grid.refresh()

    def grid_right_button(self, grid, row, col, modif):
        key = col.key
        if key.startswith("__"):
            return
        val = self.grid_dato(grid, row, col)
        if val:
            val = str(val)
            QTUtil.set_clipboard(val)
            QTUtil2.temporary_message(self,
                val + "<br><br>" + _("It is saved in the clipboard to paste it wherever you want."), 2.0)

    def grid_tecla_control(self, grid, k, is_shift, is_control, is_alt):
        if k == QtCore.Qt.Key_R and is_alt:
            self.grid.resizeColumnsToContents()
        else:
            return True  # que siga con el resto de teclas

    def export(self):
        menu = QTVarios.LCMenu(self)

        menu.opcion("csv", _("To a CSV file"), Iconos.CSV())
        menu.separador()

        resp = menu.lanza()
        if resp:
            self.export_csv()

    def export_csv(self):
        dic_csv = self.configuration.read_variables("CSV")
        path_csv = SelectFiles.salvaFichero(self, _("Export") + " - " + _("To a CSV file"),
                                            dic_csv.get("FOLDER", self.configuration.carpeta), "csv")
        if not path_csv:
            return
        if not path_csv.lower().endswith(".csv"):
            path_csv = path_csv.strip() + ".csv"
        dic_csv["FOLDER"] = os.path.dirname(path_csv)
        self.configuration.write_variables("CSV", dic_csv)
        li_cols = []
        for col in self.grid.oColumnasR.li_columns:
            key = col.key
            if key.startswith("__"):
                continue
            li_cols.append(col)

        with open(path_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            li_data = []
            for col in li_cols:
                if col.key == "WB":
                    if self.tipo == "FIDE":
                        label = _("Fide method")
                    elif self.tipo == "MATH":
                        label = _("Mathematical method")
                    else:
                        label = _("Linear method")
                    li_data.append(label)
                else:
                    li_data.append(col.head.replace(" (+)", "").replace(" (-)", ""))
            writer.writerow(li_data)

            for recno in range(len(self.li_players)):
                li_data = []
                for col in li_cols:
                    li_data.append(self.grid_dato(self.grid, recno, col))
                writer.writerow(li_data)
        Code.startfile(path_csv)
