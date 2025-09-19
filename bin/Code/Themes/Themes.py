import colorsys
import zlib

import FasterCode
from PySide2.QtCore import QByteArray, QSize
from PySide2.QtGui import QPixmap, QPainter, QColor
from PySide2.QtSvg import QSvgRenderer

import Code
from Code.Base import Move
from Code.Base.Constantes import PZ_VALUES
from Code.Engines import EngineResponse


class Themes:
    def __init__(self):
        self.dic_standard = {
            "advancedPawn": _("Advanced pawn"),  # A
            "attraction": _("Attraction"),  # A
            "backRankMate": _("Back rank mate"),  # A
            "boardVision": _("Board vision"),
            "capturingDefender": _("Capture the defender"),
            "checkMateThreat": _("Checkmate threat"),
            "clearance": _("Clearance"),
            "decoy": _("Decoy"),  # A
            "defensiveMove": _("Defensive move"),
            "deflection": _("Deflection"),  # A
            "desperado": _("Desperado"),
            "discoveredAttack": _("Discovered attack"),  # ?
            "doubledPawns": _("Doubled pawns"),
            "doubleCheck": _("Double check"),  # A
            "exposedKing": _("Exposed king"),
            "exchange": _("Exchange"),
            "forcedMove": _("Forced Move"),
            "fork": _("Fork / Double attack"),  # ?
            "hangingPiece": _("Hanging piece"),
            "interference": _("Interference"),
            "isolatedPawn": _("Isolated pawn"),
            "openFile": _("Open file ||Tactic theme"),
            "overload": _("Overload"),
            "outpost": _("Outpost"),
            "passedPawn": _("Passed pawn"),
            "pin": _("Pin"),  # A
            "promotion": _("Promotion"),
            "quietMove": _("Quiet move"),
            "sacrifice": _("Sacrifice"),  # ?
            "semiProtectedPiece": _("Semi-protected piece"),
            "simplification": _("Simplification"),
            "skewer": _("Skewer"),  # A
            "speculation": _("Speculation"),
            "tempo": _("Tempo"),
            "threat": _("Threat"),
            "trappedPiece": _("Trapped piece"),
            "underPromotion": _("Underpromotion"),  # A
            "weakSquare": _("Weak square"),
            "unsafeSquare": _("Unsafe square"),
            "xRayAttack": _("X-Ray attack"),  # ?
            "zwischenzug": _("Zwischenzug"),  # ?
            "zugzwang": _("Zugzwang"),  # ?
            "advantage": _("Advantage"),
            "anastasiaMate": _("Anastasia's mate"),  # A
            "arabianMate": _("Arabian mate"),  # A
            "bodenMate": _("Boden's mate"),  # A
            "coercion": _("Coercion"),
            "crushing": _("Crushing"),
            "doubleBishopMate": _("Double bishop mate"),
            "dovetailMate": _("Dovetail mate"),  # A
            "hookMate": _("Hook mate"),  # A
            "kingsideAttack": _("King side attack"),
            "queensideAttack": _("Queen side attack"),
            "smotheredMate": _("Smothered mate"),  # A
            "vukovicMate": _("Vukovic mate"),  # A
            "killBoxMate": _("Kill box mate"),  # A
        }
        self.li_custom = []
        self.li_head = []
        self.li_themes = []
        self.dic_pixmap = {}
        self.dic_letters = {}
        self.dic_custom_letters = {}
        self.dic_custom_colors = {}
        self.read()
        self.build()

        self.svg_data = """
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="10">
          <text x="%d" y="9" font-family="Arial" font-size="9" fill="black">%s</text>
        </svg>
        """

    @staticmethod
    def generar_abreviaturas(conceptos):
        abreviaturas = {}
        reservadas = set()

        for concepto in conceptos:
            # Preprocesamiento: eliminar apóstrofes y normalizar
            palabras = concepto.replace("'", "").split()

            # Generar candidato inicial
            if len(palabras) == 1:
                palabra = palabras[0]
                abrev_candidata = (palabra[:3] if len(palabra) >= 3 else palabra + palabra[0] * (3 - len(palabra)))[:3]
            else:
                # Tomar iniciales de las primeras 3 palabras (o todas si son menos)
                abrev_candidata = ''.join(p[0] for p in palabras[:3])
                if len(abrev_candidata) < 3:
                    # Completar con letras de la última palabra
                    abrev_candidata += palabras[-1][1:3 - len(abrev_candidata)]

            # Hacer única si es necesario
            original_candidata = abrev_candidata
            contador = 1
            while abrev_candidata.lower() in reservadas:
                # Modificar la última letra primero
                if contador < len(palabras[-1]):
                    abrev_candidata = abrev_candidata[:-1] + palabras[-1][contador]
                    contador += 1
                else:
                    # Si no hay suficientes letras, agregar un número
                    abrev_candidata = original_candidata[:2] + str(contador)
                    contador += 1

            reservadas.add(abrev_candidata.lower())
            abreviaturas[concepto] = abrev_candidata.upper()

        return abreviaturas

    def gen_letters(self):
        forbidden_chars = r"\/'\"()\-–—%$#@!?¿¡&*[]{}<>+=,:;."
        translation_table = str.maketrans("", "", forbidden_chars)

        def limpia(txt):
            return txt.upper().translate(translation_table)

        li_conceptos = [limpia(self.dic_standard.get(theme, theme)) for theme in self.li_themes]
        dic_abrev = self.generar_abreviaturas(li_conceptos)

        self.dic_letters = {theme: dic_abrev[li_conceptos[pos]] for pos, theme in enumerate(self.li_themes)}

    def get_color(self, theme):
        if theme in self.dic_custom_colors:
            return self.dic_custom_colors[theme]
        if "Mate" in theme:
            color = "#ff9999"
        elif theme == "⧉":
            color = "#ffa638"
        else:
            def generar_color_contraste(xtheme):
                ratio = (zlib.crc32(xtheme.encode()) % 100) / 100.0
                hue = 0.05 + (0.7 - 0.05) * ratio
                lightness = 0.7 + 0.2 * (1.0 - ratio)
                r, g, b = colorsys.hls_to_rgb(hue, lightness, 0.9)
                return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

            color = generar_color_contraste(theme)
        return color

    def get_letters(self, theme):
        if not self.dic_letters:
            self.gen_letters()

        # Convertir string a QByteArray
        if theme == "⧉":
            letters = "+" + theme
        else:
            if theme in self.dic_custom_letters:
                letters = self.dic_custom_letters[theme]
            else:
                letters = self.dic_letters[theme]
        return letters

    def change_custom_letters(self, theme, letters):
        if theme in self.dic_custom_letters:
            del self.dic_custom_letters[theme]
        previous = self.get_letters(theme)
        if letters and letters != previous:
            self.dic_custom_letters[theme] = letters
        self.write()
        del self.dic_pixmap[theme]
        self.dic_letters = {}

    def change_custom_color(self, theme, color):
        if theme in self.dic_custom_colors:
            del self.dic_custom_colors[theme]
        previous = self.get_color(theme)
        if color and color != previous:
            self.dic_custom_colors[theme] = color
        self.write()
        del self.dic_pixmap[theme]

    def gen_pixmap(self, theme):
        letters = self.get_letters(theme)
        num = 1
        svg = self.svg_data % (num, letters)
        svg_bytes = QByteArray(svg.encode('utf-8'))

        # Crear el renderer SVG
        renderer = QSvgRenderer(svg_bytes)

        # Crear un QPixmap
        size = QSize(22, 10)
        pixmap = QPixmap(size)

        color = self.get_color(theme)

        pixmap.fill(QColor(color))
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    def pixmap(self, theme):
        if theme not in self.dic_pixmap:
            self.dic_pixmap[theme] = self.gen_pixmap(theme)
        return self.dic_pixmap[theme]

    def build(self):
        li_themes = []
        for theme in self.li_head:
            if theme in self.li_custom or theme in self.dic_standard:
                li_themes.append(theme)
        li_after = list(x for x in self.dic_standard if x not in li_themes)
        for theme in self.li_custom:
            if theme not in li_themes:
                li_after.append(theme)
        li_after.sort(key=lambda x: self.dic_standard.get(x, x))
        li_themes.extend(li_after)
        self.li_themes = li_themes

    def read(self):
        dic = Code.configuration.read_variables("THEMES")
        self.li_head = dic.get("HEAD", [])
        self.li_custom = dic.get("CUSTOM", [])
        self.dic_custom_letters = dic.get("CUSTOM_LETTERS", {})
        self.dic_custom_colors = dic.get("CUSTOM_COLORS", {})

    def write(self):
        self.li_head = [theme for theme in self.li_head if theme in self.li_custom or theme in self.dic_standard]
        dic = {"HEAD": self.li_head, "CUSTOM": self.li_custom, "CUSTOM_LETTERS": self.dic_custom_letters,
               "CUSTOM_COLORS": self.dic_custom_colors}
        Code.configuration.write_variables("THEMES", dic)

    def __len__(self):
        return len(self.li_themes)

    def name_pos(self, num):
        if num < len(self.li_themes):
            key = self.li_themes[num]
            return self.dic_standard.get(key, key)
        return ""

    def name(self, key):
        return self.dic_standard.get(key, key)

    def key_pos(self, num):
        if num < len(self.li_themes):
            return self.li_themes[num]
        return ""

    def in_head(self, key):
        return key in self.li_head

    def is_custom(self, key):
        return key not in self.dic_standard and key in self.li_custom

    def add_custom(self, key):
        key = key.strip()
        if key not in self.li_custom:
            self.li_custom.append(key)
            self.add_head(key)
            self.gen_letters()
            self.write()

    def rem_custom(self, key):
        if key in self.li_custom:
            self.li_custom.remove(key)
            if not self.rem_head(key):
                self.write()
                self.build()

    def add_head(self, key):
        if key in self.li_head:
            self.li_head.remove(key)
        self.li_head.insert(0, key)
        self.build()
        self.write()

    def rem_head(self, key):
        if key in self.li_head:
            self.li_head.remove(key)
            self.build()
            self.write()
            return True
        return False

    def order_themes(self, st_themes):
        return [theme for theme in self.li_themes if theme in st_themes]

    def str_themes(self, move):
        return ", ".join(self.name(theme) for theme in move.li_themes)

    def verify(self, st_themes):
        for theme in st_themes:
            if theme not in self.dic_standard and theme not in self.li_custom:
                self.add_custom(theme)

    def get_themes_labels(self, move):
        output = []
        for theme in move.li_themes:
            output.append(self.name(theme))
        return output


class CheckTheme:
    theme: str = ""
    is_mate: bool = False

    def check_move(self, move: Move.Move):
        if self.is_theme(move):
            move.add_theme(self.theme)
            return self.theme

    def is_theme(self, move: Move.Move) -> bool:
        pass

    @staticmethod
    def is_best_move(mrm: EngineResponse.MultiEngineResponse, rm: EngineResponse.EngineResponse, pos_rm: int) -> bool:
        if pos_rm:
            rm_best = mrm.best_rm_ordered()
            if rm_best.centipawns_abs() > rm.centipawns_abs():
                return False
        return True

    @staticmethod
    def is_lost(rm: EngineResponse.EngineResponse) -> bool:
        if rm.centipawns_abs() < -100:
            return True
        return False

    @staticmethod
    def pz_value(pz) -> int:
        return PZ_VALUES[pz.upper()]

    @staticmethod
    def cr_col_row(cr) -> tuple:
        pos = FasterCode.a1_pos(cr)
        row, col = FasterCode.pos_rc(pos)
        return col, row

    @staticmethod
    def col_row_cr(col, row) -> str:
        return FasterCode.pos_a1(FasterCode.rc_pos(row, col))

    @staticmethod
    def squares_round(cr) -> list:
        pos = FasterCode.a1_pos(cr)
        row, col = FasterCode.pos_rc(pos)
        li = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                xrow = row + dr
                xcol = col + dc
                if 0 <= xrow < 8 and 0 <= xcol < 8:
                    li.append(FasterCode.pos_a1(FasterCode.rc_pos(xrow, xcol)))
        return li
