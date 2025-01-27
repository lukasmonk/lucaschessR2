import datetime
import json
import time

import requests

import Code
from Code.Base import Game
from Code.QT import Controles, LCDialog, Colocacion, QTVarios, Iconos, QTUtil2


class WebExternalImporter:
    def __init__(self, owner, db_games, title: str, url: str, icon):
        self.owner = owner
        self.title = title
        self.db_games = db_games
        self.url = url
        self.icon = icon

        self.username_import = None
        self.from_date = None
        self.to_date = None

        self.message_import = _("Games Loaded") + ": %d"
        self.message_import_initial = _("Reading") + "..."

    def params(self):
        w = WParams(self.owner, self.title, self.icon, self.url)
        if w.exec_():
            self.username_import = w.username_import
            self.from_date = w.from_date
            self.to_date = w.to_date
            return True

        return False

    def show_error(self, response):
        if response.status_code == 404:
            QTUtil2.message_error(self.owner, _("User does not exist"))
        else:
            QTUtil2.message_error(self.owner, f'{_("Error")}: {response.status_code}')
        return False


class Lichess(WebExternalImporter):
    def __init__(self, owner, db):
        super().__init__(owner, db, "Lichess", "https://lichess.org", Iconos.Lichess())

    def import_games(self):
        # Convertir fechas a Unix timestamp
        since = int(time.mktime(self.from_date.timetuple()) * 1000)
        until = int(time.mktime(self.to_date.timetuple()) * 1000)

        # Endpoint de la API de Lichess
        url = f"https://lichess.org/api/games/user/{self.username_import}"

        max_read = 50

        with QTUtil2.OneMomentPlease(self.owner, self.message_import_initial, with_cancel=True) as omp:
            num_imported = 0
            while True:
                params = {
                    "since": since,
                    "until": until,
                    "max": max_read,
                    "pgnInJson": True,  # Obtiene el PGN en formato JSON
                }
                if omp.is_canceled():
                    break
                response = requests.get(url, params=params, headers={"Accept": "application/x-ndjson"})
                if response.status_code == 200:
                    games_json = response.text.strip().split("\n")
                    num_imported_now = 0
                    for game_json in games_json:
                        if omp.is_canceled():
                            break
                        if not game_json.strip():
                            continue
                        dic_game = json.loads(game_json)
                        if "createdAt" not in dic_game:
                            continue
                        until = dic_game["createdAt"]
                        num_imported += 1
                        num_imported_now += 1
                        omp.label(self.message_import % num_imported)
                        pgn = dic_game["pgn"]
                        ok, game = Game.pgn_game(pgn)
                        if ok and not game.get_tag("FEN"):
                            self.db_games.insert(game)
                    if num_imported_now >= max_read:
                        until -= 1
                    else:
                        if num_imported == 0:
                            QTUtil2.message_error(self.owner, _("No game found"))
                            return False
                        return True
                else:
                    omp.close()
                    return self.show_error(response)
        return True


class ChessCom(WebExternalImporter):
    def __init__(self, owner, db):
        super().__init__(owner, db, "chess.com", "https://chess.com", Iconos.ChessCom())

    def import_games(self):
        headers = {
            'User-Agent': f'my-profile-tool/1.2 (username: {self.username_import}; contact: youremail@example.com)',
            'Accept-Encoding': 'gzip',
            'Accept': 'application/json, text/plain, */*'
        }

        # Obtener la lista de archivos de partidas
        url = f"https://api.chess.com/pub/player/{self.username_import}/games/archives"
        response = requests.get(url, headers=headers)
        with QTUtil2.OneMomentPlease(self.owner, self.message_import_initial, with_cancel=True) as omp:
            if response.status_code == 200:
                archives = response.json().get('archives', [])

                sum_from = f"{self.from_date.year}{self.from_date.month:02d}"
                sum_to = f"{self.to_date.year}{self.to_date.month:02d}"
                num_imported = 0
                for archive_url in archives:
                    if omp.is_canceled():
                        break
                    li = archive_url.split("/")
                    cyear = li[-2]
                    cmonth = li[-1]
                    sum_date = cyear + cmonth
                    if sum_from <= sum_date <= sum_to:
                        pgn_response = requests.get(f"{archive_url}/pgn", headers=headers)
                        if pgn_response.status_code == 200:
                            path_temp = Code.configuration.temporary_file("pgn")
                            with open(path_temp, "wt", encoding="utf-8") as q:
                                q.write(pgn_response.text)
                            for ok, game in Game.read_games(path_temp):
                                if omp.is_canceled():
                                    break
                                if ok:
                                    if not game.get_tag("FEN"):
                                        cdate = game.get_tag("Date")
                                        if cdate:
                                            cyear, cmonth, cday = cdate.split(".")
                                            date = datetime.date(year=int(cyear), month=int(cmonth), day=int(cday))
                                            if self.from_date <= date <= self.to_date:
                                                self.db_games.insert(game)
                                                num_imported += 1

                                omp.label(self.message_import % num_imported)
            else:
                omp.close()
                response.status_code = 404
                self.show_error(response)
                return False

        if num_imported == 0:
            QTUtil2.message_error(self.owner, _("No game found"))
            return False
        return True


class WParams(LCDialog.LCDialog):
    def __init__(self, owner, title, icon, url):
        self.key = "wparams_importexternal"
        super().__init__(owner, title, icon, self.key)

        self.username_import = None
        self.from_date = None
        self.to_date = None

        tb = QTVarios.tb_accept_cancel(self)

        lb_user = Controles.LB(self, _("User") + ":")
        self.ed_user = Controles.ED(self, "")

        lb_from = Controles.LB(self, _("From") + ":")
        date = datetime.date(year=2000, month=1, day=1)
        self.dt_from = Controles.GetDate(self, date)

        lb_to = Controles.LB(self, _("To") + ":")
        date = datetime.date.today()
        self.dt_to = Controles.GetDate(self, date)

        lb_url = Controles.LB(self, f'<a href="{url}">{url}</a>')

        layout = Colocacion.G()
        layout.filaVacia(0, 20)
        layout.controld(lb_user, 1, 0).control(self.ed_user, 1, 1)
        layout.filaVacia(2, 20)
        layout.controld(lb_from, 3, 0).control(self.dt_from, 3, 1)
        layout.filaVacia(4, 20)
        layout.controld(lb_to, 5, 0).control(self.dt_to, 5, 1)
        layout.filaVacia(6, 20)
        layout.control(lb_url, 7, 0)

        layout_gen = Colocacion.V()
        layout_gen.control(tb)
        layout_gen.otro(layout)
        layout_gen.relleno()

        self.setLayout(layout_gen)

        self.restore_video()

        self.restore_data()
        self.ed_user.setFocus()

    def restore_data(self):
        dic = Code.configuration.read_variables(self.key)
        self.ed_user.set_text(dic.get("user", ""))
        if "from_date" in dic:
            self.dt_from.set_date(dic["from_date"])
        if "to_date" in dic:
            self.dt_to.set_date(dic["to_date"])

    def save_data(self):
        dic = Code.configuration.read_variables(self.key)
        dic["user"] = self.username_import
        dic["from_date"] = self.from_date
        dic["to_date"] = self.to_date
        Code.configuration.write_variables(self.key, dic)

    def aceptar(self):
        self.username_import = self.ed_user.text().strip()
        self.from_date = self.dt_from.pydate()
        self.to_date = self.dt_to.pydate()
        if self.from_date > self.to_date:
            self.from_date, self.to_date = self.to_date, self.from_date
        self.save_video()
        if self.username_import:
            self.save_data()
            self.accept()

    def cancelar(self):
        self.reject()
