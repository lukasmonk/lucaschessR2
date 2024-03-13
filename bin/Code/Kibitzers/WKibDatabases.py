from PySide2 import QtCore, QtWidgets

from Code.Databases import WDB_Games, DBgames
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil


class InfoMoveReplace:

    def modoPartida(self, x, y):
        return True


class WKibDatabases(QtWidgets.QDialog):
    def __init__(self, cpu):
        QtWidgets.QDialog.__init__(self)

        self.cpu = cpu
        self.kibitzer = cpu.kibitzer
        self.db = DBgames.DBgames(self.kibitzer.path_exe)

        dic_video = self.cpu.dic_video
        if not dic_video:
            dic_video = {'_SIZE_': '886,581'}

        self.siTop = dic_video.get("SITOP", True)

        self.is_temporary = False
        self.wgames = WDB_Games.WGames(self, self.db, None, False)
        self.wgames.infoMove = InfoMoveReplace()

        self.wgames.tbWork.hide()
        self.wgames.status.hide()

        self.status = QtWidgets.QStatusBar(self)
        self.status.setFixedHeight(22)

        self.setWindowTitle(cpu.titulo)
        self.setWindowIcon(Iconos.Database())

        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )

        li_acciones = (
            (_("Quit"), Iconos.Kibitzer_Close(), self.terminar),
            (_("Continue"), Iconos.Kibitzer_Play(), self.play),
            (_("Pause"), Iconos.Kibitzer_Pause(), self.pause),
            ("%s: %s" % (_("Enable"), _("window on top")), Iconos.Kibitzer_Up(), self.windowTop),
            ("%s: %s" % (_("Disable"), _("window on top")), Iconos.Kibitzer_Down(), self.windowBottom),
        )
        self.tb = Controles.TBrutina(self, li_acciones, with_text=False, icon_size=24)
        self.tb.set_action_visible(self.play, False)

        ly1 = Colocacion.H().control(self.tb).relleno().margen(0)
        ly2 = Colocacion.V().otro(ly1).control(self.wgames).control(self.status)

        self.setLayout(ly2)

        self.siPlay = True

        self.restore_video(dic_video)
        self.ponFlags()

        self.db.filter_pv("")
        self.wgames.grid.refresh()
        self.wgames.grid.gotop()
        self.pv = ""
        self.previous_stable = False
        self.show_num_games()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_input)
        self.timer.start(200)

    def check_input(self):
        self.show_num_games()
        self.cpu.check_input()

    def tw_terminar(self):
        pass

    def ponFlags(self):
        flags = self.windowFlags()
        if self.siTop:
            flags |= QtCore.Qt.WindowStaysOnTopHint
        else:
            flags &= ~QtCore.Qt.WindowStaysOnTopHint
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.tb.set_action_visible(self.windowTop, not self.siTop)
        self.tb.set_action_visible(self.windowBottom, self.siTop)
        self.show()

    def windowTop(self):
        self.siTop = True
        self.ponFlags()

    def windowBottom(self):
        self.siTop = False
        self.ponFlags()

    def terminar(self):
        self.finalizar()
        self.accept()

    def pause(self):
        self.siPlay = False
        self.tb.set_pos_visible(0, True)
        self.tb.set_pos_visible(1, False)
        self.stop()

    def play(self):
        self.siPlay = True
        self.tb.set_pos_visible(0, False)
        self.tb.set_pos_visible(1, True)
        self.reset()

    def stop(self):
        pass

    def closeEvent(self, event):
        self.finalizar()

    def finalizar(self):
        self.save_video()
        if self.db:
            self.db.close()
            self.db = None
            self.siPlay = False

    def save_video(self):
        dic = {}

        pos = self.pos()
        dic["_POSICION_"] = "%d,%d" % (pos.x(), pos.y())

        tam = self.size()
        dic["_SIZE_"] = "%d,%d" % (tam.width(), tam.height())

        dic["SITOP"] = self.siTop

        self.cpu.save_video(dic)

    def restore_video(self, dic_video):
        if dic_video:
            w_e, h_e = QTUtil.desktop_size()
            x, y = dic_video.get("_POSICION_", "0,0").split(",")
            x = int(x)
            y = int(y)
            if not (0 <= x <= (w_e - 50)):
                x = 0
            if not (0 <= y <= (h_e - 50)):
                y = 0
            self.move(x, y)
            if not ("_SIZE_" in dic_video):
                w, h = self.width(), self.height()
                for k in dic_video:
                    if k.startswith("_TAMA"):
                        w, h = dic_video[k].split(",")
            else:
                w, h = dic_video["_SIZE_"].split(",")
            w = int(w)
            h = int(h)
            if w > w_e:
                w = w_e
            elif w < 20:
                w = 20
            if h > h_e:
                h = h_e
            elif h < 20:
                h = 20
            self.resize(w, h)

    def orden_game(self, game):
        self.pv = game.pv()
        self.db.filter_pv(self.pv)
        self.wgames.grid.refresh()
        self.wgames.grid.gotop()
        self.siPlay = True
        self.show_num_games()
        self.previous_stable = False

    def show_num_games(self):
        if not self.previous_stable:
            reccount, stable = self.db.reccount_stable()
            message = _("Games") + f": {reccount}"
            self.previous_stable = stable
            if stable:
                li_moves = self.db.get_summary(self.pv, {}, False)
                if li_moves and reccount:
                    dicmove = li_moves[-1]
                    # win y lost es al revés
                    message += (f'  ||   {_("Win")}: {dicmove["lost"]}  '
                                f'{_("Lost")}: {dicmove["win"]}  '
                                f'{_("Draw")}: {dicmove["draw"]}')
            self.status.showMessage(message, 0)

    def reset(self):
        self.orden_game(self.game)
