import sys
from PySide2 import QtWidgets

import Code
from Code import Util
from Code.Config import Configuration
from Code.Openings import OpeningsStd
from Code.QT import Piezas
from Code.Leagues import WLeagueWorker


def run(user, file_league_work):
    if not Code.DEBUG:
        sys.stderr = Util.Log("./bug.league")

    app = QtWidgets.QApplication([])

    configuration = Configuration.Configuration(user)
    configuration.lee()
    configuration.leeConfBoards()
    configuration.load_translation()
    OpeningsStd.ap.reset()
    Code.all_pieces = Piezas.AllPieces()

    app.setStyle(QtWidgets.QStyleFactory.create(configuration.x_style))
    QtWidgets.QApplication.setPalette(QtWidgets.QApplication.style().standardPalette())

    w = WLeagueWorker.WLeagueWorker(file_league_work)
    w.show()
    w.looking_for_work()
