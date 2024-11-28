from Code import Manager
from Code.Base.Constantes import TB_COMMENTS
from Code.Nags import Nags
from Code.QT import QTUtil2


class ManagerOpeningLines(Manager.Manager):
    show_comments = None
    dic_comments: dict

    def tb_with_comments(self, li_tb):
        ok_comments = False
        for reg in self.dic_comments.values():
            if reg.get("COMENTARIO"):
                ok_comments = True
                break

        if ok_comments:
            li_tb.append(TB_COMMENTS)
            dic = self.configuration.read_variables("OPENINLINES_TRAIN")
            self.show_comments = dic.get("SHOWCOMMENTS", False)
            self.main_window.base.set_title_toolbar(TB_COMMENTS, _("Disable") if self.show_comments else _("Enable"))
        else:
            self.show_comments = None
        self.set_toolbar(li_tb)

    def change_comments(self):
        self.show_comments = not self.show_comments
        self.main_window.base.set_title_toolbar(TB_COMMENTS, _("Disable") if self.show_comments else _("Enable"))
        dic = self.configuration.read_variables("OPENINLINES_TRAIN")
        dic["SHOWCOMMENTS"] = self.show_comments
        self.configuration.write_variables("OPENINLINES_TRAIN", dic)

    def add_move(self, move, is_player_move):
        comment = None
        ventaja = None
        valoracion = None

        fenm2 = move.position.fenm2()
        if fenm2 in self.dic_comments:
            reg = self.dic_comments[fenm2]
            if "COMENTARIO" in reg:
                comment = reg["COMENTARIO"]
                move.set_comment(comment)
            if "VENTAJA" in reg:
                ventaja = reg["VENTAJA"]
                move.add_nag(ventaja)
            if "VALORACION" in reg:
                valoracion = reg["VALORACION"]
                move.add_nag(valoracion)

        self.game.add_move(move)
        self.check_boards_setposition()

        self.put_arrow_sc(move.from_sq, move.to_sq)
        self.beep_extended(is_player_move)

        self.pgn_refresh(self.game.last_position.is_white)
        self.refresh()

        if self.show_comments and comment:
            if ventaja:
                comment += "\n\n* " + Nags.dic_text_nags(ventaja)
            if valoracion:
                comment += "\n\n* " + Nags.dic_text_nags(valoracion)

            text_move = "%d." % ((len(self.game) - 1) // 2 + 1)
            if not move.is_white():
                text_move += ".."
            text_move += move.pgn_translated()

            QTUtil2.message_menu(self.main_window.base.pgn, text_move, comment, not is_player_move)

    def add_coments_all_game(self):
        for move in self.game.li_moves:
            fenm2 = move.position.fenm2()
            if fenm2 in self.dic_comments:
                reg = self.dic_comments[fenm2]
                if "COMENTARIO" in reg:
                    comment = reg["COMENTARIO"]
                    move.set_comment(comment)
                if "VENTAJA" in reg:
                    ventaja = reg["VENTAJA"]
                    move.add_nag(ventaja)
                if "VALORACION" in reg:
                    valoracion = reg["VALORACION"]
                    move.add_nag(valoracion)
