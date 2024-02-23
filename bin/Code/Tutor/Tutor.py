import FasterCode

import Code
from Code.Analysis import Analysis
from Code.Base import Game
from Code.Base.Constantes import INACCURACY, MISTAKE, BLUNDER, TOP_RIGHT
from Code.QT import QTUtil2
from Code.Tutor import WindowTutor


class Tutor:
    def __init__(self, manager, move, from_sq, to_sq, siEntrenando):
        self.manager = manager

        self.game = manager.game

        self.main_window = manager.main_window
        self.managerTutor = manager.xtutor
        self.last_position = self.game.last_position
        self.move = move
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.mrm_tutor = manager.mrm_tutor
        self.rm_rival = manager.rm_rival
        self.is_white = manager.is_human_side_white
        self.siEntrenando = siEntrenando
        self.list_rm = None  # necesario

        self.is_moving_time = False

    def elegir(self, has_hints, li_ap_posibles=None):

        self.rmUsuario, posUsuario = self.mrm_tutor.buscaRM(self.move.movimiento())
        if self.rmUsuario is None:
            # Elegimos si la opcion del tutor es mejor que la del usuario
            # Ponemos un mensaje mientras piensa
            me = QTUtil2.waiting_message.start(self.main_window, _("Analyzing the move...."), physical_pos=TOP_RIGHT)

            fen = self.move.position.fen()
            mrm_usuario = self.managerTutor.analiza(fen)
            if len(mrm_usuario.li_rm) == 0:
                self.rmUsuario = self.mrm_tutor.li_rm[0].copia()
                self.rmUsuario.from_sq = self.move.from_sq
                self.rmUsuario.to_sq = self.move.to_sq
                self.rmUsuario.promotion = self.move.promotion
                self.rmUsuario.mate = 0
                self.rmUsuario.puntos = 0
            else:
                self.rmUsuario = mrm_usuario.li_rm[0]
                self.rmUsuario.change_side(self.move.position)

            me.final()

        # Comparamos la puntuacion del usuario con la del tutor
        if not launch_tutor(self.mrm_tutor, self.rmUsuario):
            return False

        # Creamos la lista de movimientos analizados por el tutor
        self.list_rm = self.do_lirm(posUsuario)  # rm,name

        # Creamos la ventana
        si_rival = self.rm_rival and " " in self.rm_rival.getPV()

        self.li_ap_posibles = li_ap_posibles
        in_the_opening = li_ap_posibles and len(li_ap_posibles) > 1
        if in_the_opening:
            si_rival = False

        self.w = w = WindowTutor.WindowTutor(self.manager, self, si_rival, in_the_opening, self.is_white, has_hints)

        self.cambiadoRM(0)

        self.gameUsuario = Game.Game(self.move.position)
        self.gameUsuario.add_move(self.move)
        self.gameUsuario.read_pv(self.rmUsuario.getPV())
        self.posUsuario = 0
        self.max_user = len(self.gameUsuario.li_moves)
        self.boardUsuario.set_position(self.move.position)

        message = _("Your move") + "<br><br>" + \
                  self.gameUsuario.li_moves[0].pgn_html_base(Code.configuration.x_pgn_withfigurines) + \
                  " " + self.rmUsuario.texto()

        w.ponPuntuacionUsuario(message)

        if si_rival:
            self.rm_rival.change_side()
            pvBloque = self.rm_rival.getPV()
            n = pvBloque.find(" ")
            if n > 0:
                pvBloque = pvBloque[n + 1:].strip()
            else:
                pvBloque = ""

            if pvBloque:
                self.gameRival = Game.Game(self.last_position)
                self.gameRival.read_pv(pvBloque)
                self.posRival = 0
                self.maxRival = len(self.gameRival.li_moves) - 1
                if self.maxRival >= 0:
                    self.boardRival.set_position(self.gameRival.li_moves[0].position)
                    self.rival_has_moved(True)
                    message = _("Opponent's prediction") + "<br><br>" + \
                              self.gameRival.li_moves[0].pgn_html_base(Code.configuration.x_pgn_withfigurines) + \
                              " " + self.rm_rival.texto_rival()
                    w.ponPuntuacionRival(message)

        self.moving_tutor(True)
        self.moving_user(True)

        if w.exec_():
            if w.siElegidaOpening:
                from_sq = self.gameOpenings.move(0).from_sq
                to_sq = self.gameOpenings.move(0).to_sq
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

    def ponVariations(self, move, movenum):
        if self.list_rm:
            rm, name = self.list_rm[0]
            game = Game.Game(self.move.position_before)
            game.read_pv(rm.getPV())

            jgvar = game.move(0)
            jgvar.set_comment(rm.texto())

            move.add_variation(game)

            game_usuario = Game.Game(self.move.position_before)
            game_usuario.read_pv(self.rmUsuario.getPV())
            txt = game_usuario.pgn_translated()
            puntos = self.rmUsuario.texto()
            vusu = "%s : %s" % (puntos, txt)
            move.set_comment(vusu.replace("\n", ""))

    def do_lirm(self, posUsuario):
        li = []
        pb = self.move.position_before

        for n, rm in enumerate(self.mrm_tutor.li_rm):
            if n != posUsuario:
                pv1 = rm.getPV().split(" ")[0]
                from_sq = pv1[:2]
                to_sq = pv1[2:4]
                promotion = pv1[4] if len(pv1) == 5 else ""
                name = pb.pgn_translated(from_sq, to_sq, promotion)
                name += " " + rm.abrTexto()

                li.append((rm, name))
        return li

    def cambiadoRM(self, pos):
        self.pos_rm = pos
        rm = self.list_rm[pos][0]
        self.game_tutor = Game.Game(self.last_position)
        self.game_tutor.read_pv(rm.getPV())

        message = _("Tutor's suggestion") + "<br><br>" + \
                  self.game_tutor.li_moves[0].pgn_html_base(Code.configuration.x_pgn_withfigurines) + \
                  " " + rm.texto()

        self.w.ponPuntuacionTutor(message)

        self.pos_tutor = 0
        self.max_tutor = len(self.game_tutor)
        self.moving_tutor(True)

    def mueve(self, quien, que):
        if quien not in ("user", "tutor"):
            return

        funcion = eval("self.moving_" + quien)

        if que == "Adelante":
            funcion(n_saltar=1)
        elif que == "Atras":
            funcion(n_saltar=-1)
        elif que == "Inicio":
            funcion(is_base=True)
        elif que == "Final":
            funcion(siFinal=True)
        elif que == "Libre":
            self.analiza(quien)
        elif que == "Tiempo":
            tb = eval("self.w.tb" + quien)
            posMax = eval("self.max_" + quien)
            self.move_timed(funcion, tb, posMax)

    def move_timed(self, funcion, tb, posMax):
        if self.is_moving_time:
            self.is_moving_time = False
            self.time_others_tb(True)
            self.w.stop_clock()
            return

        def otrosTB(siHabilitar):
            for accion in tb.li_acciones:
                if not accion.key.endswith("MoverTiempo"):
                    accion.setEnabled(siHabilitar)

        self.time_function = funcion
        self.time_pos_max = posMax
        self.time_pos = -1
        self.time_others_tb = otrosTB
        self.is_moving_time = True
        otrosTB(False)
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

    def moving_user(self, si_inicio=False, n_saltar=0, siFinal=False, is_base=False):
        if n_saltar:
            pos = self.posUsuario + n_saltar
            if 0 <= pos < self.max_user:
                self.posUsuario = pos
            else:
                return
        elif si_inicio:
            self.posUsuario = 0
        elif is_base:
            self.posUsuario = -1
        else:
            self.posUsuario = self.max_user - 1

        move = self.gameUsuario.move(self.posUsuario if self.posUsuario > -1 else 0)
        if is_base:
            self.boardUsuario.set_position(move.position_before)
        else:
            self.boardUsuario.set_position(move.position)
            self.boardUsuario.put_arrow_sc(move.from_sq, move.to_sq)

    def moving_tutor(self, si_inicio=False, n_saltar=0, siFinal=False, is_base=False):
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
        else:
            self.pos_tutor = self.max_tutor - 1

        move = self.game_tutor.move(self.pos_tutor if self.pos_tutor > -1 else 0)
        if move:
            if is_base:
                self.boardTutor.set_position(move.position_before)
            else:
                self.boardTutor.set_position(move.position)
                self.boardTutor.put_arrow_sc(move.from_sq, move.to_sq)

    def rival_has_moved(self, si_inicio=False, n_saltar=0, siFinal=False, is_base=False):
        if n_saltar:
            pos = self.posRival + n_saltar
            if 0 <= pos < self.maxRival:
                self.posRival = pos
            else:
                return
        elif si_inicio:
            self.posRival = 0
        elif is_base:
            self.posRival = -1
        else:
            self.posRival = self.maxRival - 1

        move = self.gameRival.move(self.posRival if self.posRival > -1 else 0)
        if is_base:
            self.boardRival.set_position(move.position_before)
        else:
            self.boardRival.set_position(move.position)
            self.boardRival.put_arrow_sc(move.from_sq, move.to_sq)

    def mueveOpening(self, si_inicio=False, n_saltar=0, siFinal=False, is_base=False):
        if n_saltar:
            pos = self.posOpening + n_saltar
            if 0 <= pos < self.maxOpening:
                self.posOpening = pos
            else:
                return
        elif si_inicio:
            self.posOpening = 0
        elif is_base:
            self.posOpening = -1
        else:
            self.posOpening = self.maxOpening - 1

        move = self.gameOpenings.move(self.posOpening if self.posOpening > -1 else 0)
        if is_base:
            self.boardOpenings.set_position(move.position_before)
        else:
            self.boardOpenings.set_position(move.position)
            self.boardOpenings.put_arrow_sc(move.from_sq, move.to_sq)

    def ponBoardsGUI(self, boardTutor, boardUsuario, boardRival, boardOpenings):
        self.boardTutor = boardTutor
        self.boardTutor.exePulsadoNum = self.exePulsadoNumTutor
        self.boardUsuario = boardUsuario
        self.boardUsuario.exePulsadoNum = self.exePulsadoNumUsuario
        self.boardRival = boardRival
        self.boardOpenings = boardOpenings

    def cambiarOpening(self, number):
        self.gameOpenings = Game.Game(self.last_position)
        self.gameOpenings.read_pv(self.li_ap_posibles[number].a1h8)
        self.maxOpening = len(self.gameOpenings)
        if self.maxOpening > 0:
            self.boardOpenings.set_position(self.gameOpenings.move(0).position)
        self.mueveOpening(si_inicio=True)

    def opcionesOpenings(self):
        return [(ap.tr_name, num) for num, ap in enumerate(self.li_ap_posibles)]

    def analiza(self, quien):
        if quien == "Tutor":
            rmTutor = self.list_rm[self.pos_rm][0]
            move = self.game_tutor.move(self.pos_tutor)
            pts = rmTutor.texto()
        else:
            move = self.gameUsuario.move(self.posUsuario)
            pts = self.rmUsuario.texto()

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
                self.boardTutor.remove_arrows()
                if self.boardTutor.flechaSC:
                    self.boardTutor.flechaSC.hide()
                li = FasterCode.get_captures(fen, siMB)
                for m in li:
                    d = m.xfrom()
                    h = m.xto()
                    self.boardTutor.show_arrow_mov(d, h, "c")
            else:
                self.boardTutor.remove_arrows()
                if self.boardTutor.flechaSC:
                    self.boardTutor.flechaSC.show()

    def exePulsadoNumUsuario(self, siActivar, number):
        if number in [1, 8]:
            if siActivar:
                # Que move esta en el board
                move = self.gameUsuario.move(self.posUsuario if self.posUsuario > -1 else 0)
                if self.posUsuario == -1:
                    fen = move.position_before.fen()
                else:
                    fen = move.position.fen()
                is_white = " w " in fen
                if is_white:
                    siMB = number == 1
                else:
                    siMB = number == 8
                self.boardUsuario.remove_arrows()
                if self.boardUsuario.flechaSC:
                    self.boardUsuario.flechaSC.hide()
                li = FasterCode.get_captures(fen, siMB)
                for m in li:
                    d = m.xfrom()
                    h = m.xto()
                    self.boardUsuario.show_arrow_mov(d, h, "c")
            else:
                self.boardUsuario.remove_arrows()
                if self.boardUsuario.flechaSC:
                    self.boardUsuario.flechaSC.show()


def launch_tutor(mrm_tutor, rm_usuario, tp=None):
    if tp is None:
        tp = Code.configuration.x_tutor_diftype
    rm_tutor = mrm_tutor.mejorMov()
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
        rm, n = mrm_tutor.buscaRM(a1h8_user)
        if rm is None:
            return True
        if n == 0:
            return False
        return launch_tutor(mrm_tutor, rm)
    return False
