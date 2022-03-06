import sys
import time

from PySide2 import QtWidgets

from Code import Util
from Code.Base import Game
from Code.Base.Constantes import (
    KIB_GAVIOTA,
    KIBRUN_GAME,
    KIBRUN_STOP,
    KIBRUN_CLOSE,
    KIB_BEFORE_MOVE,
    KIB_BESTMOVE,
    KIB_BESTMOVE_ONELINE,
    KIB_CANDIDATES,
    KIB_INDEXES,
    KIB_POLYGLOT,
    KIB_STOCKFISH,
    KIB_THREATS,
    KIBRUN_CONFIGURATION,
)
from Code.Config import Configuration
from Code.Engines import Priorities
from Code.Kibitzers import Kibitzers
from Code.Kibitzers import WKibBooks
from Code.Kibitzers import WKibEngine
from Code.Kibitzers import WKibGaviota
from Code.Kibitzers import WKibIndex
from Code.Kibitzers import WKibLinea
from Code.Kibitzers import WKibStEval
from Code.Openings import OpeningsStd
from Code.QT import QTUtil
from Code.SQL import UtilSQL


class Orden:
    def __init__(self):
        self.key = ""
        self.titulo = ""
        self.dv = {}


class CPU:
    def __init__(self, fdb):

        self.ipc = UtilSQL.IPC(fdb, False)

        self.configuration = None
        self.titulo = None

        self.ventana = None
        self.engine = None

    def run(self):
        # Primero espera la orden de lucas
        while True:
            orden = self.recibe()
            if orden:
                break
            time.sleep(0.1)

        self.procesa(orden)

    def recibe(self):
        dv = self.ipc.pop()
        if not dv:
            return None

        orden = Orden()
        orden.key = dv["__CLAVE__"]
        orden.dv = dv
        return orden

    def procesa(self, orden):
        key = orden.key
        if key == KIBRUN_CONFIGURATION:
            user = orden.dv["USER"]
            self.configuration = Configuration.Configuration(user)
            self.configuration.lee()
            self.configuration.leeConfBoards()
            OpeningsStd.ap.reset()

            kibitzers = Kibitzers.Kibitzers()
            self.numkibitzer = kibitzers.number(orden.dv["HUELLA"])
            self.kibitzer = kibitzers.kibitzer(self.numkibitzer)
            prioridad = self.kibitzer.prioridad

            priorities = Priorities.priorities

            if prioridad != priorities.normal:
                self.prioridad = priorities.value(prioridad)
            else:
                self.prioridad = None

            self.titulo = self.kibitzer.name

            self.key_video = "Kibitzers%s" % self.kibitzer.huella
            self.dic_video = self.configuration.restore_video(self.key_video)

            self.tipo = self.kibitzer.tipo
            self.lanzaVentana()

        elif key == KIBRUN_GAME:
            game = Game.Game()
            game.restore(orden.dv["GAME"])
            if hasattr(self.ventana, "board"):
                self.ventana.board.set_side_bottom(orden.dv["IS_WHITE_BOTTOM"])
            if self.kibitzer.pointofview == KIB_BEFORE_MOVE:
                game.anulaSoloUltimoMovimiento()
            if self.tipo == KIB_THREATS:
                last_position = game.last_position
                last_position.is_white = not last_position.is_white
                game_thread = Game.Game(first_position=last_position)
                self.ventana.orden_game(game_thread)
            else:
                self.ventana.orden_game(game)

        elif key == KIBRUN_STOP:
            self.ventana.stop()

        elif key == KIBRUN_CLOSE:
            self.ipc.close()
            self.ventana.finalizar()
            self.ventana.reject()

    def save_video(self, dic):
        self.configuration.save_video(self.key_video, dic)

    def lanzaVentana(self):
        app = QtWidgets.QApplication([])

        app.setStyle(QtWidgets.QStyleFactory.create(self.configuration.x_style))
        QtWidgets.QApplication.setPalette(QtWidgets.QApplication.style().standardPalette())

        self.configuration.load_translation()

        if self.tipo == KIB_BESTMOVE:
            self.ventana = WKibEngine.WKibEngine(self)

        elif self.tipo == KIB_CANDIDATES:
            self.ventana = WKibEngine.WKibEngine(self)

        elif self.tipo == KIB_THREATS:
            self.ventana = WKibEngine.WKibEngine(self)

        elif self.tipo == KIB_BESTMOVE_ONELINE:
            self.ventana = WKibLinea.WKibLinea(self)

        elif self.tipo == KIB_POLYGLOT:
            self.ventana = WKibBooks.WPolyglot(self)

        elif self.tipo in KIB_INDEXES:
            self.ventana = WKibIndex.WKibIndex(self)

        elif self.tipo == KIB_STOCKFISH:
            self.ventana = WKibStEval.WStEval(self)

        elif self.tipo == KIB_GAVIOTA:
            self.ventana = WKibGaviota.WGaviota(self)

        self.ventana.show()

        # Code.gc = QTUtil.GarbageCollector()

        return app.exec_()

    def compruebaInput(self):
        if self.ventana:
            orden = self.recibe()
            if orden:
                self.procesa(orden)

    def dispatch(self, texto):
        if texto:
            self.ventana.set_text(texto)
        QTUtil.refresh_gui()

        return True


def run(fdb):
    sys.stderr = Util.Log("./bug.kibitzers")

    cpu = CPU(fdb)
    cpu.run()
