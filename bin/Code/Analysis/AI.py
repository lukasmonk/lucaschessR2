import webbrowser

import Code
import Code.Nags.Nags
from Code import Util
from Code.Base import Game
from Code.QT import Colocacion
from Code.QT import FormLayout
from Code.QT import Grid, Columnas
from Code.QT import Iconos, QTUtil2, QTUtil
from Code.QT import LCDialog
from Code.QT import QTVarios
from Code.SQL import UtilSQL

SEPARADOR_KEY = "||"


class Prompt:
    def __init__(self, name="", prompt="", web="", xid="", order=0):
        self.name = name
        self.prompt = prompt
        self.web = web
        self.order = order
        self.xid = xid

    def save(self):
        return {
            "NAME": self.name,
            "PROMPT": self.prompt,
            "WEB": self.web,
            "ORDER": self.order,
            "XID": self.xid,
        }

    def key(self):
        return f"{self.order:04d}{SEPARADOR_KEY}{self.name}{SEPARADOR_KEY}{self.xid}"

    def restore(self, dic):
        self.name = dic.get("NAME", self.name)
        self.prompt = dic.get("PROMPT", self.prompt)
        self.web = dic.get("WEB", self.web)
        self.xid = dic.get("XID", Util.huella())


def add_default(db):
    prompt = """Act as an International Master of chess.
Analyze a chess game move by move, explaining what happened in each move, and the result should be displayed in a pgn file where the comments are in each move and in braces, following the pgn standard.
The writing style should be instructive and detailed aimed at an intermediate player.
Consider the following context: The analysis should include intermediate comments, covering both the player's and the opponent's moves. Additionally, it should include an evaluation of the positions after each move, focusing on both tactics and strategy.

Here is the final prompt:

Analyze the following chess game move by move, providing detailed comments for each move and displaying the result in a pgn file. The comments should be in braces and follow the pgn standard. The comments should be intermediate, covering both the player's and the opponent's moves, and including an evaluation of the positions after each move. The analysis should focus on both tactics and strategy.
"""
    if Code.configuration.x_translator != "en":
        prompt += f"The answer must be in {Code.configuration.language()}.\n"
    oprompt = Prompt(name=_("Basic"), prompt=prompt, xid=Util.huella())
    key = oprompt.key()
    db[key] = oprompt


def add_submenu(submenu_base):
    submenu = submenu_base.submenu(_("Help requesting an analysis from an AI"), Iconos.AI())
    with UtilSQL.DictSQL(Code.configuration.file_prompts()) as db:
        li_keys = db.keys(si_ordenados=True)
        if len(li_keys) == 0:
            add_default(db)
            li_keys = db.keys(si_ordenados=True)
        for key in li_keys:
            name = key.split(SEPARADOR_KEY)[1]
            submenu.opcion(f"ai_{key}", name, Iconos.PuntoAzul())

    submenu.opcion("ai_", _("Maintenance"), Iconos.Configurar())


def run_menu(main_window, key: str, game: Game.Game):
    key = key[3:]
    if not key:
        maintenance(main_window, game)
    else:
        launch(main_window, key, game)


def launch(main_window, key: str, game: Game.Game):
    with UtilSQL.DictSQL(Code.configuration.file_prompts()) as db:
        oprompt: Prompt = db[key]
    launch_prompt(main_window, oprompt, game)


def launch_prompt(main_window, oprompt: Prompt, game: Game.Game):
    if oprompt.web:
        webbrowser.open(oprompt.web)

    prompt = oprompt.prompt
    game_new = Game.Game()
    game_new.assign_other_game(game)
    game_new.remove_info_moves()
    prompt = prompt.strip() + f"\nThe game is:\n{game.pgn()}"
    QTUtil.set_clipboard(prompt)

    QTUtil2.temporary_message(main_window, _("The prompt is on the clipboard, to paste into the AI chat."), 2.2)


def maintenance(mainwindow, game: Game.Game):
    w = WPrompts(mainwindow, game)
    w.exec_()


class WPrompts(LCDialog.LCDialog):
    def __init__(self, owner, game):
        self.owner = owner
        self.game = game
        icono = Iconos.AI()
        extparam = "WPrompts"
        title = _("Prompts")
        LCDialog.LCDialog.__init__(self, owner, title, icono, extparam)

        self.db = UtilSQL.DictSQL(Code.configuration.file_prompts())
        self.li_keys = self.db.keys(si_ordenados=True)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("name", _("Name"), 300)
        o_columns.nueva("web", _("Web"), 300)
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)

        tb = QTVarios.LCTB(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.aceptar)
        tb.new(_("New"), Iconos.TutorialesCrear(), self.new)
        tb.new(_("Modify"), Iconos.Modificar(), self.modify)
        tb.new(_("Remove"), Iconos.Borrar(), self.remove)
        tb.new(_("Copy"), Iconos.Copiar(), self.copy)
        tb.new(_("Up"), Iconos.Arriba(), self.up)
        tb.new(_("Down"), Iconos.Abajo(), self.down)
        tb.new(_("Test"), Iconos.AI(), self.test)

        layout = Colocacion.V()
        layout.control(tb).control(self.grid)
        self.setLayout(layout)

        self.register_grid(self.grid)

        self.restore_video(altoDefecto=560)
        self.grid.setFocus()
        self.grid.gotop()

    def end_tasks(self):
        self.save_video()
        self.db.close()

    def aceptar(self):
        self.end_tasks()
        self.accept()

    def closeEvent(self, event):
        self.end_tasks()

    def grid_num_datos(self, grid):
        return len(self.li_keys)

    def grid_dato(self, grid, row, o_column):
        col = o_column.key
        key = self.li_keys[row]
        prompt: Prompt = self.db[key]
        return getattr(prompt, col)

    def next_order(self):
        x = -1
        for key in self.li_keys:
            order, name, xid = key.split(SEPARADOR_KEY)
            order = int(order)
            if order > x:
                x = order
        return x + 1

    def refresh_all(self):
        self.li_keys = self.db.keys(si_ordenados=True)
        self.grid.refresh()

    def new(self):
        oprompt = Prompt(xid=Util.huella())
        if self.edit(oprompt):
            oprompt.order = self.next_order()
            self.db[oprompt.key()] = oprompt
            self.refresh_all()
            self.grid.gobottom()

    def modify(self):
        row = self.grid.recno()
        if row >= 0:
            key_prev = self.li_keys[row]
            oprompt = self.db[key_prev]
            if self.edit(oprompt):
                key_new = oprompt.key()
                if key_new != key_prev:
                    del self.db[key_prev]
                self.db[key_new] = oprompt
                self.refresh_all()

    def edit(self, oprompt: Prompt) -> bool:
        name, prompt, web = oprompt.name, oprompt.prompt, oprompt.web
        error = None
        while True:
            form = FormLayout.FormLayout(self, _("New try"), Iconos.AI(), anchoMinimo=640)
            form.separador()
            form.edit(_("Name"), name)
            form.separador()
            form.editbox(_("Prompt"), alto=6, init_value=prompt)
            form.separador()
            form.edit(_("Web"), web)
            form.separador()
            if error:
                form.apart_np(error)
                form.separador()

            resultado = form.run()
            if resultado is None:
                return False

            accion, li_resp = resultado
            name, prompt, web = li_resp
            web = web.strip()
            if not name:
                error = _("Name") + "???"
                continue
            if not prompt:
                error = _("Prompt") + "???"
                continue
            oprompt.name = name.replace(SEPARADOR_KEY, "-")
            oprompt.prompt = prompt.replace(SEPARADOR_KEY, "-")
            oprompt.web = web
            return True

    def copy(self):
        row = self.grid.recno()
        if row >= 0:
            key = self.li_keys[row]
            oprompt = self.db[key]
            oprompt_new = Prompt()
            oprompt_new.restore(oprompt.save())
            oprompt_new.order = self.next_order()
            oprompt_new.xid = Util.huella()
            if self.edit(oprompt_new):
                self.db[oprompt_new.key()] = oprompt_new
                self.refresh_all()
                self.grid.gobottom()

    def up(self):
        row = self.grid.recno()
        if row < 1:
            return
        current_key, previous_key = self.li_keys[row], self.li_keys[row - 1]
        current_prompt, previous_prompt = self.db[current_key], self.db[previous_key]
        current_order, previous_order = current_prompt.order, previous_prompt.order
        current_prompt.order = previous_order
        previous_prompt.order = current_order
        del self.db[current_key]
        del self.db[previous_key]
        self.db[current_prompt.key()] = current_prompt
        self.db[previous_prompt.key()] = previous_prompt
        self.refresh_all()
        self.grid.goto(row - 1, 0)

    def down(self):
        row = self.grid.recno()
        if row >= (len(self.li_keys) - 1):
            return
        current_key, next_key = self.li_keys[row], self.li_keys[row + 1]
        current_prompt, next_prompt = self.db[current_key], self.db[next_key]
        current_order, next_order = current_prompt.order, next_prompt.order
        current_prompt.order = next_order
        next_prompt.order = current_order
        del self.db[current_key]
        del self.db[next_key]
        self.db[current_prompt.key()] = current_prompt
        self.db[next_prompt.key()] = next_prompt
        self.refresh_all()
        self.grid.goto(row + 1, 0)

    def grid_doble_click(self, grid, row, o_column):
        self.modify()

    def remove(self):
        row = self.grid.recno()
        if row >= 0:
            key = self.li_keys[row]
            prompt = self.db[key]

            if QTUtil2.pregunta(self, _("Are you sure you want to remove %s?") % prompt.name):
                del self.db[key]
                del self.li_keys[row]
                self.grid.refresh()

    def test(self):
        row = self.grid.recno()
        if row >= 0:
            key = self.li_keys[row]
            prompt = self.db[key]
            launch_prompt(self, prompt, self.game)
