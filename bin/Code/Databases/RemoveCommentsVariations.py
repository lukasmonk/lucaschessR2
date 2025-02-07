import re

import Code
from Code.Base import Game, Move
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import LCDialog
from Code.QT import QTVarios
from Code.QT import QTUtil


class WRemoveCommentsVariations(LCDialog.LCDialog):
    def __init__(self, owner, key, is_body):
        LCDialog.LCDialog.__init__(self, owner, _("Remove comments and variations"), Iconos.DeleteColumn(), key)

        self.rem = RemoveCommentsVariations(key)

        self.ok = False

        self.lb_title = Controles.LB(self, _("Remove") + ":").set_font_type(puntos=14, peso=700)

        self.chb_variations = Controles.CHB(self, _("Variations"), self.rem.rem_variations)
        self.chb_nags = Controles.CHB(self, _("Ratings") + " (NAGs)", self.rem.rem_nags)
        self.chb_analysis = Controles.CHB(self, _("Analysis"), self.rem.rem_analysis)
        self.chb_comments = Controles.CHB(self, _("Comments"), self.rem.rem_comments)
        self.chb_comments.capture_changes(self, self.changes_done)
        self.chb_brackets = Controles.CHB(self, _("Brackets in comments"), self.rem.rem_brackets)
        self.chb_brackets.capture_changes(self, self.changes_done)
        self.chb_clk = Controles.CHB(self, "[%clk ...]", self.rem.rem_clk)
        self.chb_emt = Controles.CHB(self, "[%emt ...]", self.rem.rem_emt)
        self.chb_eval = Controles.CHB(self, "[%eval ...]", self.rem.rem_eval)
        self.chb_csl = Controles.CHB(self, "[%csl ...]", self.rem.rem_csl)
        self.chb_cal = Controles.CHB(self, "[%cal ...]", self.rem.rem_cal)
        self.chb_other = Controles.CHB(self, "[%<?> ...] → <?> = ", self.rem.rem_other)
        self.ed_other = Controles.ED(self, self.rem.val_other)
        self.ed_other.setMinimumWidth(90)

        if is_body:
            self.chb_analysis.hide()
            self.chb_analysis.set_value(False)

        tb = QTVarios.LCTB(self)
        tb.new(_("Accept"), Iconos.Aceptar(), self.aceptar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.reject)

        layout = Colocacion.V()
        layout.control(tb)
        layout.espacio(10)
        layout.controlc(self.lb_title)
        layout.espacio(10)

        sp = 50
        for chb in (self.chb_variations, self.chb_analysis, self.chb_nags, self.chb_comments, self.chb_brackets,
                    self.chb_clk, self.chb_emt, self.chb_eval, self.chb_csl, self.chb_cal, self.chb_other):
            if chb == self.chb_brackets:
                sp += 20
            elif chb == self.chb_clk:
                sp += 20
            elif chb == self.chb_other:
                lychb = Colocacion.H().espacio(sp).control(chb).control(self.ed_other)
                layout.otro(lychb)
                continue

            lychb = Colocacion.H().espacio(sp).control(chb)
            layout.otro(lychb)

        layout.espacio(20)
        layout.relleno()
        self.setLayout(layout)

        self.restore_video(default_width=460)
        self.changes_done()

    def changes_done(self):
        disable = self.chb_comments.valor() or self.chb_brackets.valor()
        for chb in (self.chb_clk, self.chb_emt, self.chb_eval, self.chb_csl, self.chb_cal, self.chb_other):
            if disable:
                chb.set_value(False)
                chb.hide()
            else:
                chb.show()
        self.ed_other.setVisible(not disable)

        if self.chb_comments.valor():
            self.chb_brackets.set_value(False)
            self.chb_brackets.hide()
        else:
            self.chb_brackets.show()

        QTUtil.shrink(self)


    def aceptar(self):
        self.rem.remove_variations(self.chb_variations.valor())
        self.rem.remove_nags(self.chb_nags.valor())
        self.rem.remove_comments(self.chb_comments.valor())
        self.rem.remove_brackets(self.chb_brackets.valor())
        self.rem.remove_clk(self.chb_clk.valor())
        self.rem.remove_emt(self.chb_emt.valor())
        self.rem.remove_eval(self.chb_eval.valor())
        self.rem.remove_csl(self.chb_csl.valor())
        self.rem.remove_cal(self.chb_cal.valor())
        self.rem.remove_analysis(self.chb_analysis.valor())
        self.rem.remove_other(self.chb_other.valor(), self.ed_other.texto().strip())
        self.rem.save()

        self.save_video()
        self.accept()

    def run(self, body: bytes) -> bytes:
        return self.rem.run(body)

    def run_game(self, game):
        return self.rem.run_game(game)


class RemoveCommentsVariations:
    def __init__(self, key):
        self.key = key
        dic = Code.configuration.read_variables(self.key)
        self.rem_variations = dic.get("rem_variations", False)
        self.rem_nags = dic.get("rem_nags", False)
        self.rem_analysis = dic.get("rem_analysis", False)
        self.rem_comments = dic.get("rem_comments", False)
        self.rem_brackets = dic.get("rem_brackets", False)
        self.rem_clk = dic.get("rem_clk", False)
        self.rem_emt = dic.get("rem_emt", False)
        self.rem_eval = dic.get("rem_eval", False)
        self.rem_csl = dic.get("rem_csl", False)
        self.rem_cal = dic.get("rem_cal", False)
        self.rem_other = dic.get("rem_other", False)
        self.val_other = dic.get("val_other", "")
        self.ok = len([v for k, v in dic.items() if k.startswith("rem_") and v]) > 0

    def save(self):
        dic = Code.configuration.read_variables(self.key)
        dic["rem_variations"] = self.rem_variations
        dic["rem_nags"] = self.rem_nags
        dic["rem_analysis"] = self.rem_analysis
        dic["rem_comments"] = self.rem_comments
        dic["rem_brackets"] = self.rem_brackets
        dic["rem_clk"] = self.rem_clk
        dic["rem_emt"] = self.rem_emt
        dic["rem_eval"] = self.rem_eval
        dic["rem_csl"] = self.rem_csl
        dic["rem_cal"] = self.rem_cal
        dic["rem_other"] = self.rem_other
        dic["val_other"] = self.val_other
        Code.configuration.write_variables(self.key, dic)
        self.ok = len([v for k, v in dic.items() if k.startswith("rem_") and v]) > 0

    def remove_variations(self, value):
        self.rem_variations = value

    def remove_nags(self, value):
        self.rem_nags = value

    def remove_analysis(self, value):
        self.rem_analysis = value

    def remove_comments(self, value):
        self.rem_comments = value

    def remove_brackets(self, value):
        self.rem_brackets = value

    def remove_clk(self, value):
        self.rem_clk = value

    def remove_emt(self, value):
        self.rem_emt = value

    def remove_eval(self, value):
        self.rem_eval = value

    def remove_csl(self, value):
        self.rem_csl = value

    def remove_cal(self, value):
        self.rem_cal = value

    def remove_other(self, value, param):
        if not param:
            value = False
        self.rem_other = value
        self.val_other = param

    @staticmethod
    def remove(texto, c_ini: str, c_fin: str):
        pos = 0
        total = len(texto)
        new_text = []
        while pos < total:
            bb = texto[pos]
            if bb == c_ini:
                ok = False
                for busca in range(pos + 1, total):
                    if texto[busca] == c_fin:
                        pos = busca + 1
                        ok = True
                        break
                if not ok:
                    pos = total
            else:
                new_text.append(bb)
                pos += 1
        return "".join(new_text)

    @staticmethod
    def remove_comando_brackets(texto, comando):
        pattern = rf'%{comando}\s+[^\]\s]+(\s+|\])'
        texto = re.sub(pattern, lambda m: ']' if ']' in m.group(1) else '', texto)
        # texto = re.sub(rf'%{comando} [^%\]]*', '', texto)
        # texto = re.sub(rf'%{comando}\s+[^\]\s]+(\s+|\])]*', '', texto)

        # Eliminar corchetes vacíos
        texto = re.sub(r'\[ *\]', '', texto)

        # Limpiar espacios extra dentro de los corchetes restantes
        # texto = re.sub(r'\[ +', '[', texto)
        # texto = re.sub(r' +\]', ']', texto)
        return texto

    def run(self, body: bytes):
        if not self.ok:
            return body
        texto = body.decode("utf-8", errors="backslashreplace")

        if self.rem_variations:
            pos = 0
            total = len(texto)
            new_body = []
            ini_par = "("
            end_par = ")"
            ini_com = "{"
            end_com = "}"
            in_comment = False
            while pos < total:
                c = texto[pos]
                if c == ini_com:
                    in_comment = True
                elif c == end_com:
                    in_comment = False
                if not in_comment and c == ini_par:
                    par = 1
                    in_comment = False
                    for busca in range(pos + 1, total):
                        bb = texto[busca]
                        if in_comment:
                            if bb == end_com:
                                in_comment = False
                            continue
                        if bb == end_par:
                            par -= 1
                            if par == 0:
                                pos = busca + 1
                                break
                        elif bb == ini_par:
                            par += 1
                        elif bb == ini_com:
                            in_comment = True
                    in_comment = False
                else:
                    new_body.append(c)
                    pos += 1
            texto = "".join(new_body)

        if self.rem_nags:
            texto = re.sub(r"\$\d+", "", texto)
            texto = texto.replace("!", "")
            texto = texto.replace("?", "")

        if self.rem_comments:
            texto = self.remove(texto, "{", "}")
        else:
            rec = False
            if self.rem_brackets:
                texto = self.remove(texto, "[", "]")
                rec = True
            else:
                if self.rem_clk:
                    texto = self.remove_comando_brackets(texto, "clk")
                    rec = True
                if self.rem_emt:
                    texto = self.remove_comando_brackets(texto, "emt")
                    rec = True
                if self.rem_eval:
                    texto = self.remove_comando_brackets(texto, "eval")
                    rec = True
                if self.rem_csl:
                    texto = self.remove_comando_brackets(texto, "csl")
                    rec = True
                if self.rem_cal:
                    texto = self.remove_comando_brackets(texto, "cal")
                    rec = True
                if self.rem_other:
                    texto = self.remove_comando_brackets(texto, self.val_other)
                    rec = True
            if rec:
                while "{ " in texto:
                    texto = texto.replace("{ ", "{")
                texto = texto.replace("{}", "")
                texto = re.sub(r'\d+\.\.\.', '', texto)
                while "  " in texto:
                    texto = texto.replace("  ", " ")
        return texto.encode("utf-8", errors="ignore")

    def run_game(self, game: Game.Game):
        if not self.ok:
            return game, False

        changed = False
        move: Move.Move
        for move in game.li_moves:
            if self.rem_variations:
                if len(move.variations) > 0:
                    move.variations.clear()
                    changed = True

            if self.rem_nags:
                if move.li_nags:
                    move.li_nags = []
                    changed = True

            if self.rem_analysis:
                if move.analysis:
                    move.analysis = None
                    changed = True

            if move.comment:
                comment_ini = move.comment
                if self.rem_comments:
                    move.comment = ""
                else:
                    if self.rem_brackets:
                        move.comment = self.remove(comment_ini, "[", "]")
                    else:
                        if self.rem_clk:
                            move.comment = self.remove_comando_brackets(move.comment, "clk")
                        if self.rem_emt:
                            move.comment = self.remove_comando_brackets(move.comment, "emt")
                        if self.rem_eval:
                            move.comment = self.remove_comando_brackets(move.comment, "eval")
                        if self.rem_csl:
                            move.comment = self.remove_comando_brackets(move.comment, "csl")
                        if self.rem_cal:
                            move.comment = self.remove_comando_brackets(move.comment, "cal")
                        if self.rem_other:
                            move.comment = self.remove_comando_brackets(move.comment, self.val_other)
                if move.comment != comment_ini:
                    move.comment.strip()
                    while "  " in move.comment:
                        move.comment = move.comment.replace("  ", " ")
                    changed = True
        return game, changed
