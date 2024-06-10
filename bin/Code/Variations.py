from Code import ManagerVariations
from Code.Base import Game


def edit_variation(procesador, game, titulo=None, with_engine_active=False, is_competitive=False, is_white_bottom=None,
                   go_to_move=None):
    window = procesador.main_window
    xtutor = procesador.XTutor()
    procesador_variations = procesador.clonVariations(window, xtutor, is_competitive=is_competitive)

    manager_variations = ManagerVariations.ManagerVariations(procesador_variations)
    manager_variations.start(game, is_white_bottom, with_engine_active, is_competitive, go_to_move)
    procesador_variations.manager = manager_variations

    if titulo is None:
        titulo = game.pgn_base_raw()

    procesador_variations.main_window.show_variations(titulo)

    return manager_variations.valor()


def edit_variation_moves(procesador, window, is_white_bottom, fen, linea_pgn, titulo=None):
    game = Game.fen_game(fen, linea_pgn)
    xtutor = procesador.XTutor()
    procesador_variations = procesador.clonVariations(window, xtutor, is_competitive=False)

    manager_variations = ManagerVariations.ManagerVariations(procesador_variations)
    manager_variations.start(game, is_white_bottom, False, False)
    procesador_variations.manager = manager_variations

    if titulo is None:
        titulo = game.pgn_base_raw()

    procesador_variations.main_window.show_variations(titulo)

    return manager_variations.valor()
