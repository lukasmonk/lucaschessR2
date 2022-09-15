from typing import List

import chess
from chess import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
from chess import WHITE, BLACK
from chess import square_rank, square_file, Board, SquareSet, Piece, PieceType, square_distance
from chess.pgn import ChildNode

from Code.Themes.Lichess import util
from Code.Themes.Lichess.model import Puzzle, TagKind
from Code.Themes.Lichess.util import material_diff


def cook(puzzle: Puzzle):
    tags: List[TagKind] = []

    mate_tag = mate_in(puzzle)
    if mate_tag:
        tags.append(mate_tag)
        tags.append("mate")
        if smothered_mate(puzzle):
            tags.append("smotheredMate")
        elif back_rank_mate(puzzle):
            tags.append("backRankMate")
        elif anastasia_mate(puzzle):
            tags.append("anastasiaMate")
        elif hook_mate(puzzle):
            tags.append("hookMate")
        elif arabian_mate(puzzle):
            tags.append("arabianMate")
        else:
            found = boden_or_double_bishop_mate(puzzle)
            if found:
                tags.append(found)
            elif dovetail_mate(puzzle):
                tags.append("dovetailMate")
    elif puzzle.cp > 600:
        tags.append("crushing")
    elif puzzle.cp > 200:
        tags.append("advantage")
    else:
        tags.append("equality")

    if attraction(puzzle):
        tags.append("attraction")

    if deflection(puzzle):
        tags.append("deflection")
    elif overloading(puzzle):
        tags.append("overload")

    if advanced_pawn(puzzle):
        tags.append("advancedPawn")

    if double_check(puzzle):
        tags.append("doubleCheck")

    if quiet_move(puzzle):
        tags.append("quietMove")

    if defensive_move(puzzle) or check_escape(puzzle):
        tags.append("defensiveMove")

    if sacrifice(puzzle):
        tags.append("sacrifice")

    if x_ray(puzzle):
        tags.append("xRayAttack")

    if fork(puzzle):
        tags.append("fork")

    if hanging_piece(puzzle):
        tags.append("hangingPiece")

    if trapped_piece(puzzle):
        tags.append("trappedPiece")

    if discovered_attack(puzzle):
        tags.append("discoveredAttack")

    if exposed_king(puzzle):
        tags.append("exposedKing")

    if skewer(puzzle):
        tags.append("skewer")

    if self_interference(puzzle) or interference(puzzle):
        tags.append("interference")

    if intermezzo(puzzle):
        tags.append("intermezzo")

    if pin_prevents_attack(puzzle) or pin_prevents_escape(puzzle):
        tags.append("pin")

    if attacking_f2_f7(puzzle):
        tags.append("attackingF2F7")

    if clearance(puzzle):
        tags.append("clearance")

    if en_passant(puzzle):
        tags.append("enPassant")

    if castling(puzzle):
        tags.append("castling")

    if promotion(puzzle):
        tags.append("promotion")
        if under_promotion(puzzle):
            tags.append("underPromotion")

    if capturing_defender(puzzle):
        tags.append("capturingDefender")

    if piece_endgame(puzzle, PAWN):
        tags.append("pawnEndgame")
    elif piece_endgame(puzzle, QUEEN):
        tags.append("queenEndgame")
    elif piece_endgame(puzzle, ROOK):
        tags.append("rookEndgame")
    elif piece_endgame(puzzle, BISHOP):
        tags.append("bishopEndgame")
    elif piece_endgame(puzzle, KNIGHT):
        tags.append("knightEndgame")
    elif queen_rook_endgame(puzzle):
        tags.append("queenRookEndgame")

    if "backRankMate" not in tags and "fork" not in tags:
        if kingside_attack(puzzle):
            tags.append("kingsideAttack")
        elif queenside_attack(puzzle):
            tags.append("queensideAttack")

    if len(puzzle.mainline) == 2:
        tags.append("oneMove")
    elif len(puzzle.mainline) == 4:
        tags.append("short")
    elif len(puzzle.mainline) >= 8:
        tags.append("veryLong")
    else:
        tags.append("long")

    return tags


def advanced_pawn(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        if util.is_very_advanced_pawn_move(node):
            return True
    return False


def double_check(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        if len(node.board().checkers()) > 1:
            return True
    return False


def sacrifice(puzzle: Puzzle) -> bool:
    # down in material compared to initial position, after moving
    diffs = [material_diff(n.board(), puzzle.pov) for n in puzzle.mainline]
    initial = diffs[0]
    for d in diffs[1::2][1:]:
        if d - initial <= -2:
            return not any(n.move.promotion for n in puzzle.mainline[::2][1:])
    return False


def x_ray(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2][1:]:
        if not util.is_capture(node):
            continue
        prev_op_node = node.parent
        assert isinstance(prev_op_node, ChildNode)
        if prev_op_node.move.to_square != node.move.to_square or util.moved_piece_type(prev_op_node) == KING:
            continue
        prev_pl_node = prev_op_node.parent
        assert isinstance(prev_pl_node, ChildNode)
        if prev_pl_node.move.to_square != prev_op_node.move.to_square:
            continue
        if prev_op_node.move.from_square in SquareSet.between(node.move.from_square, node.move.to_square):
            return True

    return False


def fork(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2][:-1]:
        if util.moved_piece_type(node) is not KING:
            board = node.board()
            if util.is_in_bad_spot(board, node.move.to_square):
                continue
            nb = 0
            for (piece, square) in util.attacked_opponent_squares(board, node.move.to_square, puzzle.pov):
                if piece.piece_type == PAWN:
                    continue
                if util.king_values[piece.piece_type] > util.king_values[util.moved_piece_type(node)] or (
                    util.is_hanging(board, piece, square)
                    and square not in board.attackers(not puzzle.pov, node.move.to_square)
                ):
                    nb += 1
            if nb > 1:
                return True
    return False


def hanging_piece(puzzle: Puzzle) -> bool:
    to = puzzle.mainline[1].move.to_square
    captured = puzzle.mainline[0].board().piece_at(to)
    if puzzle.mainline[0].board().is_check() and (not captured or captured.piece_type == PAWN):
        return False
    if captured and captured.piece_type != PAWN:
        if util.is_hanging(puzzle.mainline[0].board(), captured, to):
            op_move = puzzle.mainline[0].move
            op_capture = puzzle.game.board().piece_at(op_move.to_square)
            if (
                op_capture
                and util.values[op_capture.piece_type] >= util.values[captured.piece_type]
                and op_move.to_square == to
            ):
                return False
            if len(puzzle.mainline) < 4:
                return True
            if material_diff(puzzle.mainline[3].board(), puzzle.pov) >= material_diff(
                puzzle.mainline[1].board(), puzzle.pov
            ):
                return True
    return False


def trapped_piece(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2][1:]:
        square = node.move.to_square
        captured = node.parent.board().piece_at(square)
        if captured and captured.piece_type != PAWN:
            prev = node.parent
            assert isinstance(prev, ChildNode)
            if prev.move.to_square == square:
                square = prev.move.from_square
            if util.is_trapped(prev.parent.board(), square):
                return True
    return False


def overloading(puzzle: Puzzle) -> bool:
    return False


def discovered_attack(puzzle: Puzzle) -> bool:
    if discovered_check(puzzle):
        return True
    for node in puzzle.mainline[1::2][1:]:
        if util.is_capture(node):
            between = SquareSet.between(node.move.from_square, node.move.to_square)
            assert isinstance(node.parent, ChildNode)
            if node.parent.move.to_square == node.move.to_square:
                return False
            prev = node.parent.parent
            assert isinstance(prev, ChildNode)
            if (
                prev.move.from_square in between
                and node.move.to_square != prev.move.to_square
                and node.move.from_square != prev.move.to_square
                and not util.is_castling(prev)
            ):
                return True
    return False


def discovered_check(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        board = node.board()
        checkers = board.checkers()
        if checkers and node.move.to_square not in checkers:
            return True
    return False


def quiet_move(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline:
        if (
            # on player move, not the last move of the puzzle
            node.turn() != puzzle.pov
            and not node.is_end()
            and
            # no check given or escaped
            not node.board().is_check()
            and not node.parent.board().is_check()
            and
            # no capture made or threatened
            not util.is_capture(node)
            and not util.attacked_opponent_pieces(node.board(), node.move.to_square, puzzle.pov)
            and
            # no advanced pawn push
            not util.is_advanced_pawn_move(node)
            and util.moved_piece_type(node) != KING
        ):
            return True
    return False


def defensive_move(puzzle: Puzzle) -> bool:
    # like quiet_move, but on last move
    # at least 3 legal moves
    if puzzle.mainline[-2].board().legal_moves.count() < 3:
        return False
    node = puzzle.mainline[-1]
    # no check given, no piece taken
    if node.board().is_check() or util.is_capture(node):
        return False
    # no piece attacked
    if util.attacked_opponent_pieces(node.board(), node.move.to_square, puzzle.pov):
        return False
    # no advanced pawn push
    return not util.is_advanced_pawn_move(node)


def check_escape(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        if node.board().is_check() or util.is_capture(node):
            return False
        if node.parent.board().legal_moves.count() < 3:
            return False
        if node.parent.board().is_check():
            return True
    return False


def attraction(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1:]:
        if node.turn() == puzzle.pov:
            continue
        # 1. player moves to a square
        first_move_to = node.move.to_square
        opponent_reply = util.next_node(node)
        # 2. opponent captures on that square
        if opponent_reply and opponent_reply.move.to_square == first_move_to:
            attracted_piece = util.moved_piece_type(opponent_reply)
            if attracted_piece in [KING, QUEEN, ROOK]:
                attracted_to_square = opponent_reply.move.to_square
                next_node = util.next_node(opponent_reply)
                if next_node:
                    attackers = next_node.board().attackers(puzzle.pov, attracted_to_square)
                    # 3. player attacks that square
                    if next_node.move.to_square in attackers:
                        # 4. player checks on that square
                        if attracted_piece == KING:
                            return True
                        n3 = util.next_next_node(next_node)
                        # 4. or player later captures on that square
                        if n3 and n3.move.to_square == attracted_to_square:
                            return True
    return False


def deflection(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2][1:]:
        captured_piece = node.parent.board().piece_at(node.move.to_square)
        if captured_piece or node.move.promotion:
            capturing_piece = util.moved_piece_type(node)
            if captured_piece and util.king_values[captured_piece.piece_type] > util.king_values[capturing_piece]:
                continue
            square = node.move.to_square
            prev_op_move = node.parent.move
            assert prev_op_move
            grandpa = node.parent.parent
            assert isinstance(grandpa, ChildNode)
            prev_player_move = grandpa.move
            prev_player_capture = grandpa.parent.board().piece_at(prev_player_move.to_square)
            if (
                (
                    not prev_player_capture
                    or util.values[prev_player_capture.piece_type] < util.moved_piece_type(grandpa)
                )
                and square != prev_op_move.to_square
                and square != prev_player_move.to_square
                and (prev_op_move.to_square == prev_player_move.to_square or grandpa.board().is_check())
                and (
                    square in grandpa.board().attacks(prev_op_move.from_square)
                    or node.move.promotion
                    and square_file(node.move.to_square) == square_file(prev_op_move.from_square)
                    and node.move.from_square in grandpa.board().attacks(prev_op_move.from_square)
                )
                and (not square in node.parent.board().attacks(prev_op_move.to_square))
            ):
                return True
    return False


def exposed_king(puzzle: Puzzle) -> bool:
    if puzzle.pov:
        pov = puzzle.pov
        board = puzzle.mainline[0].board()
    else:
        pov = not puzzle.pov
        board = puzzle.mainline[0].board().mirror()
    king = board.king(not pov)
    assert king is not None
    if chess.square_rank(king) < 5:
        return False
    squares = SquareSet.from_square(king - 8)
    if chess.square_file(king) > 0:
        squares.add(king - 1)
        squares.add(king - 9)
    if chess.square_file(king) < 7:
        squares.add(king + 1)
        squares.add(king - 7)
    for square in squares:
        if board.piece_at(square) == Piece(PAWN, not pov):
            return False
    for node in puzzle.mainline[1::2][1:-1]:
        if node.board().is_check():
            return True
    return False


def skewer(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2][1:]:
        prev = node.parent
        assert isinstance(prev, ChildNode)
        capture = prev.board().piece_at(node.move.to_square)
        if capture and util.moved_piece_type(node) in util.ray_piece_types and not node.board().is_checkmate():
            between = SquareSet.between(node.move.from_square, node.move.to_square)
            op_move = prev.move
            assert op_move
            if op_move.to_square == node.move.to_square or not op_move.from_square in between:
                continue
            if util.king_values[util.moved_piece_type(prev)] > util.king_values[
                capture.piece_type
            ] and util.is_in_bad_spot(prev.board(), node.move.to_square):
                return True
    return False


def self_interference(puzzle: Puzzle) -> bool:
    # intereference by opponent piece
    for node in puzzle.mainline[1::2][1:]:
        prev_board = node.parent.board()
        square = node.move.to_square
        capture = prev_board.piece_at(square)
        if capture and util.is_hanging(prev_board, capture, square):
            grandpa = node.parent.parent
            assert grandpa
            init_board = grandpa.board()
            defenders = init_board.attackers(capture.color, square)
            defender = defenders.pop() if defenders else None
            defender_piece = init_board.piece_at(defender) if defender else None
            if defender and defender_piece and defender_piece.piece_type in util.ray_piece_types:
                if node.parent.move and node.parent.move.to_square in SquareSet.between(square, defender):
                    return True
    return False


def interference(puzzle: Puzzle) -> bool:
    # intereference by player piece
    for node in puzzle.mainline[1::2][1:]:
        prev_board = node.parent.board()
        square = node.move.to_square
        capture = prev_board.piece_at(square)
        assert node.parent.move
        if capture and square != node.parent.move.to_square and util.is_hanging(prev_board, capture, square):
            assert node.parent
            assert node.parent.parent
            assert node.parent.parent.parent
            init_board = node.parent.parent.parent.board()
            defenders = init_board.attackers(capture.color, square)
            defender = defenders.pop() if defenders else None
            defender_piece = init_board.piece_at(defender) if defender else None
            if defender and defender_piece and defender_piece.piece_type in util.ray_piece_types:
                interfering = node.parent.parent
                if interfering.move and interfering.move.to_square in SquareSet.between(square, defender):
                    return True
    return False


def intermezzo(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2][1:]:
        if util.is_capture(node):
            capture_move = node.move
            capture_square = node.move.to_square
            op_node = node.parent
            assert isinstance(op_node, ChildNode)
            prev_pov_node = node.parent.parent
            assert isinstance(prev_pov_node, ChildNode)
            if not op_node.move.from_square in prev_pov_node.board().attackers(not puzzle.pov, capture_square):
                if prev_pov_node.move.to_square != capture_square:
                    prev_op_node = prev_pov_node.parent
                    assert isinstance(prev_op_node, ChildNode)
                    return (
                        prev_op_node.move.to_square == capture_square
                        and util.is_capture(prev_op_node)
                        and capture_move in prev_op_node.board().legal_moves
                    )
    return False


# the pinned piece can't attack a player piece
def pin_prevents_attack(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        board = node.board()
        for square, piece in board.piece_map().items():
            if piece.color == puzzle.pov:
                continue
            pin_dir = board.pin(piece.color, square)
            if pin_dir == chess.BB_ALL:
                continue
            for attack in board.attacks(square):
                attacked = board.piece_at(attack)
                if (
                    attacked
                    and attacked.color == puzzle.pov
                    and not attack in pin_dir
                    and (
                        util.values[attacked.piece_type] > util.values[piece.piece_type]
                        or util.is_hanging(board, attacked, attack)
                    )
                ):
                    return True
    return False


# the pinned piece can't escape the attack
def pin_prevents_escape(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        board = node.board()
        for pinned_square, pinned_piece in board.piece_map().items():
            if pinned_piece.color == puzzle.pov:
                continue
            pin_dir = board.pin(pinned_piece.color, pinned_square)
            if pin_dir == chess.BB_ALL:
                continue
            for attacker_square in board.attackers(puzzle.pov, pinned_square):
                if attacker_square in pin_dir:
                    attacker = board.piece_at(attacker_square)
                    assert attacker
                    if util.values[pinned_piece.piece_type] > util.values[attacker.piece_type]:
                        return True
                    if (
                        util.is_hanging(board, pinned_piece, pinned_square)
                        and pinned_square not in board.attackers(not puzzle.pov, attacker_square)
                        and [
                            m
                            for m in board.pseudo_legal_moves
                            if m.from_square == pinned_square and m.to_square not in pin_dir
                        ]
                    ):
                        return True
    return False


def attacking_f2_f7(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        square = node.move.to_square
        if node.parent.board().piece_at(node.move.to_square) and square in [chess.F2, chess.F7]:
            king = node.board().piece_at(chess.E8 if square == chess.F7 else chess.E1)
            return king is not None and king.piece_type == KING and king.color != puzzle.pov
    return False


def kingside_attack(puzzle: Puzzle) -> bool:
    return side_attack(puzzle, 7, [6, 7], 20)


def queenside_attack(puzzle: Puzzle) -> bool:
    return side_attack(puzzle, 0, [0, 1, 2], 18)


def side_attack(puzzle: Puzzle, corner_file: int, king_files: List[int], nb_pieces: int) -> bool:
    back_rank = 7 if puzzle.pov else 0
    init_board = puzzle.mainline[0].board()
    king_square = init_board.king(not puzzle.pov)
    if (
        not king_square
        or square_rank(king_square) != back_rank
        or square_file(king_square) not in king_files
        or len(init_board.piece_map()) < nb_pieces
        or not any(node.board().is_check() for node in puzzle.mainline[1::2])  # no endgames
    ):
        return False
    score = 0
    corner = chess.square(corner_file, back_rank)
    for node in puzzle.mainline[1::2]:
        corner_dist = square_distance(corner, node.move.to_square)
        if node.board().is_check():
            score += 1
        if util.is_capture(node) and corner_dist <= 3:
            score += 1
        elif corner_dist >= 5:
            score -= 1
    return score >= 2


def clearance(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2][1:]:
        board = node.board()
        if not node.parent.board().piece_at(node.move.to_square):
            piece = board.piece_at(node.move.to_square)
            if piece and piece.piece_type in util.ray_piece_types:
                prev = node.parent.parent
                assert prev
                prev_move = prev.move
                assert prev_move
                assert isinstance(node.parent, ChildNode)
                if (
                    not prev_move.promotion
                    and prev_move.to_square != node.move.from_square
                    and prev_move.to_square != node.move.to_square
                    and not node.parent.board().is_check()
                    and (not board.is_check() or util.moved_piece_type(node.parent) != KING)
                ):
                    if prev_move.from_square == node.move.to_square or prev_move.from_square in SquareSet.between(
                        node.move.from_square, node.move.to_square
                    ):
                        if (
                            prev.parent
                            and not prev.parent.board().piece_at(prev_move.to_square)
                            or util.is_in_bad_spot(prev.board(), prev_move.to_square)
                        ):
                            return True
    return False


def en_passant(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        if (
            util.moved_piece_type(node) == PAWN
            and square_file(node.move.from_square) != square_file(node.move.to_square)
            and not node.parent.board().piece_at(node.move.to_square)
        ):
            return True
    return False


def castling(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        if util.is_castling(node):
            return True
    return False


def promotion(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        if node.move.promotion:
            return True
    return False


def under_promotion(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2]:
        if node.move.promotion and node.move.promotion != QUEEN:
            return True
    return False


def capturing_defender(puzzle: Puzzle) -> bool:
    for node in puzzle.mainline[1::2][1:]:
        board = node.board()
        capture = node.parent.board().piece_at(node.move.to_square)
        assert isinstance(node.parent, ChildNode)
        if board.is_checkmate() or (
            capture
            and util.moved_piece_type(node) != KING
            and util.values[capture.piece_type] <= util.values[util.moved_piece_type(node)]
            and util.is_hanging(node.parent.board(), capture, node.move.to_square)
            and node.parent.move.to_square != node.move.to_square
        ):
            prev = node.parent.parent
            assert isinstance(prev, ChildNode)
            if not prev.board().is_check() and prev.move.to_square != node.move.from_square:
                assert prev.parent
                init_board = prev.parent.board()
                defender_square = prev.move.to_square
                defender = init_board.piece_at(defender_square)
                if (
                    defender
                    and defender_square in init_board.attackers(defender.color, node.move.to_square)
                    and not init_board.is_check()
                ):
                    return True
    return False


def back_rank_mate(puzzle: Puzzle) -> bool:
    node = puzzle.game.end()
    board = node.board()
    king = board.king(not puzzle.pov)
    assert king is not None
    assert isinstance(node, ChildNode)
    back_rank = 7 if puzzle.pov else 0
    if board.is_checkmate() and square_rank(king) == back_rank:
        squares = SquareSet.from_square(king + (-8 if puzzle.pov else 8))
        if puzzle.pov:
            if chess.square_file(king) < 7:
                squares.add(king - 7)
            if chess.square_file(king) > 0:
                squares.add(king - 9)
        else:
            if chess.square_file(king) < 7:
                squares.add(king + 9)
            if chess.square_file(king) > 0:
                squares.add(king + 7)
        for square in squares:
            piece = board.piece_at(square)
            if piece is None or piece.color == puzzle.pov or board.attackers(puzzle.pov, square):
                return False
        return any(square_rank(checker) == back_rank for checker in board.checkers())
    return False


def anastasia_mate(puzzle: Puzzle) -> bool:
    node = puzzle.game.end()
    board = node.board()
    king = board.king(not puzzle.pov)
    assert king is not None
    assert isinstance(node, ChildNode)
    if square_file(king) in [0, 7] and square_rank(king) not in [0, 7]:
        if square_file(node.move.to_square) == square_file(king) and util.moved_piece_type(node) in [QUEEN, ROOK]:
            if square_file(king) != 0:
                board.apply_transform(chess.flip_horizontal)
            king = board.king(not puzzle.pov)
            assert king is not None
            blocker = board.piece_at(king + 1)
            if blocker is not None and blocker.color != puzzle.pov:
                knight = board.piece_at(king + 3)
                if knight is not None and knight.color == puzzle.pov and knight.piece_type == KNIGHT:
                    return True
    return False


def hook_mate(puzzle: Puzzle) -> bool:
    node = puzzle.game.end()
    board = node.board()
    king = board.king(not puzzle.pov)
    assert king is not None
    assert isinstance(node, ChildNode)
    if util.moved_piece_type(node) == ROOK and square_distance(node.move.to_square, king) == 1:
        for rook_defender_square in board.attackers(puzzle.pov, node.move.to_square):
            defender = board.piece_at(rook_defender_square)
            if defender and defender.piece_type == KNIGHT and square_distance(rook_defender_square, king) == 1:
                for knight_defender_square in board.attackers(puzzle.pov, rook_defender_square):
                    pawn = board.piece_at(knight_defender_square)
                    if pawn and pawn.piece_type == PAWN:
                        return True
    return False


def arabian_mate(puzzle: Puzzle) -> bool:
    node = puzzle.game.end()
    board = node.board()
    king = board.king(not puzzle.pov)
    assert king is not None
    assert isinstance(node, ChildNode)
    if (
        square_file(king) in [0, 7]
        and square_rank(king) in [0, 7]
        and util.moved_piece_type(node) == ROOK
        and square_distance(node.move.to_square, king) == 1
    ):
        for knight_square in board.attackers(puzzle.pov, node.move.to_square):
            knight = board.piece_at(knight_square)
            if (
                knight
                and knight.piece_type == KNIGHT
                and (
                    abs(square_rank(knight_square) - square_rank(king)) == 2
                    and abs(square_file(knight_square) - square_file(king)) == 2
                )
            ):
                return True
    return False


def boden_or_double_bishop_mate(puzzle: Puzzle):
    node = puzzle.game.end()
    board = node.board()
    king = board.king(not puzzle.pov)
    assert king is not None
    assert isinstance(node, ChildNode)
    bishop_squares = list(board.pieces(BISHOP, puzzle.pov))
    if len(bishop_squares) < 2:
        return None
    for square in [s for s in SquareSet(chess.BB_ALL) if square_distance(s, king) < 2]:
        if not all([p.piece_type == BISHOP for p in util.attacker_pieces(board, puzzle.pov, square)]):
            return None
    if (square_file(bishop_squares[0]) < square_file(king)) == (square_file(bishop_squares[1]) > square_file(king)):
        return "bodenMate"
    else:
        return "doubleBishopMate"


def dovetail_mate(puzzle: Puzzle) -> bool:
    node = puzzle.game.end()
    board = node.board()
    king = board.king(not puzzle.pov)
    assert king is not None
    assert isinstance(node, ChildNode)
    if square_file(king) in [0, 7] or square_rank(king) in [0, 7]:
        return False
    queen_square = node.move.to_square
    if (
        util.moved_piece_type(node) != QUEEN
        or square_file(queen_square) == square_file(king)
        or square_rank(queen_square) == square_rank(king)
        or square_distance(queen_square, king) > 1
    ):
        return False
    for square in [s for s in SquareSet(chess.BB_ALL) if square_distance(s, king) == 1]:
        if square == queen_square:
            continue
        attackers = list(board.attackers(puzzle.pov, square))
        if attackers == [queen_square]:
            if board.piece_at(square):
                return False
        elif attackers:
            return False
    return True


def piece_endgame(puzzle: Puzzle, piece_type: PieceType) -> bool:
    for board in [puzzle.mainline[i].board() for i in [0, 1]]:
        if not board.pieces(piece_type, WHITE) and not board.pieces(piece_type, BLACK):
            return False
        for piece in board.piece_map().values():
            if not piece.piece_type in [KING, PAWN, piece_type]:
                return False
    return True


def queen_rook_endgame(puzzle: Puzzle) -> bool:
    def test(board: Board) -> bool:
        pieces = board.piece_map().values()
        return (
            len([p for p in pieces if p.piece_type == QUEEN]) == 1
            and any(p.piece_type == ROOK for p in pieces)
            and all(p.piece_type in [QUEEN, ROOK, PAWN, KING] for p in pieces)
        )

    return all(test(puzzle.mainline[i].board()) for i in [0, 1])


def smothered_mate(puzzle: Puzzle) -> bool:
    board = puzzle.game.end().board()
    king_square = board.king(not puzzle.pov)
    assert king_square is not None
    for checker_square in board.checkers():
        piece = board.piece_at(checker_square)
        assert piece
        if piece.piece_type == KNIGHT:
            for escape_square in [s for s in chess.SQUARES if square_distance(s, king_square) == 1]:
                blocker = board.piece_at(escape_square)
                if not blocker or blocker.color == puzzle.pov:
                    return False
            return True
    return False


def mate_in(puzzle: Puzzle):
    if not puzzle.game.end().board().is_checkmate():
        return None
    moves_to_mate = len(puzzle.mainline) // 2
    if moves_to_mate == 1:
        return "mateIn1"
    elif moves_to_mate == 2:
        return "mateIn2"
    elif moves_to_mate == 3:
        return "mateIn3"
    elif moves_to_mate == 4:
        return "mateIn4"
    return "mateIn5"


st_valid = {
    # "advancedPawn",
    "attraction",
    "backRankMate",
    # "boardVision",
    "capturingDefender",
    "checkMateThreat",
    # "clearance",
    "decoy",
    # "defensiveMove",
    "deflection",
    "desperado",
    "discoveredAttack",
    "doubledPawns",
    "doubleCheck",
    # "exposedKing",
    # "exchange",
    "forcedMove",
    "fork",
    "hangingPiece",
    "interference",
    "isolatedPawn",
    "openFile",
    "overload",
    "outpost",
    "passedPawn",
    "pin",
    # "promotion",
    #    "quietMove",
    "sacrifice",
    "semiProtectedPiece",
    "simplification",
    "skewer",
    "speculation",
    # "tempo",
    "threat",
    "trappedPiece",
    "underPromotion",
    "weakSquare",
    "unsafeSquare",
    "xRayAttack",
    "zwischenzug",
    "zugzwang",
    # "advantage",
    "anastasiaMate",
    "arabianMate",
    "bodenMate",
    "coercion",
    "crushing",
    "doubleBishopMate",
    "dovetailMate",
    "hookMate",
    # "kingsideAttack",
    # "queensideAttack",
    "smotheredMate",
}

st_not_unique = {
    "capturingDefender",
    "forcedMove",
    "sacrifice",
    "simplification",
    "speculation",
    "threat",
    "weakSquare",
    "unsafeSquare",
    "coercion",
    "crushing",
}


def get_tags(fen, pvline, cp):
    b = chess.Board(fen)
    game = chess.pgn.Game()
    game.setup(b)

    node = game
    for mv in pvline.split(" "):
        node = node.add_variation(chess.Move.from_uci(mv))

    p = Puzzle()
    p.game = game
    p.pov = not game.turn()
    p.mainline = list(game.mainline())
    p.cp = cp

    li = cook(p)
    li_themes = [theme for theme in li if theme in st_valid]

    if len(li_themes) == 1:
        if li_themes[0] in st_not_unique:
            li_themes = []

    return li_themes
