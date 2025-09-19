import collections

from PySide2 import QtGui

import Code
from Code.Base.Constantes import NO_RATING, GOOD_MOVE, MISTAKE, VERY_GOOD_MOVE, BLUNDER, INTERESTING_MOVE, INACCURACY

NAG_0, NAG_1, NAG_2, NAG_3, NAG_4, NAG_5, NAG_6 = (
    NO_RATING,
    GOOD_MOVE,
    MISTAKE,
    VERY_GOOD_MOVE,
    BLUNDER,
    INTERESTING_MOVE,
    INACCURACY,
)


class Nag:
    def __init__(self, number, text, symbol):
        self.number = number
        self.text = text
        self.symbol = symbol


def dic_nags():
    lista = (
        Nag(NAG_1, _("Good move"), "!"),
        Nag(NAG_2, _("Mistake"), "?"),
        Nag(NAG_3, _("Brilliant move"), "‼"),
        Nag(NAG_4, _("Blunder"), "⁇"),
        Nag(NAG_5, _("Interesting move"), "⁉"),
        Nag(NAG_6, _("Dubious move"), "⁈"),
        Nag(7, _("Forced move (all others lose quickly)"), "□"),
        Nag(8, _("Singular move (no reasonable alternatives)"), ""),
        Nag(9, _("Worst move"), ""),
        Nag(10, _("Drawish position"), "="),
        Nag(11, _("Equal chances, quiet position"), ""),
        Nag(12, _("Equal chances, active position"), ""),
        Nag(13, _("Unclear position"), "∞"),
        Nag(14, _("White has a slight advantage"), "⩲"),
        Nag(15, _("Black has a slight advantage"), "⩱"),
        Nag(16, _("White has a moderate advantage"), "±"),
        Nag(17, _("Black has a moderate advantage"), "∓"),
        Nag(18, _("White has a decisive advantage"), "+-"),
        Nag(19, _("Black has a decisive advantage"), "-+"),
        Nag(20, _("White has a crushing advantage (Black should resign)"), ""),
        Nag(21, _("Black has a crushing advantage (White should resign)"), ""),
        Nag(22, _("White is in zugzwang"), "⨀"),
        Nag(23, _("Black is in zugzwang"), "⨀"),
        Nag(24, _("White has a slight space advantage"), ""),
        Nag(25, _("Black has a slight space advantage"), ""),
        Nag(26, _("White has a moderate space advantage"), "○"),
        Nag(27, _("Black has a moderate space advantage"), "○"),
        Nag(28, _("White has a decisive space advantage"), ""),
        Nag(29, _("Black has a decisive space advantage"), ""),
        Nag(30, _("White has a slight time (development) advantage"), ""),
        Nag(31, _("Black has a slight time (development) advantage"), ""),
        Nag(32, _("White has a moderate time (development) advantage"), "⟳"),
        Nag(33, _("Black has a moderate time (development) advantage"), "⟳"),
        Nag(34, _("White has a decisive time (development) advantage"), ""),
        Nag(35, _("Black has a decisive time (development) advantage"), ""),
        Nag(36, _("White has the initiative"), "↑"),
        Nag(37, _("Black has the initiative"), "↑"),
        Nag(38, _("White has a lasting initiative"), ""),
        Nag(39, _("Black has a lasting initiative"), ""),
        Nag(40, _("White has the attack"), "→"),
        Nag(41, _("Black has the attack"), "→"),
        Nag(42, _("White has insufficient compensation for material deficit"), ""),
        Nag(43, _("Black has insufficient compensation for material deficit"), ""),
        Nag(44, _("White has sufficient compensation for material deficit"), ""),
        Nag(45, _("Black has sufficient compensation for material deficit"), ""),
        Nag(46, _("White has more than adequate compensation for material deficit"), ""),
        Nag(47, _("Black has more than adequate compensation for material deficit"), ""),
        Nag(48, _("White has a slight center control advantage"), ""),
        Nag(49, _("Black has a slight center control advantage"), ""),
        Nag(50, _("White has a moderate center control advantage"), ""),
        Nag(51, _("Black has a moderate center control advantage"), ""),
        Nag(52, _("White has a decisive center control advantage"), ""),
        Nag(53, _("Black has a decisive center control advantage"), ""),
        Nag(54, _("White has a slight kingside control advantage"), ""),
        Nag(55, _("Black has a slight kingside control advantage"), ""),
        Nag(56, _("White has a moderate kingside control advantage"), ""),
        Nag(57, _("Black has a moderate kingside control advantage"), ""),
        Nag(58, _("White has a decisive kingside control advantage"), ""),
        Nag(59, _("Black has a decisive kingside control advantage"), ""),
        Nag(60, _("White has a slight queenside control advantage"), ""),
        Nag(61, _("Black has a slight queenside control advantage"), ""),
        Nag(62, _("White has a moderate queenside control advantage"), ""),
        Nag(63, _("Black has a moderate queenside control advantage"), ""),
        Nag(64, _("White has a decisive queenside control advantage"), ""),
        Nag(65, _("Black has a decisive queenside control advantage"), ""),
        Nag(66, _("White has a vulnerable first rank"), ""),
        Nag(67, _("Black has a vulnerable first rank"), ""),
        Nag(68, _("White has a well protected first rank"), ""),
        Nag(69, _("Black has a well protected first rank"), ""),
        Nag(70, _("White has a poorly protected king"), ""),
        Nag(71, _("Black has a poorly protected king"), ""),
        Nag(72, _("White has a well protected king"), ""),
        Nag(73, _("Black has a well protected king"), ""),
        Nag(74, _("White has a poorly placed king"), ""),
        Nag(75, _("Black has a poorly placed king"), ""),
        Nag(76, _("White has a well placed king"), ""),
        Nag(77, _("Black has a well placed king"), ""),
        Nag(78, _("White has a very weak pawn structure"), ""),
        Nag(79, _("Black has a very weak pawn structure"), ""),
        Nag(80, _("White has a moderately weak pawn structure"), ""),
        Nag(81, _("Black has a moderately weak pawn structure"), ""),
        Nag(82, _("White has a moderately strong pawn structure"), ""),
        Nag(83, _("Black has a moderately strong pawn structure"), ""),
        Nag(84, _("White has a very strong pawn structure"), ""),
        Nag(85, _("Black has a very strong pawn structure"), ""),
        Nag(86, _("White has poor knight placement"), ""),
        Nag(87, _("Black has poor knight placement"), ""),
        Nag(88, _("White has good knight placement"), ""),
        Nag(89, _("Black has good knight placement"), ""),
        Nag(90, _("White has poor bishop placement"), ""),
        Nag(91, _("Black has poor bishop placement"), ""),
        Nag(92, _("White has good bishop placement"), ""),
        Nag(93, _("Black has good bishop placement"), ""),
        Nag(94, _("White has poor rook placement"), ""),
        Nag(95, _("Black has poor rook placement"), ""),
        Nag(96, _("White has good rook placement"), ""),
        Nag(97, _("Black has good rook placement"), ""),
        Nag(98, _("White has poor queen placement"), ""),
        Nag(99, _("Black has poor queen placement"), ""),
        Nag(100, _("White has good queen placement"), ""),
        Nag(101, _("Black has good queen placement"), ""),
        Nag(102, _("White has poor piece coordination"), ""),
        Nag(103, _("Black has poor piece coordination"), ""),
        Nag(104, _("White has good piece coordination"), ""),
        Nag(105, _("Black has good piece coordination"), ""),
        Nag(106, _("White has played the opening very poorly"), ""),
        Nag(107, _("Black has played the opening very poorly"), ""),
        Nag(108, _("White has played the opening poorly"), ""),
        Nag(109, _("Black has played the opening poorly"), ""),
        Nag(110, _("White has played the opening well"), ""),
        Nag(111, _("Black has played the opening well"), ""),
        Nag(112, _("White has played the opening very well"), ""),
        Nag(113, _("Black has played the opening very well"), ""),
        Nag(114, _("White has played the middlegame very poorly"), ""),
        Nag(115, _("Black has played the middlegame very poorly"), ""),
        Nag(116, _("White has played the middlegame poorly"), ""),
        Nag(117, _("Black has played the middlegame poorly"), ""),
        Nag(118, _("White has played the middlegame well"), ""),
        Nag(119, _("Black has played the middlegame well"), ""),
        Nag(120, _("White has played the middlegame very well"), ""),
        Nag(121, _("Black has played the middlegame very well"), ""),
        Nag(122, _("White has played the ending very poorly"), ""),
        Nag(123, _("Black has played the ending very poorly"), ""),
        Nag(124, _("White has played the ending poorly"), ""),
        Nag(125, _("Black has played the ending poorly"), ""),
        Nag(126, _("White has played the ending well"), ""),
        Nag(127, _("Black has played the ending well"), ""),
        Nag(128, _("White has played the ending very well"), ""),
        Nag(129, _("Black has played the ending very well"), ""),
        Nag(130, _("White has slight counterplay"), ""),
        Nag(131, _("Black has slight counterplay"), ""),
        Nag(132, _("White has moderate counterplay"), "⇆"),
        Nag(133, _("Black has moderate counterplay"), "⇆"),
        Nag(134, _("White has decisive counterplay"), ""),
        Nag(135, _("Black has decisive counterplay"), ""),
        Nag(136, _("White has moderate time control pressure"), ""),
        Nag(137, _("Black has moderate time control pressure"), ""),
        Nag(138, _("White has severe time control pressure"), "⨁"),
        Nag(139, _("Black has severe time control pressure"), "⨁"),
        Nag(150, _("Diagonal"), ""),
        Nag(151, _("Bishops of light squares"), ""),
        Nag(153, _("Bishops of opposite color"), ""),
        Nag(154, _("Bishops of dark squares"), ""),
        Nag(155, _("Pawn duo"), ""),
        Nag(157, _("Pawn islands"), ""),
        Nag(159, _("Doubled pawns"), ""),
        Nag(163, _("Pawn majority"), ""),
    )
    dic_nag = collections.OrderedDict()
    for nag in lista:
        dic_nag[nag.number] = nag

    return dic_nag


class Nags:
    def __init__(self):
        self.dic_standard = dic_nags()
        self.li_nags = list(self.dic_standard.keys())
        self.li_nags.sort()

    def __len__(self):
        return len(self.li_nags)

    def __getitem__(self, item):
        return self.li_nags[item]

    def title(self, nag):
        return self.dic_standard[nag].text

    def symbol(self, nag):
        return self.dic_standard[nag].symbol

    def str_move(self, move):
        if not move:
            return ""
        li = move.li_nags
        if not li:
            return ""
        li_resp = []
        for num_nag in li:
            symbol = self.dic_standard[num_nag].symbol if num_nag in self.dic_standard else ""
            resp = symbol if symbol else "$%d" % num_nag
            text = self.dic_standard[num_nag].text if num_nag in self.dic_standard else ""
            resp += " %s" % text
            li_resp.append(resp)
        return "\n".join(li_resp)


xdic_nags = {}
xdic_colors = {}


def dic_symbol_nags(num_nag):
    global xdic_nags
    if not xdic_nags:
        xdic_nags = dic_nags()
    return xdic_nags[num_nag].symbol if num_nag in xdic_nags else ""


def dic_text_nags(num_nag):
    global xdic_nags
    if not xdic_nags:
        xdic_nags = dic_nags()
    return xdic_nags[num_nag].text if num_nag in xdic_nags else ""


def nag_color(num_nag):
    global xdic_colors
    if not xdic_colors:
        xdic_colors[GOOD_MOVE] = Code.dic_colors["GOOD_MOVE"]
        xdic_colors[MISTAKE] = Code.dic_colors["MISTAKE"]
        xdic_colors[VERY_GOOD_MOVE] = Code.dic_colors["VERY_GOOD_MOVE"]
        xdic_colors[BLUNDER] = Code.dic_colors["BLUNDER"]
        xdic_colors[INTERESTING_MOVE] = Code.dic_colors["INTERESTING_MOVE"]
        xdic_colors[INACCURACY] = Code.dic_colors["INACCURACY"]
    return xdic_colors.get(num_nag)


def nag_less_color(num_nag, opacity):
    qcolor = QtGui.QColor(nag_color(num_nag))

    # Obtener valores RGB + alpha (por defecto 255 = opaco)
    r = int(qcolor.red() * opacity) % 255
    g = int(qcolor.green() * opacity) % 255
    b = int(qcolor.blue() * opacity) % 255

    return f"rgb({r}, {g}, {b})"


def nag_qcolor(num_nag):
    if NAG_0 < num_nag <= NAG_6:
        return QtGui.QColor(nag_color(num_nag))
    return None


def html_nag_txt(nag):
    dic_htm_lnags_txt = {NAG_1: "!", NAG_2: "?", NAG_3: "!!", NAG_4: "??", NAG_5: "!?", NAG_6: "?!"}
    return dic_htm_lnags_txt.get(nag, "$%d" % nag)


def html_nag_symbol(nag):
    # dic_htm_lnags_txt = {NAG_1: "!", NAG_2: "?", NAG_3: "!!", NAG_4: "??", NAG_5: "!?", NAG_6: "?!"}
    symbol = dic_symbol_nags(nag)
    return symbol if symbol else "$%d" % nag
