import Code
from Code import Util
from Code.QT import QTUtil2
from Code.SQL import UtilSQL


class Adjournments:
    def __init__(self):
        self.file = Code.configuration.file_adjournments()

    def open(self):
        return UtilSQL.DictSQL(self.file)

    def add(self, tp: int, dic: dict, label_menu: str):
        with self.open() as db:
            now = Util.today()
            key = "%d|%d|%d|%d|%d|%d|%d|%s" % (now.year, now.month, now.day, now.hour, now.minute, now.second, tp, label_menu)
            db[key] = dic

    def get(self, key):
        with self.open() as db:
            return db[key]

    def remove(self, key):
        with self.open() as db:
            del db[key]
            num_elem = len(db)
        if num_elem == 0:
            Util.remove_file(self.file)

    def list_menu(self):
        with self.open() as db:
            li = db.keys(True)
            li_resp = []
            for key in li:
                year, month, day, hour, minute, second, tp, label_menu = key.split("|")
                label = "%d-%02d-%02d %02d:%02d:%02d " % (int(year), int(month), int(day), int(hour), int(minute), int(second))
                tp = int(tp)
                li_resp.append((key, label + label_menu, tp))
            return li_resp

    def __len__(self):
        if Util.exist_file(self.file):
            with self.open() as db:
                return len(db)
        else:
            return 0

    @staticmethod
    def si_seguimos(manager):
        if QTUtil2.pregunta(manager.main_window, _("Do you want to exit Lucas Chess?")):
            manager.main_window.accept()
            return False
        else:
            manager.main_window.activaJuego(False, False)
            manager.quitaCapturas()
            manager.procesador.start()
            return True

    def __enter__(self):
        return self

    def __exit__(self, xtype, value, traceback):
        pass
