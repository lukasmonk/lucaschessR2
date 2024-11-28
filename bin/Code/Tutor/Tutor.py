import FasterCode

import Code
from Code.Analysis import Analysis
from Code.Base import Game
from Code.Base.Constantes import INACCURACY, MISTAKE, BLUNDER, TOP_RIGHT
from Code.QT import QTUtil2
from Code.Tutor import WindowTutor


class Tutor:
    def __init__(self, manager, move, from_sq, to_sq, is_training):
        self.manager = manager

        self.game = manager.game

        self.main_window = manager.main_window
        self.xtutor = manager.xtutor
        self.last_position = self.game.last_position
        self.move = move
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.promotion = ""
        self.mrm_tutor = manager.mrm_tutor
        self.is_white = manager.is_human_side_white
        self.is_training = is_training
        self.list_rm = None  # necesario

        self.w = None

        self.is_moving_time = False

        self.tb_opening = None

        self.rm_user = None
        self.game_user = None
        self.pos_user = 0
        self.max_user = 0
        self.board_user = None

        self.rm_rival = manager.rm_rival
        self.game_rival = None
        self.pos_rival = 0
        self.max_rival = 0
        self.board_rival = None

        self.game_tutor = None
        self.pos_tutor = 0
        self.max_tutor = 0
        self.board_tutor = None

        self.game_opening = None
        self.pos_opening = 0
        self.max_opening = 0
        self.board_openings = None

        self.li_ap_posibles = None

        self.time_function = None
        self.time_pos_max = 0
        self.time_pos = -1
        self.time_others_tb = None

    def elegir(self, has_hints, li_ap_posibles=None):

        self.rm_user, pos_user = self.mrm_tutor.search_rm(self.move.movimiento())
        if self.rm_user is None:
            # Elegimos si la opcion del tutor es mejor que la del usuario
            # Ponemos un mensaje mientras piensa
            me = QTUtil2.waiting_message.start(self.main_window, _("Analyzing the move...."), physical_pos=TOP_RIGHT)

            fen = self.move.position.fen()
            mrm_usuario = self.xtutor.analiza(fen)
            if len(mrm_usuario.li_rm) == 0:
                self.rm_user = self.mrm_tutor.li_rm[0].copia()
                self.rm_user.from_sq = self.move.from_sq
                self.rm_user.to_sq = self.move.to_sq
                self.rm_user.promotion = self.move.promotion
                self.rm_user.mate = 0
                self.rm_user.puntos = 0
            else:
                self.rm_user = mrm_usuario.li_rm[0]
                self.rm_user.change_side(self.move.position)

            me.final()

        # Comparamos la puntuacion del usuario con la del tutor
        if not launch_tutor(self.mrm_tutor, self.rm_user):
            return False

        # Creamos la lista de movimientos analizados por el tutor
        self.list_rm = self.do_lirm(pos_user)  # rm,name

        # Creamos la ventana
        si_rival = self.rm_rival and " " in self.rm_rival.get_pv()

        self.li_ap_posibles = li_ap_posibles
        in_the_opening = li_ap_posibles and len(li_ap_posibles) > 1
        if in_the_opening:
            si_rival = False

        self.w = w = WindowTutor.WindowTutor(self.manager, self, si_rival, in_the_opening, self.is_white, has_hints)

        self.changed_rm(0)

        self.game_user = Game.Game(self.move.position)
        self.game_user.add_move(self.move)
        self.game_user.read_pv(self.rm_user.get_pv())
        self.pos_user = 0
        self.max_user = len(self.game_user.li_moves)
        self.board_user.set_position(self.move.position)

        message = _("Your move") + "<br><br>" + \
                  self.game_user.li_moves[0].pgn_html_base(Code.configuration.x_pgn_withfigurines) + \
                  " " + self.rm_user.texto()

        w.set_score_user(message)

        if si_rival:
            self.rm_rival.change_side()
            pv_bloque = self.rm_rival.get_pv()
            n = pv_bloque.find(" ")
            if n > 0:
                pv_bloque = pv_bloque[n + 1:].strip()
            else:
                pv_bloque = ""

            self.w.tbrival.setVisible(pv_bloque.count(" ") > 0)

            if pv_bloque:
                self.game_rival = Game.Game(self.last_position)
                self.game_rival.read_pv(pv_bloque)
                self.pos_rival = 0
                self.max_rival = len(self.game_rival.li_moves) - 1
                if self.max_rival >= 0:
                    self.board_rival.set_position(self.game_rival.li_moves[0].position)
                    self.rival_has_moved(True)
                    message = _("Opponent's prediction") + "<br><br>" + \
                              self.game_rival.li_moves[0].pgn_html_base(Code.configuration.x_pgn_withfigurines) + \
                              " " + self.rm_rival.texto_rival()
                    w.set_score_rival(message)

        self.moving_tutor(True)
        self.moving_user(True)

        if w.exec_():
            if w.siElegidaOpening:
                from_sq = self.game_opening.move(0).from_sq
                to_sq = self.game_opening.move(0).to_sq
                if from_sq == self.from_sq and to_sq == self.to_sq:
                    return False
                self.from_sq = from_sq
                self.to_sq = to_sq
                self.promotion = ""
            elif w.respLibro:
                self.from_sq, self.to_sq, self.promotion = w.respLibro
            else:
                rm = self.list_rm[self.pos_rm][0]
                self.from_sq = rm.from_sq
                self.to_sq = rm.to_sq
                self.promotion = rm.promotion
            return True
        return False

    def add_variations_to_move(self, move, movenum):
        if self.list_rm:
            rm, name = self.list_rm[0]
            game = Game.Game(self.move.position_before)
            game.read_pv(rm.get_pv())

            jgvar = game.move(0)
            jgvar.set_comment(rm.texto())

            move.add_variation(game)

            game_usuario = Game.Game(self.move.position_before)
            game_usuario.read_pv(self.rm_user.get_pv())

            jgvar = game_usuario.move(0)
            jgvar.set_comment(self.rm_user.texto())

            move.add_variation(game_usuario)

    def do_lirm(self, pos_user):
        li = []
        pb = self.move.position_before

        for n, rm in enumerate(self.mrm_tutor.li_rm):
            if n != pos_user:
                pv1 = rm.get_pv().split(" ")[0]
                from_sq = pv1[:2]
                to_sq = pv1[2:4]
                promotion = pv1[4] if len(pv1) == 5 else ""
                name = pb.pgn_translated(from_sq, to_sq, promotion)
                name += " " + rm.abbrev_text()

                li.append((rm, name))
        return li

    def changed_rm(self, pos):
        self.pos_rm = pos
        rm = self.list_rm[pos][0]
        self.game_tutor = Game.Game(self.last_position)
        self.game_tutor.read_pv(rm.get_pv())

        message = _("Tutor's suggestion") + "<br><br>" + \
                  self.game_tutor.li_moves[0].pgn_html_base(Code.configuration.x_pgn_withfigurines) + \
                  " " + rm.texto()

        self.w.set_score_tutor(message)

        self.pos_tutor = 0
        self.max_tutor = len(self.game_tutor)
        self.moving_tutor(True)

    def mueve(self, quien, que):
        if quien not in ("user", "tutor", "opening", "rival"):
            return

        funcion = eval("self.moving_" + quien)

        if que == "Adelante":
            funcion(n_saltar=1)
        elif que == "Atras":
            funcion(n_saltar=-1)
        elif que == "Inicio":
            funcion(is_base=True)
        elif que == "Final":
            funcion(is_end=True)
        elif que == "Libre":
            self.analiza(quien)
        elif que == "Tiempo":
            tb = eval("self.w.tb" + quien)
            posMax = eval("self.max_" + quien)
            self.move_timed(funcion, tb, posMax)

    def move_timed(self, funcion, tb, pos_max):
        if self.is_moving_time:
            self.is_moving_time = False
            self.time_others_tb(True)
            self.w.stop_clock()
            return

        def other_tb(si_habilitar):
            for accion in tb.li_acciones:
                if not accion.key.endswith("MoverTiempo"):
                    accion.setEnabled(si_habilitar)

        self.time_function = funcion
        self.time_pos_max = pos_max
        self.time_pos = -1
        self.time_others_tb = other_tb
        self.is_moving_time = True
        other_tb(False)
        funcion(is_base=True)
        self.w.start_clock(self.moving_time_1)

    def moving_time_1(self):
        self.time_pos += 1
        if self.time_pos == self.time_pos_max:
            self.is_moving_time = False
            self.time_others_tb(True)
            self.w.stop_clock()
            return
        if self.time_pos == 0:
            self.time_function(si_inicio=True)
        else:
            self.time_function(n_saltar=1)

    def moving_user(self, si_inicio=False, n_saltar=0, is_end=False, is_base=False):
        if n_saltar:
            pos = self.pos_user + n_saltar
            if 0 <= pos < self.max_user:
                self.pos_user = pos
            else:
                return
        elif si_inicio:
            self.pos_user = 0
        elif is_base:
            self.pos_user = -1
        elif is_end:
            self.pos_user = self.max_user - 1
        else:
            return

        move = self.game_user.move(self.pos_user if self.pos_user > -1 else 0)
        if is_base:
            self.board_user.set_position(move.position_before)
        else:
            self.board_user.set_position(move.position)
            self.board_user.put_arrow_sc(move.from_sq, move.to_sq)

    def moving_tutor(self, si_inicio=False, n_saltar=0, is_end=False, is_base=False):
        if n_saltar:
            pos = self.pos_tutor + n_saltar
            if 0 <= pos < self.max_tutor:
                self.pos_tutor = pos
            else:
                return
        elif si_inicio:
            self.pos_tutor = 0
        elif is_base:
            self.pos_tutor = -1
        elif is_end:
            self.pos_tutor = self.max_tutor - 1
        else:
            return

        move = self.game_tutor.move(self.pos_tutor if self.pos_tutor > -1 else 0)
        if move:
            if is_base:
                self.board_tutor.set_position(move.position_before)
            else:
                self.board_tutor.set_position(move.position)
                self.board_tutor.put_arrow_sc(move.from_sq, move.to_sq)

    def moving_opening(self, si_inicio=False, n_saltar=0, is_end=False, is_base=False):
        if n_saltar:
            pos = self.pos_opening + n_saltar
            if 0 <= pos < self.max_opening:
                self.pos_opening = pos
            else:
                return
        elif si_inicio:
            self.pos_opening = 0
        elif is_base:
            self.pos_opening = -1
        elif is_end:
            self.pos_opening = self.max_opening - 1
        else:
            return

        move = self.game_opening.move(self.pos_opening if self.pos_opening > -1 else 0)
        if is_base:
            self.board_openings.set_position(move.position_before)
        else:
            self.board_openings.set_position(move.position)
            self.board_openings.put_arrow_sc(move.from_sq, move.to_sq)

    def moving_rival(self, si_inicio=False, n_saltar=0, is_end=False, is_base=False):
        if n_saltar:
            pos = self.pos_rival + n_saltar
            if 0 <= pos < self.max_rival:
                self.pos_rival = pos
            else:
                return
        elif si_inicio:
            self.pos_rival = 0
        elif is_base:
            self.pos_rival = -1
        else:
            self.pos_rival = self.max_rival - 1

        move = self.game_rival.move(self.pos_rival if self.pos_rival > -1 else 0)
        if is_base:
            self.board_rival.set_position(move.position_before)
        else:
            self.board_rival.set_position(move.position)
            self.board_rival.put_arrow_sc(move.from_sq, move.to_sq)

    def rival_has_moved(self, si_inicio=False, n_saltar=0, is_end=False, is_base=False):
        if n_saltar:
            pos = self.pos_rival + n_saltar
            if 0 <= pos < self.max_rival:
                self.pos_rival = pos
            else:
                return
        elif si_inicio:
            self.pos_rival = 0
        elif is_base:
            self.pos_rival = -1
        elif is_end:
            self.pos_rival = self.max_rival - 1
        else:
            return

        move = self.game_rival.move(self.pos_rival if self.pos_rival > -1 else 0)
        if is_base:
            self.board_rival.set_position(move.position_before)
        else:
            self.board_rival.set_position(move.position)
            self.board_rival.put_arrow_sc(move.from_sq, move.to_sq)

    def ponBoardsGUI(self, board_tutor, board_user, board_rival, board_openings):
        self.board_tutor = board_tutor
        self.board_tutor.do_pressed_number = self.exePulsadoNumTutor
        self.board_user = board_user
        self.board_user.do_pressed_number = self.exePulsadoNumUsuario
        self.board_rival = board_rival
        self.board_openings = board_openings

    def set_toolbaropening_gui(self, tb_opening):
        self.tb_opening = tb_opening

    def cambiarOpening(self, number):
        self.game_opening = Game.Game(self.last_position)
        self.game_opening.read_pv(self.li_ap_posibles[number].a1h8)
        self.max_opening = len(self.game_opening)
        if self.max_opening > 0:
            self.board_openings.set_position(self.game_opening.move(0).position)
        self.moving_opening(si_inicio=True)

        self.tb_opening.setVisible(self.max_opening >= 2)

    def opcionesOpenings(self):
        return [(ap.tr_name, num) for num, ap in enumerate(self.li_ap_posibles)]

    def analiza(self, quien):
        if quien == "Tutor":
            rmTutor = self.list_rm[self.pos_rm][0]
            move = self.game_tutor.move(self.pos_tutor)
            pts = rmTutor.texto()
        else:
            move = self.game_user.move(self.pos_user)
            pts = self.rm_user.texto()

        Analysis.AnalisisVariations(self.w, self.manager.xtutor, move, self.is_white, pts)

    def exePulsadoNumTutor(self, siActivar, number):
        if number in [1, 8]:
            if siActivar:
                # Que move esta en el board
                move = self.game_tutor.move(self.pos_tutor if self.pos_tutor > -1 else 0)
                if self.pos_tutor == -1:
                    fen = move.position_before.fen()
                else:
                    fen = move.position.fen()
                is_white = " w " in fen
                if is_white:
                    siMB = number == 1
                else:
                    siMB = number == 8
                self.board_tutor.remove_arrows()
                if self.board_tutor.arrow_sc:
                    self.board_tutor.arrow_sc.hide()
                li = FasterCode.get_captures(fen, siMB)
                for m in li:
                    d = m.xfrom()
                    h = m.xto()
                    self.board_tutor.show_arrow_mov(d, h, "c")
            else:
                self.board_tutor.remove_arrows()
                if self.board_tutor.arrow_sc:
                    self.board_tutor.arrow_sc.show()

    def exePulsadoNumUsuario(self, siActivar, number):
        if number in [1, 8]:
            if siActivar:
                # Que move esta en el board
                move = self.game_user.move(self.pos_user if self.pos_user > -1 else 0)
                if self.pos_user == -1:
                    fen = move.position_before.fen()
                else:
                    fen = move.position.fen()
                is_white = " w " in fen
                if is_white:
                    siMB = number == 1
                else:
                    siMB = number == 8
                self.board_user.remove_arrows()
                if self.board_user.arrow_sc:
                    self.board_user.arrow_sc.hide()
                li = FasterCode.get_captures(fen, siMB)
                for m in li:
                    d = m.xfrom()
                    h = m.xto()
                    self.board_user.show_arrow_mov(d, h, "c")
            else:
                self.board_user.remove_arrows()
                if self.board_user.arrow_sc:
                    self.board_user.arrow_sc.show()


def launch_tutor(mrm_tutor, rm_usuario, tp=None):
    if tp is None:
        tp = Code.configuration.x_tutor_diftype
    rm_tutor = mrm_tutor.best_rm_ordered()
    if tp == 0:  # ALWAYS
        return (rm_tutor.movimiento() != rm_usuario.movimiento()) and (
                rm_tutor.centipawns_abs() > rm_usuario.centipawns_abs()
        )
    else:
        ev = Code.analysis_eval.evaluate(rm_tutor, rm_usuario)
        if tp == INACCURACY:
            return ev in (INACCURACY, BLUNDER, MISTAKE)
        elif tp == MISTAKE:
            return ev in (BLUNDER, MISTAKE)
        else:
            return ev == BLUNDER


def launch_tutor_movimiento(mrm_tutor, a1h8_user):
    if mrm_tutor.li_rm:
        rm, n = mrm_tutor.search_rm(a1h8_user)
        if rm is None:
            return True
        if n == 0:
            return False
        return launch_tutor(mrm_tutor, rm)
    return False
