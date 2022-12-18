import sys
from PySide2 import QtWidgets

import Code
from Code import Util
from Code.Config import Configuration
from Code.Openings import OpeningsStd
from Code.QT import Piezas
from Code.Tournaments import WTournamentRun
from Code.MainWindow import InitApp


def run(user, file_tournament, file_work):
    sys.stderr = Util.Log("./bug.tournaments")

    app = QtWidgets.QApplication([])

    configuration = Configuration.Configuration(user)
    configuration.lee()
    configuration.leeConfBoards()
    configuration.load_translation()
    OpeningsStd.ap.reset()
    Code.all_pieces = Piezas.AllPieces()

    InitApp.init_app_style(app, configuration)

    w = WTournamentRun.WTournamentRun(file_tournament, file_work)
    w.show()
    w.looking_for_work()

    # app.exec_()
