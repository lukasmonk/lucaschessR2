import random
import time

import Code
from Code import Util
from Code.Base import Position
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios


class ManagerChallenge101:
    def __init__(self, procesador):
        self.main_window = procesador.main_window
        self.board = self.main_window.board
        self.procesador = procesador
        self.configuration = procesador.configuration
        self.cod_variables = "challenge101"
        self.puntos_totales = 0
        self.puntos_ultimo = 0
        self.pendientes = 10
        self.st_randoms = set()
        self.st_lines = set()  # para no salvar mas de una vez una linea
        self.key = str(Util.today())
        random.seed()

        fmt = Code.path_resource("IntFiles", "tactic0.bm")

        with open(fmt, "rt", encoding="utf-8", errors="ignore") as f:
            self.li_lineas_posicion = [linea for linea in f if linea.strip()]

        self.siguiente_posicion()

    def siguiente_posicion(self):
        num_lineas_posicion = len(self.li_lineas_posicion)
        while True:
            random_pos = random.randint(0, num_lineas_posicion - 1)
            if not (random_pos in self.st_randoms):
                self.st_randoms.add(random_pos)
                break
        self.fen, self.result, self.pgn_result, self.pgn, self.difficult = (
            self.li_lineas_posicion[random_pos].strip().split("|")
        )
        self.difficult = int(self.difficult)

        self.cp = Position.Position()
        self.cp.read_fen(self.fen)

        self.is_white = " w " in self.fen
        self.board.bloqueaRotacion(False)
        self.board.set_dispatcher(self.player_has_moved)
        self.board.set_position(self.cp)
        self.board.set_side_bottom(self.is_white)
        self.board.activate_side(self.is_white)
        self.board.set_side_indicator(self.is_white)

        self.intentos = 0
        self.max_intentos = (self.difficult + 1) // 2 + 4
        self.iniTime = time.time()

    def lee_results(self):
        dic = self.configuration.read_variables(self.cod_variables)
        results = dic.get("RESULTS", [])
        results.sort(key=lambda x: -x[1])
        return results

    def guarda_puntos(self):
        dic = self.configuration.read_variables(self.cod_variables)
        results = dic.get("RESULTS", [])
        if len(results) >= 10:
            ok = False
            for k, pts in results:
                if pts <= self.puntos_totales:
                    ok = True
                    break
        else:
            ok = True
        if ok:
            ok_find = False
            for n in range(len(results)):
                if results[n][0] == self.key:
                    ok_find = True
                    results[n] = (self.key, self.puntos_totales)
                    break
            if not ok_find:
                results.append((self.key, self.puntos_totales))
            results.sort(reverse=True, key=lambda x: "%4d%s" % (x[1], x[0]))
            if len(results) > 10:
                results = results[:10]
            dic["RESULTS"] = results
            self.configuration.write_variables(self.cod_variables, dic)

    def menu(self):
        main_window = self.procesador.main_window
        main_window.cursorFueraBoard()
        menu = QTVarios.LCMenu(main_window)
        self.configuration.set_property(menu, "101")
        f = Controles.FontType(name=Code.font_mono, puntos=12)
        fbold = Controles.FontType(name=Code.font_mono, puntos=12, peso=700)
        fbolds = Controles.FontType(name=Code.font_mono, puntos=12, peso=500, is_underlined=True)
        menu.set_font(f)

        li_results = self.lee_results()
        icono = Iconos.PuntoAzul()

        menu.separador()
        titulo = ("** %s **" % _("Challenge 101")).center(30)
        if self.pendientes == 0:
            menu.opcion("close", titulo, Iconos.Terminar())
        else:
            menu.opcion("continuar", titulo, Iconos.Pelicula_Seguir())
        menu.separador()
        ok_en_lista = False
        for n, (fecha, pts) in enumerate(li_results, 1):
            if fecha == self.key:
                ok_en_lista = True
                ico = Iconos.PuntoEstrella()
                font_type = fbolds
            else:
                ico = icono
                font_type = None
            txt = str(fecha)[:16]
            menu.opcion(None, "%2d. %-20s %6d" % (n, txt, pts), ico, font_type=font_type)

        menu.separador()
        menu.opcion(None, "", Iconos.PuntoNegro())
        menu.separador()
        if self.puntos_ultimo:
            menu.opcion(None, ("+%d" % (self.puntos_ultimo)).center(30), Iconos.PuntoNegro(), font_type=fbold)
        if self.pendientes == 0:
            if not ok_en_lista:
                menu.opcion(
                    None, ("%s: %d" % (_("Score"), self.puntos_totales)).center(30), Iconos.Gris(), font_type=fbold
                )
            menu.separador()
            menu.opcion("close", _("GAME OVER").center(30), Iconos.Terminar())
        else:
            menu.opcion(
                None, ("%s: %d" % (_("Score"), self.puntos_totales)).center(30), Iconos.PuntoNegro(), font_type=fbold
            )
            menu.separador()
            menu.opcion(
                None,
                ("%s: %d" % (_("Positions left"), self.pendientes)).center(30),
                Iconos.PuntoNegro(),
                font_type=fbold,
            )
            menu.separador()
            menu.opcion(None, "", Iconos.PuntoNegro())
            menu.separador()
            menu.opcion("continuar", _("Continue"), Iconos.Pelicula_Seguir())
            menu.separador()
            menu.opcion("close", _("Close"), Iconos.MainMenu())

        resp = menu.lanza()

        return not (resp == "close" or self.pendientes == 0)

    def player_has_moved(self, from_sq, to_sq, promotion=""):
        self.savePosition()  # Solo cuando ha hecho un intento
        self.puntos_ultimo = 0
        if from_sq + to_sq == self.result:  # No hay promotiones
            tm = time.time() - self.iniTime
            self.board.disable_all()
            self.cp.play(from_sq, to_sq, promotion)
            self.board.set_position(self.cp)
            self.board.put_arrow_sc(from_sq, to_sq)

            puntos = int(1000 - (1000 / self.max_intentos) * self.intentos)
            puntos -= int(tm * 7)

            if puntos > 0:
                self.puntos_totales += puntos
                self.guarda_puntos()
                self.puntos_ultimo = puntos

            self.pendientes -= 1
            if self.menu():
                self.siguiente_posicion()
            return True
        else:
            self.intentos += 1
            if self.intentos < self.max_intentos:
                QTUtil2.temporary_message_without_image(
                    self.main_window, str(self.max_intentos - self.intentos), 0.5, puntos=20, background="#ffd985"
                )
            else:
                self.board.set_position(self.cp)
                self.board.put_arrow_sc(self.result[:2], self.result[2:])
                self.pendientes = 0
                self.menu()
                return True
        return False

    def savePosition(self):
        line = "%s|%s|%s|%s\n" % (self.fen, str(self.key)[:19], self.pgn_result, self.pgn)
        if not (line in self.st_lines):
            self.st_lines.add(line)
            fich = self.configuration.ficheroPresentationPositions
            existe = Util.exist_file(fich)
            with open(fich, "at") as q:
                line = "%s|%s|%s|%s\n" % (self.fen, str(self.key)[:19], self.pgn_result, self.pgn)
                q.write(line)
            if not existe:
                self.procesador.entrenamientos.menu = None
