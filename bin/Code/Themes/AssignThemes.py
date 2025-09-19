import Code
from Code.Base import Game, Move
from Code.Base.Constantes import TACTICTHEMES
from Code.Engines import EngineResponse
from Code.Themes import Th_Attraction, Th_Deflection, Th_Decoy
from Code.Themes import Th_BackRankMate, Th_AnastasiaMate, Th_BodenMate, Th_ArabianMate
from Code.Themes import Th_KillBoxMate
from Code.Themes import Th_Pin, Th_UnderPromotion, Th_Skewer, Th_DoubleCheck
from Code.Themes import Th_SmotheredMate, Th_DovetailMate, Th_HookMate, Th_VukovicMate


class AssignThemes:
    def __init__(self):
        self.li_themes_run = [# Th_AdvancedPawn.AdvancedPawn(),
            Th_Deflection.Deflection(), Th_Decoy.Decoy(), Th_Attraction.Attraction(), Th_Pin.Pin(),
            Th_UnderPromotion.UnderPromotion(), Th_Skewer.Skewer(), Th_DoubleCheck.DoubleCheck(), ]
        self.li_themes_mate_run = [Th_AnastasiaMate.AnastasiaMate(), Th_BodenMate.BodenMate(),
            Th_ArabianMate.ArabianMate(), Th_SmotheredMate.SmotheredMate(), Th_DovetailMate.DovetailMate(),
            Th_HookMate.HookMate(), Th_VukovicMate.VukovicMate(), Th_KillBoxMate.KillBoxMate(),
            Th_BackRankMate.BackRankMate(), ]
        # self.li_themes_run = [
        #     Th_Deflection.Deflection(),
        # ]
        # self.li_themes_mate_run = [
        # ]

        self.all_themes = self.list_themes()

    def list_themes(self):
        li = []
        for chk_theme in self.li_themes_run:
            li.append(chk_theme.theme)
        for chk_theme in self.li_themes_mate_run:
            li.append(chk_theme.theme)
        return li

    def liblk80_themes(self, st_themes=None):
        themes = Code.get_themes()
        li = []
        tam = 0
        maxim = 74
        li_blk80 = []
        for key in self.list_themes():
            if st_themes and key not in st_themes:
                continue
            txt = themes.dic_standard[key]
            tam += len(txt) + 2
            if tam >= maxim:
                li_blk80.append(", ".join(li))
                li = [txt]
                tam = len(txt) + 2
            else:
                li.append(txt)
        if li:
            li_blk80.append(", ".join(li))
        return li_blk80

    def txt_all_themes(self, st_themes=None):
        themes = Code.get_themes()
        li = []
        for key in self.list_themes():
            if st_themes and key not in st_themes:
                continue
            txt = themes.dic_standard[key]
            li.append(txt)
        return ", ".join(li)

    def assign_game(self, game: Game.Game, with_tags: bool, reset: bool):
        move: Move.Move
        li_themes = []
        for move in game.li_moves:
            if reset and move.has_themes():
                move.clear_themes(self.all_themes)
            if move.in_the_opening:
                continue
            if move.analysis is None:
                continue
            for theme_run in self.li_themes_run:
                theme_run.check_move(move)

        st_themes = set()
        for move in game.li_moves:
            if move.analysis is None:
                continue
            mrm: EngineResponse.MultiEngineResponse
            pos: int
            mrm, pos = move.analysis
            rm: EngineResponse.EngineResponse = mrm.li_rm[pos]
            if rm.mate:
                for theme_run in self.li_themes_mate_run:
                    theme = theme_run.check_move(move)
                    if theme:
                        if theme in st_themes:
                            move.rem_theme(theme)
                        else:
                            st_themes.add(theme)
            elif st_themes:  # Si hay un corte saliendo del mate, vuelven a valer todos los mates
                st_themes = set()

            li_th_move = move.get_themes()
            if li_th_move:
                li_themes.extend(li_th_move)
        if with_tags:
            if li_themes:
                game.set_tag(TACTICTHEMES, ",".join(list(dict.fromkeys(li_themes))))
            else:
                game.del_tag(TACTICTHEMES)
