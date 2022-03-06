import sys
from PySide2 import QtWidgets

import Code
from Code import Util
from Code.Config import Configuration
from Code.Openings import OpeningsStd
from Code.QT import Piezas
from Code.Tournaments import WTournamentRun


def run(user, file_tournament, file_work):
    sys.stderr = Util.Log("./bug.tournaments")

    app = QtWidgets.QApplication([])

    configuration = Configuration.Configuration(user)
    configuration.lee()
    configuration.leeConfBoards()
    configuration.load_translation()
    OpeningsStd.ap.reset()
    Code.todasPiezas = Piezas.TodasPiezas()

    app.setStyle(QtWidgets.QStyleFactory.create(configuration.x_style))
    QtWidgets.QApplication.setPalette(QtWidgets.QApplication.style().standardPalette())

    w = WTournamentRun.WTournamentRun(file_tournament, file_work)
    w.show()
    w.busca_trabajo()

    # app.exec_()
