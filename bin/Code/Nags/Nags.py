import collections
import os

import Code
from Code.Base.Constantes import (
    dicHTMLnags,
)
from Code.QT import QTVarios


class Nags:
    def __init__(self):
        self.dic_standard = dic_nags()
        del self.dic_standard[0]
        self.li_nags = list(self.dic_standard)
        self.li_nags.sort()

    @staticmethod
    def ico(num_nag, tam):
        path = Code.path_resource("IntFiles", "NAGs", "$%d.svg" % num_nag)
        return QTVarios.fsvg2ico(path, tam)

    @staticmethod
    def dic_pm():
        dic = {}
        path = Code.path_resource("IntFiles", "NAGs")
        svg2pm = QTVarios.fsvg2pm
        entry: os.DirEntry
        for entry in os.scandir(path):
            name = entry.name
            if name.startswith("$"):
                num, ext = name[1:].split(".")
                dic[num] = svg2pm(entry.path, 16)
        return dic

    def __len__(self):
        return len(self.dic_standard)

    def __getitem__(self, item):
        return self.li_nags[item]

    def title(self, nag):
        return self.dic_standard[nag]

    def str_move(self, move):
        if not move:
            return ""
        li = move.li_nags
        if not li:
            return ""
        li_resp = []
        for nag in li:
            if nag in dicHTMLnags:
                resp = dicHTMLnags[nag]
            else:
                resp = "$%d" % nag
            resp += " %s" % self.dic_standard.get(nag, "")
            li_resp.append(resp)
        return "\n".join(li_resp)


def dic_nags():
    lista = (
        "",
        _("Good move"),
        _("Mistake"),
        _("Brilliant move"),
        _("Blunder"),
        _("Interesting move"),
        _("Dubious move"),
        _("Forced move (all others lose quickly)"),
        _("Singular move (no reasonable alternatives)"),
        _("Worst move"),
        _("Drawish position"),
        _("Equal chances, quiet position"),
        _("Equal chances, active position"),
        _("Unclear position"),
        _("White has a slight advantage"),
        _("Black has a slight advantage"),
        _("White has a moderate advantage"),
        _("Black has a moderate advantage"),
        _("White has a decisive advantage"),
        _("Black has a decisive advantage"),
        _("White has a crushing advantage (Black should resign)"),
        _("Black has a crushing advantage (White should resign)"),
        _("White is in zugzwang"),
        _("Black is in zugzwang"),
        _("White has a slight space advantage"),
        _("Black has a slight space advantage"),
        _("White has a moderate space advantage"),
        _("Black has a moderate space advantage"),
        _("White has a decisive space advantage"),
        _("Black has a decisive space advantage"),
        _("White has a slight time (development) advantage"),
        _("Black has a slight time (development) advantage"),
        _("White has a moderate time (development) advantage"),
        _("Black has a moderate time (development) advantage"),
        _("White has a decisive time (development) advantage"),
        _("Black has a decisive time (development) advantage"),
        _("White has the initiative"),
        _("Black has the initiative"),
        _("White has a lasting initiative"),
        _("Black has a lasting initiative"),
        _("White has the attack"),
        _("Black has the attack"),
        _("White has insufficient compensation for material deficit"),
        _("Black has insufficient compensation for material deficit"),
        _("White has sufficient compensation for material deficit"),
        _("Black has sufficient compensation for material deficit"),
        _("White has more than adequate compensation for material deficit"),
        _("Black has more than adequate compensation for material deficit"),
        _("White has a slight center control advantage"),
        _("Black has a slight center control advantage"),
        _("White has a moderate center control advantage"),
        _("Black has a moderate center control advantage"),
        _("White has a decisive center control advantage"),
        _("Black has a decisive center control advantage"),
        _("White has a slight kingside control advantage"),
        _("Black has a slight kingside control advantage"),
        _("White has a moderate kingside control advantage"),
        _("Black has a moderate kingside control advantage"),
        _("White has a decisive kingside control advantage"),
        _("Black has a decisive kingside control advantage"),
        _("White has a slight queenside control advantage"),
        _("Black has a slight queenside control advantage"),
        _("White has a moderate queenside control advantage"),
        _("Black has a moderate queenside control advantage"),
        _("White has a decisive queenside control advantage"),
        _("Black has a decisive queenside control advantage"),
        _("White has a vulnerable first rank"),
        _("Black has a vulnerable first rank"),
        _("White has a well protected first rank"),
        _("Black has a well protected first rank"),
        _("White has a poorly protected king"),
        _("Black has a poorly protected king"),
        _("White has a well protected king"),
        _("Black has a well protected king"),
        _("White has a poorly placed king"),
        _("Black has a poorly placed king"),
        _("White has a well placed king"),
        _("Black has a well placed king"),
        _("White has a very weak pawn structure"),
        _("Black has a very weak pawn structure"),
        _("White has a moderately weak pawn structure"),
        _("Black has a moderately weak pawn structure"),
        _("White has a moderately strong pawn structure"),
        _("Black has a moderately strong pawn structure"),
        _("White has a very strong pawn structure"),
        _("Black has a very strong pawn structure"),
        _("White has poor knight placement"),
        _("Black has poor knight placement"),
        _("White has good knight placement"),
        _("Black has good knight placement"),
        _("White has poor bishop placement"),
        _("Black has poor bishop placement"),
        _("White has good bishop placement"),
        _("Black has good bishop placement"),
        _("White has poor rook placement"),
        _("Black has poor rook placement"),
        _("White has good rook placement"),
        _("Black has good rook placement"),
        _("White has poor queen placement"),
        _("Black has poor queen placement"),
        _("White has good queen placement"),
        _("Black has good queen placement"),
        _("White has poor piece coordination"),
        _("Black has poor piece coordination"),
        _("White has good piece coordination"),
        _("Black has good piece coordination"),
        _("White has played the opening very poorly"),
        _("Black has played the opening very poorly"),
        _("White has played the opening poorly"),
        _("Black has played the opening poorly"),
        _("White has played the opening well"),
        _("Black has played the opening well"),
        _("White has played the opening very well"),
        _("Black has played the opening very well"),
        _("White has played the middlegame very poorly"),
        _("Black has played the middlegame very poorly"),
        _("White has played the middlegame poorly"),
        _("Black has played the middlegame poorly"),
        _("White has played the middlegame well"),
        _("Black has played the middlegame well"),
        _("White has played the middlegame very well"),
        _("Black has played the middlegame very well"),
        _("White has played the ending very poorly"),
        _("Black has played the ending very poorly"),
        _("White has played the ending poorly"),
        _("Black has played the ending poorly"),
        _("White has played the ending well"),
        _("Black has played the ending well"),
        _("White has played the ending very well"),
        _("Black has played the ending very well"),
        _("White has slight counterplay"),
        _("Black has slight counterplay"),
        _("White has moderate counterplay"),
        _("Black has moderate counterplay"),
        _("White has decisive counterplay"),
        _("Black has decisive counterplay"),
        _("White has moderate time control pressure"),
        _("Black has moderate time control pressure"),
        _("White has severe time control pressure"),
        _("Black has severe time control pressure"),
    )
    dic_nag = collections.OrderedDict()
    for n, x in enumerate(lista):
        dic_nag[n] = x

    for n, x in (
        (150, _("Diagonal")),
        (151, _("Bishops of light squares")),
        (153, _("Bishops of opposite color")),
        (154, _("Bishops of dark squares")),
        (155, _("Pawn duo")),
        (157, _("Pawn islands")),
        (159, _("Doubled pawns")),
        (163, _("Pawn majority")),
    ):
        dic_nag[n] = x

    return dic_nag
