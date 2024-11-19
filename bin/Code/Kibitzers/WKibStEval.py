from PySide2 import QtCore

import Code
from Code import Util
from Code.Engines import EngineRun
from Code.Kibitzers import WKibCommon
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil2


class WStEval(WKibCommon.WKibCommon):
    def __init__(self, cpu):
        WKibCommon.WKibCommon.__init__(self, cpu, Iconos.Book())

        self.em = Controles.EM(self, siHTML=False).read_only()
        f = Controles.FontType(name=Code.font_mono, puntos=10)
        self.em.set_font(f)

        li_acciones = (
            (_("Quit"), Iconos.Kibitzer_Close(), self.terminar),
            (_("Continue"), Iconos.Kibitzer_Play(), self.play),
            (_("Pause"), Iconos.Kibitzer_Pause(), self.pause),
            (_("Original position"), Iconos.HomeBlack(), self.home),
            (_("Takeback"), Iconos.Kibitzer_Back(), self.takeback),
            (_("Show/hide board"), Iconos.Kibitzer_Board(), self.config_board),
            ("%s: %s" % (_("Enable"), _("window on top")), Iconos.Pin(), self.windowTop),
            ("%s: %s" % (_("Disable"), _("window on top")), Iconos.Unpin(), self.windowBottom),
        )
        self.tb = Controles.TBrutina(self, li_acciones, with_text=False, icon_size=24)
        self.tb.set_action_visible(self.play, False)

        ly1 = Colocacion.H().control(self.board).control(self.em).margen(3)
        layout = Colocacion.V().control(self.tb).espacio(-10).otro(ly1).margen(3)
        self.setLayout(layout)

        self.engine = self.launch_engine()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.cpu.check_input)
        self.timer.start(200)

        self.restore_video(self.dicVideo)
        self.ponFlags()

    def stop(self):
        self.siPlay = False
        self.engine.ac_final(0)

    def whether_to_analyse(self):
        siW = self.game.last_position.is_white
        if not self.siPlay or (siW and (not self.is_white)) or ((not siW) and (not self.is_black)):
            return False
        return True

    def finalizar(self):
        self.save_video()
        if self.engine:
            self.engine.close()
            self.engine = None
            self.siPlay = False

    def launch_engine(self):
        self.nom_engine = self.kibitzer.name
        exe = self.kibitzer.path_exe
        if not Util.exist_file(exe):
            QTUtil2.message_error(self, "%s:\n  %s" % (_("Engine not found"), exe))
            import sys

            sys.exit()
        args = self.kibitzer.args
        li_uci = self.kibitzer.liUCI
        return EngineRun.RunEngine(self.nom_engine, exe, li_uci, 1, priority=self.cpu.prioridad, args=args)

    def orden_game(self, game):
        txt = ""
        self.game = game
        posicion = game.last_position

        is_white = posicion.is_white

        self.board.set_position(posicion)
        self.board.activate_side(is_white)
        if self.whether_to_analyse():
            self.engine.set_fen_position(posicion.fen())
            self.engine.put_line("eval")
            li, ok = self.engine.wait_list(":", 2000)
            while li and li[-1] == "\n":
                li = li[:-1]
            if ok:
                txt = "".join(li)

        self.em.set_text(txt)

        self.test_tb_home()