import sys

from PySide2 import QtWidgets

import Code
from Code import Util
from Code.Config import Configuration
from Code.Swiss import WSwissWorker
from Code.MainWindow import InitApp
from Code.Openings import OpeningsStd
from Code.QT import Piezas


def run(user, file_swiss_work):
    if not Code.DEBUG:
        sys.stderr = Util.Log("./bug.swiss")

    app = QtWidgets.QApplication([])

    configuration = Configuration.Configuration(user)
    configuration.start()
    configuration.load_translation()
    OpeningsStd.ap.reset()
    Code.all_pieces = Piezas.AllPieces()

    InitApp.init_app_style(app, configuration)

    w = WSwissWorker.WSwissWorker(file_swiss_work)
    w.show()
    w.looking_for_work()
