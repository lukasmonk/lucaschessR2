import Code


class Themes:
    def __init__(self):
        self.dic_standard = {
            "advancedPawn": _("Advanced pawn"),
            "attraction": _("Attraction"),
            "backRankMate": _("Back rank mate"),
            "boardVision": _("Board vision"),
            "capturingDefender": _("Capture the defender"),
            "checkMateThreat": _("Checkmate threat"),
            "clearance": _("Clearance"),
            "decoy": _("Decoy"),
            "defensiveMove": _("Defensive move"),
            "deflection": _("Deflection"),
            "desperado": _("Desperado"),
            "discoveredAttack": _("Discovered attack"),
            "doubledPawns": _("Doubled pawns"),
            "doubleCheck": _("Double check"),
            "exposedKing": _("Exposed king"),
            "exchange": _("Exchange"),
            "forcedMove": _("Forced Move"),
            "fork": _("Fork / Double attack"),
            "hangingPiece": _("Hanging piece"),
            "interference": _("Interference"),
            "isolatedPawn": _("Isolated pawn"),
            "openFile": _("Open file ||Tactic theme"),
            "overload": _("Overload"),
            "outpost": _("Outpost"),
            "passedPawn": _("Passed pawn"),
            "pin": _("Pin"),
            "promotion": _("Promotion"),
            "quietMove": _("Quiet move"),
            "sacrifice": _("Sacrifice"),
            "semiProtectedPiece": _("Semi-protected piece"),
            "simplification": _("Simplification"),
            "skewer": _("Skewer"),
            "speculation": _("Speculation"),
            "tempo": _("Tempo"),
            "threat": _("Threat"),
            "trappedPiece": _("Trapped piece"),
            "underPromotion": _("Underpromotion"),
            "weakSquare": _("Weak square"),
            "unsafeSquare": _("Unsafe square"),
            "xRayAttack": _("X-Ray attack"),
            "zwischenzug": _("Zwischenzug"),
            "zugzwang": _("Zugzwang"),
            "advantage": _("Advantage"),
            "anastasiaMate": _("Anastasia's mate"),
            "arabianMate": _("Arabian mate"),
            "bodenMate": _("Boden's mate"),
            "coercion": _("Coercion"),
            "crushing": _("Crushing"),
            "doubleBishopMate": _("Double bishop mate"),
            "dovetailMate": _("Dovetail mate"),
            "hookMate": _("Hook mate"),
            "kingsideAttack": _("King side attack"),
            "queensideAttack": _("Queen side attack"),
            "smotheredMate": _("Smothered mate"),
        }

        self.li_custom = []
        self.li_head = []
        self.li_themes = []
        self.read()
        self.build()

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

    def write(self):
        self.li_head = [theme for theme in self.li_head if theme in self.li_custom or theme in self.dic_standard]
        dic = {"HEAD": self.li_head, "CUSTOM": self.li_custom}
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
