import FasterCode

from Code.Engines import EngineResponse
from Code.ForcingMoves import WForcingMoves
from Code.QT import QTUtil2


class ForcingMoves:
    def __init__(self, board, mrm: EngineResponse.MultiEngineResponse, owner):

        self.board = board
        fen = self.board.last_position.fen()
        self.fen = fen
        self.li_checks = []
        self.li_captures = []
        self.li_threats = []
        self.li_check_targets = []
        self.li_capture_targets = []
        mrm.ordena()
        self.st_best_moves = set()
        if len(mrm.li_rm) == 0:
            return
        self.rm = mrm.li_rm[0]
        if self.rm.mate < 0:  # We are being mated
            self.bm_is_getting_mated = True
        else:
            self.bm_is_getting_mated = False
        self.st_best_moves.add(self.rm.from_sq + self.rm.to_sq + self.rm.promotion)
        for rm in mrm.li_rm:
            if hasattr(rm, "nivelBMT"):
                if rm.nivelBMT == 0:
                    if (rm.from_sq + rm.to_sq + rm.promotion) not in self.st_best_moves:
                        self.st_best_moves.add(rm.from_sq + rm.to_sq + rm.promotion)

        FasterCode.set_fen(self.cut_fen(fen))
        self.position_is_check = FasterCode.ischeck()

        lista = FasterCode.get_exmoves()

        self.owner = owner
        self.checks = 0
        self.captures = 0
        self.bm_is_check = False
        self.bm_is_capture = False
        self.bm_is_threat = False
        self.bm_is_mate_threat = False
        self.bm_is_mate = False
        self.bm_is_discovered_attack = False
        move_index = -1
        self.bm_move_index = 0
        self.nextmove_checks = 0
        self.nextmove_captures = 0
        self.nextmove_li_checks = []
        self.nextmove_li_captures = []
        self.li_all_moves = []
        self.nextmove_li_all_moves = []

        for infoMove in lista:
            move_index += 1
            self.li_all_moves.append(infoMove.move())

            if infoMove.mate():
                self.st_best_moves.add(infoMove.move())
                self.bm_is_mate = True

            if infoMove.move() in self.st_best_moves:
                self.bm_move_index = move_index

            if infoMove.check() or infoMove.mate():
                # pr int("Check: %s" % infoMove.move())
                self.checks += 1
                self.li_checks.append(infoMove.move())
                self.li_check_targets.append(infoMove.xto())
                if infoMove.move() in self.st_best_moves:
                    self.bm_is_check = True

            if infoMove.capture():
                # pr int("Capture: %s" % infoMove.move())
                self.captures += 1
                self.li_captures.append(infoMove.move())
                self.li_capture_targets.append(infoMove.xto())
                if infoMove.move() in self.st_best_moves:
                    self.bm_is_capture = True

        for move in self.li_all_moves:
            # pr int("Checking [%s] for new threats" % move)
            FasterCode.set_fen(self.cut_fen(self.fen))
            FasterCode.make_move(move)  # Make the first best move
            new_fen = FasterCode.get_fen()
            if " b " in new_fen:  # Change side so we get another move
                new_fen = new_fen.replace(" b ", " w ")
            else:
                new_fen = new_fen.replace(" w ", " b ")
            new_fen = self.cut_fen(new_fen)
            FasterCode.set_fen(new_fen)
            # pr int("FEN after [%s]: %s" % (move, FasterCode.get_fen()))

            if move in self.st_best_moves:
                self.fen_after_best_move_and_null_move = new_fen

            # pr int('All follow up moves: ' + ', '.join(FasterCode.get_moves()))
            lista = FasterCode.get_exmoves()
            for infoMove in lista:
                # pr int("[%s] checking follow up move %s" % (move, infoMove.move()))
                if move in self.st_best_moves:
                    self.nextmove_li_all_moves.append(infoMove.move())
                if infoMove.mate():
                    # pr int("Threatening mate on next move: %s" % infoMove.move())
                    self.add_threat(move)
                    if move in self.st_best_moves:
                        self.bm_is_threat = self.bm_is_mate_threat = True
                if infoMove.check():
                    # pr int("Next move [%s] check: %s" % (move, infoMove.move()))
                    if move in self.st_best_moves:
                        self.nextmove_checks += 1
                        self.nextmove_li_checks.append(infoMove.move())
                    if infoMove.xto() not in self.li_check_targets:  # new check = threat
                        # pr int("New check is threatened: %s" % infoMove.move())
                        self.add_threat(move)
                        if move in self.st_best_moves:
                            self.bm_is_threat = True
                if infoMove._capture:
                    # pr int("Next move [%s] capture: %s" % (move, infoMove.move()))
                    if move in self.st_best_moves:
                        self.nextmove_captures += 1
                        self.nextmove_li_captures.append(infoMove.move())
                    if infoMove.xto() not in self.li_capture_targets:  # new capture = threat
                        if infoMove.xfrom() != self.rm.to_sq:  # a different piece now is attacking something
                            # pr int("New discovered attack: %s" % infoMove.move())
                            self.add_threat(move)
                            if move in self.st_best_moves:
                                self.bm_is_discovered_attack = True
                                self.bm_is_threat = True
                        else:
                            # pr int("New capture is threatened: %s" % infoMove.move())
                            self.add_threat(move)
                            if move in self.st_best_moves:
                                self.bm_is_threat = True

    def add_threat(self, move):
        # pr int("%s is a threat!" % move)
        if move not in self.li_threats:
            self.li_threats.append(move)

    def fm_show_checklist(self):
        if self.position_is_check:
            QTUtil2.message(self.owner, _("Forcing moves are not supported while you are in check."))
            return
        if self.bm_is_getting_mated:
            QTUtil2.message(self.owner, _("You cannot avoid being mated here. Forcing moves do not matter."))
            return
        w = WForcingMoves.WForcingMoves(self)
        w.exec_()

    def cut_fen(self, fen):
        if " w " in fen:
            new_str = fen.partition(' w ')[0] + " w - 0 1"
        else:
            new_str = fen.partition(' b ')[0] + " b - 0 1"
        return new_str
