#실행 코드 python3 pygame_chess_ai_mac.py


from pathlib import Path

output_path = Path(__file__).with_name("pygame_chess_ai_mac.py")
output_path.parent.mkdir(parents=True, exist_ok=True)

code = r'''"""
Pygame 체스: 사람 대 AI

기능
- 사람(백) 대 컴퓨터(흑)
- AI 난이도 1~5단계 조절
- 합법 수, 체크, 체크메이트, 스테일메이트
- 캐슬링, 앙파상, 폰 승격
- 무르기, 새 게임, 보드 뒤집기
- 맥에서 실행 가능

설치:
    python3 -m pip install pygame python-chess

실행:
    python3 pygame_chess_ai_mac.py
"""

from __future__ import annotations

import math
import random
import sys
import time
from dataclasses import dataclass

import chess
import pygame


# ============================================================
# 화면 설정
# ============================================================

BOARD_SIZE = 720
SIDE_PANEL_WIDTH = 330
WINDOW_WIDTH = BOARD_SIZE + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE
SQUARE_SIZE = BOARD_SIZE // 8
FPS = 60

LIGHT_SQUARE = (238, 216, 181)
DARK_SQUARE = (181, 136, 99)
SELECTED_COLOR = (246, 246, 105)
LAST_MOVE_COLOR = (235, 210, 65)
CHECK_COLOR = (225, 70, 70)
LEGAL_MOVE_COLOR = (55, 130, 70)
CAPTURE_COLOR = (180, 55, 55)

PANEL_BG = (35, 38, 45)
PANEL_TEXT = (245, 245, 245)
PANEL_MUTED = (175, 181, 191)
BUTTON_BG = (70, 76, 88)
BUTTON_HOVER = (91, 99, 115)
BUTTON_ACTIVE = (56, 120, 85)

WHITE_PIECE = (245, 245, 245)
BLACK_PIECE = (25, 25, 25)
PIECE_OUTLINE = (70, 70, 70)


# ============================================================
# 체스 말 및 AI 평가값
# ============================================================

PIECE_SYMBOLS = {
    chess.PAWN: {"white": "♙", "black": "♟"},
    chess.KNIGHT: {"white": "♘", "black": "♞"},
    chess.BISHOP: {"white": "♗", "black": "♝"},
    chess.ROOK: {"white": "♖", "black": "♜"},
    chess.QUEEN: {"white": "♕", "black": "♛"},
    chess.KING: {"white": "♔", "black": "♚"},
}

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

PROMOTION_NAMES = {
    chess.QUEEN: "퀸",
    chess.ROOK: "룩",
    chess.BISHOP: "비숍",
    chess.KNIGHT: "나이트",
}

# 난이도별 설정
# depth: 미니맥스 탐색 깊이
# randomness: 좋은 수 중 일부를 무작위로 고를 정도
DIFFICULTY_SETTINGS = {
    1: {"name": "초급", "depth": 1, "randomness": 0.45},
    2: {"name": "쉬움", "depth": 1, "randomness": 0.15},
    3: {"name": "보통", "depth": 2, "randomness": 0.08},
    4: {"name": "어려움", "depth": 3, "randomness": 0.03},
    5: {"name": "매우 어려움", "depth": 3, "randomness": 0.0},
}


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    action: str

    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        active: bool = False,
    ) -> None:
        mouse_pos = pygame.mouse.get_pos()

        if active:
            color = BUTTON_ACTIVE
        elif self.rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER
        else:
            color = BUTTON_BG

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        label = font.render(self.text, True, PANEL_TEXT)
        screen.blit(label, label.get_rect(center=self.rect.center))


class ChessAI:
    """간단한 미니맥스 + 알파베타 가지치기 체스 AI."""

    def __init__(self, color: chess.Color = chess.BLACK) -> None:
        self.color = color
        self.nodes = 0

    def choose_move(self, board: chess.Board, difficulty: int) -> chess.Move | None:
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        config = DIFFICULTY_SETTINGS[difficulty]
        depth = config["depth"]
        randomness = config["randomness"]

        self.nodes = 0
        ordered_moves = self.order_moves(board, legal_moves)
        scored_moves: list[tuple[float, chess.Move]] = []

        alpha = -math.inf
        beta = math.inf

        for move in ordered_moves:
            board.push(move)
            score = self.minimax(
                board=board,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                maximizing=False,
            )
            board.pop()
            scored_moves.append((score, move))
            alpha = max(alpha, score)

        scored_moves.sort(key=lambda item: item[0], reverse=True)

        # 낮은 난이도에서는 상위 후보들 중 일부를 확률적으로 선택한다.
        if randomness > 0 and random.random() < randomness:
            candidate_count = min(4, len(scored_moves))
            return random.choice(scored_moves[:candidate_count])[1]

        return scored_moves[0][1]

    def minimax(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        self.nodes += 1

        if depth <= 0 or board.is_game_over():
            return self.evaluate(board)

        legal_moves = self.order_moves(board, list(board.legal_moves))

        if maximizing:
            best_score = -math.inf
            for move in legal_moves:
                board.push(move)
                score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score

        best_score = math.inf
        for move in legal_moves:
            board.push(move)
            score = self.minimax(board, depth - 1, alpha, beta, True)
            board.pop()

            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score

    def evaluate(self, board: chess.Board) -> float:
        if board.is_checkmate():
            # 현재 차례인 쪽이 체크메이트를 당한 상태다.
            return 100000 if board.turn != self.color else -100000

        if (
            board.is_stalemate()
            or board.is_insufficient_material()
            or board.can_claim_fifty_moves()
            or board.can_claim_threefold_repetition()
        ):
            return 0

        score = 0.0

        for piece_type, value in PIECE_VALUES.items():
            ai_count = len(board.pieces(piece_type, self.color))
            human_count = len(board.pieces(piece_type, not self.color))
            score += (ai_count - human_count) * value

        # 중앙 장악
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        for square in center_squares:
            piece = board.piece_at(square)
            if piece:
                score += 20 if piece.color == self.color else -20

        # 기물 전개 및 이동 가능성
        current_turn = board.turn
        board.turn = self.color
        ai_mobility = board.legal_moves.count()
        board.turn = not self.color
        human_mobility = board.legal_moves.count()
        board.turn = current_turn
        score += (ai_mobility - human_mobility) * 2

        # 체크 보너스/패널티
        if board.is_check():
            if board.turn == self.color:
                score -= 35
            else:
                score += 35

        # 킹 안전: 캐슬링 권리와 실제 킹 위치를 간단히 평가
        ai_king = board.king(self.color)
        human_king = board.king(not self.color)

        if ai_king in (chess.G8, chess.C8, chess.G1, chess.C1):
            score += 25
        if human_king in (chess.G8, chess.C8, chess.G1, chess.C1):
            score -= 25

        return score

    @staticmethod
    def order_moves(
        board: chess.Board,
        moves: list[chess.Move],
    ) -> list[chess.Move]:
        def move_score(move: chess.Move) -> int:
            score = 0

            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                captured_value = PIECE_VALUES.get(captured.piece_type, 0) if captured else 100
                attacker_value = PIECE_VALUES.get(attacker.piece_type, 0) if attacker else 0
                score += 10 * captured_value - attacker_value

            if move.promotion:
                score += PIECE_VALUES.get(move.promotion, 0)

            board.push(move)
            if board.is_check():
                score += 80
            board.pop()

            return score

        return sorted(moves, key=move_score, reverse=True)


class ChessGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pygame 체스 - 사람 대 AI")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.board = chess.Board()
        self.ai = ChessAI(chess.BLACK)

        self.human_color = chess.WHITE
        self.ai_color = chess.BLACK
        self.difficulty = 3

        self.selected_square: chess.Square | None = None
        self.legal_moves: list[chess.Move] = []
        self.flipped = False
        self.learning_mode = False
        self.learning_hint: chess.Move | None = None
        self.hint_reason = ""
        self.last_move: chess.Move | None = None
        self.message = "당신의 차례입니다."
        self.ai_thinking = False
        self.ai_last_nodes = 0
        self.ai_last_time = 0.0
        self.promotion_pending: chess.PieceType | None = None
        self.piece_font = self.create_piece_font(69)
        self.title_font = self.create_text_font(29, bold=True)
        self.text_font = self.create_text_font(21)
        self.small_font = self.create_text_font(16)
        self.button_font = self.create_text_font(18, bold=True)
        self.coord_font = self.create_text_font(15, bold=True)

        panel_x = BOARD_SIZE + 22

        self.action_buttons = [
            Button(pygame.Rect(panel_x, 486, 286, 46), "무르기  [R]", "undo"),
            Button(pygame.Rect(panel_x, 542, 286, 46), "새 게임  [N]", "reset"),
            Button(pygame.Rect(panel_x, 598, 286, 46), "보드 뒤집기  [F]", "flip"),
            Button(pygame.Rect(panel_x, 654, 286, 46), "힌트  [L]", "toggle_learning"),
        ]

        self.difficulty_buttons: list[Button] = []
        start_y = 310
        for level in range(1, 6):
            name = DIFFICULTY_SETTINGS[level]["name"]
            button = Button(
                pygame.Rect(panel_x, start_y + (level - 1) * 34, 286, 29),
                f"{level}. {name}",
                f"difficulty_{level}",
            )
            self.difficulty_buttons.append(button)
    @staticmethod
    def create_text_font(size: int, bold: bool = False) -> pygame.font.Font:
        candidates = [
            "Apple SD Gothic Neo",
            "Arial Unicode MS",
            "Helvetica",
            "Arial",
        ]

        for name in candidates:
            path = pygame.font.match_font(name, bold=bold)
            if path:
                return pygame.font.Font(path, size)

        return pygame.font.Font(None, size)

    @staticmethod
    def create_piece_font(size: int) -> pygame.font.Font:
        candidates = [
            "Arial Unicode MS",
            "Apple Symbols",
            "DejaVu Sans",
            "Noto Sans Symbols 2",
            "Symbola",
        ]

        for name in candidates:
            path = pygame.font.match_font(name)
            if path:
                return pygame.font.Font(path, size)

        return pygame.font.Font(None, size)

    def square_to_screen(self, square: chess.Square) -> tuple[int, int]:
        file_index = chess.square_file(square)
        rank_index = chess.square_rank(square)

        if self.flipped:
            col = 7 - file_index
            row = rank_index
        else:
            col = file_index
            row = 7 - rank_index

        return col * SQUARE_SIZE, row * SQUARE_SIZE

    def screen_to_square(self, position: tuple[int, int]) -> chess.Square | None:
        x, y = position

        if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
            return None

        col = x // SQUARE_SIZE
        row = y // SQUARE_SIZE

        if self.flipped:
            file_index = 7 - col
            rank_index = row
        else:
            file_index = col
            rank_index = 7 - row

        return chess.square(file_index, rank_index)

    def moves_from_square(self, square: chess.Square) -> list[chess.Move]:
        return [
            move
            for move in self.board.legal_moves
            if move.from_square == square
        ]

    def reset_game(self) -> None:
        self.board.reset()
        self.selected_square = None
        self.legal_moves = []
        self.learning_hint = None
        self.hint_reason = ""
        self.promotion_pending = None
        self.ai_last_nodes = 0
        self.ai_last_time = 0.0
        self.update_message()

    def describe_hint(self, move: chess.Move, is_check: bool) -> str:
        if self.board.is_capture(move):
            return "상대 기물을 잡아 자산을 늘립니다."
        if move.promotion:
            return "폰을 승격해 강한 기물을 만들 수 있습니다."
        if is_check:
            return "체크를 걸어 상대의 반응을 제한합니다."
        if move.to_square in (chess.D4, chess.E4, chess.D5, chess.E5):
            return "중앙으로 이동해 기물 활동을 넓힙니다."
        return "기물을 안전하게 전개해 다음 수를 준비합니다."

    def get_learning_hint(self) -> tuple[chess.Move | None, str]:
        candidate_moves = (
            self.legal_moves
            if self.selected_square is not None
            else list(self.board.legal_moves)
        )
        if not candidate_moves:
            return None, ""

        best_move = None
        best_score = -math.inf

        for move in candidate_moves:
            score = 0

            if self.board.is_capture(move):
                captured = self.board.piece_at(move.to_square)
                attacker = self.board.piece_at(move.from_square)
                captured_value = (
                    PIECE_VALUES.get(captured.piece_type, 0)
                    if captured
                    else 100
                )
                attacker_value = (
                    PIECE_VALUES.get(attacker.piece_type, 0)
                    if attacker
                    else 0
                )
                score += 10 * captured_value - attacker_value

            if move.promotion:
                score += PIECE_VALUES.get(move.promotion, 0)

            self.board.push(move)
            if self.board.is_check():
                score += 80
            self.board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None:
            return None, ""

        self.board.push(best_move)
        is_check = self.board.is_check()
        self.board.pop()
        return best_move, self.describe_hint(best_move, is_check)

    def toggle_learning_mode(self) -> None:
        self.learning_mode = not self.learning_mode
        self.learning_hint = None
        self.hint_reason = ""
        if self.learning_mode:
            self.message = "힌트: 추천 수와 이유가 함께 표시됩니다."
        else:
            self.update_message()

    def undo_turn(self) -> None:
        if self.ai_thinking:
            return

        if len(self.board.move_stack) >= 2:
            self.board.pop()
            self.board.pop()
        elif self.board.move_stack:
            self.board.pop()

        self.selected_square = None
        self.legal_moves = []
        self.learning_hint = None
        self.hint_reason = ""
        self.promotion_pending = None
        self.update_message()

    def set_difficulty(self, level: int) -> None:
        if level not in DIFFICULTY_SETTINGS:
            return

        self.difficulty = level
        name = DIFFICULTY_SETTINGS[level]["name"]
        self.message = f"AI 난이도: {level}단계 {name}"

    def handle_board_click(self, square: chess.Square) -> None:
        if self.ai_thinking:
            return

        if self.board.is_game_over():
            return

        if self.board.turn != self.human_color:
            return

        if self.promotion_pending is not None:
            return

        piece = self.board.piece_at(square)

        if self.selected_square is None:
            if piece and piece.color == self.human_color:
                self.selected_square = square
                self.legal_moves = self.moves_from_square(square)
                self.learning_hint = None
                self.hint_reason = ""
            return

        matching_moves = [
            move for move in self.legal_moves
            if move.to_square == square
        ]

        if matching_moves:
            promotion_moves = [
                move for move in matching_moves
                if move.promotion is not None
            ]

            if promotion_moves:
                self.promotion_pending = (self.selected_square, square)
                return

            self.make_human_move(matching_moves[0])
            return

        if piece and piece.color == self.human_color:
            self.selected_square = square
            self.legal_moves = self.moves_from_square(square)
        else:
            self.selected_square = None
            self.legal_moves = []

    def make_human_move(self, move: chess.Move) -> None:
        if move not in self.board.legal_moves:
            return

        self.board.push(move)
        self.last_move = move
        self.selected_square = None
        self.legal_moves = []
        self.learning_hint = None
        self.hint_reason = ""
        self.promotion_pending = None
        self.update_message()

        if not self.board.is_game_over():
            pygame.time.set_timer(pygame.USEREVENT + 1, 250, loops=1)


    def make_ai_move(self) -> None:
        if self.board.is_game_over() or self.board.turn != self.ai_color:
            return

        self.ai_thinking = True
        self.message = "AI가 수를 계산하고 있습니다..."
        self.draw()
        pygame.display.flip()

        start_time = time.perf_counter()
        move = self.ai.choose_move(self.board, self.difficulty)
        elapsed = time.perf_counter() - start_time

        self.ai_last_nodes = self.ai.nodes
        self.ai_last_time = elapsed

        if move is not None:
            self.board.push(move)
            self.last_move = move

        self.ai_thinking = False
        self.update_message()

    def update_message(self) -> None:
        outcome = self.board.outcome(claim_draw=True)

        if outcome is not None:
            if outcome.winner == self.human_color:
                self.message = "게임 종료: 당신이 이겼습니다!"
            elif outcome.winner == self.ai_color:
                self.message = "게임 종료: AI가 이겼습니다."
            else:
                self.message = "게임 종료: 무승부입니다."
            return

        if self.board.is_check():
            if self.board.turn == self.human_color:
                self.message = "체크! 당신의 차례입니다."
            else:
                self.message = "AI가 체크를 당했습니다."
            return

        if self.board.turn == self.human_color:
            self.message = "당신의 차례입니다."
        else:
            self.message = "AI 차례입니다."

    def draw_board(self) -> None:
            ):
                overlay = pygame.Surface(
                    (SQUARE_SIZE, SQUARE_SIZE),
                    pygame.SRCALPHA,
                )
                overlay.fill((*LAST_MOVE_COLOR, 105))
                self.screen.blit(overlay, (x, y))

            if square == self.selected_square:
                overlay = pygame.Surface(
                    (SQUARE_SIZE, SQUARE_SIZE),
                    pygame.SRCALPHA,
                )
                overlay.fill((*SELECTED_COLOR, 130))
                self.screen.blit(overlay, (x, y))

        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            if king_square is not None:
                x, y = self.square_to_screen(king_square)
                overlay = pygame.Surface(
                    (SQUARE_SIZE, SQUARE_SIZE),
                    pygame.SRCALPHA,
                )
                overlay.fill((*CHECK_COLOR, 150))
                self.screen.blit(overlay, (x, y))

        self.draw_legal_move_marks()
        self.draw_coordinates()
        self.draw_pieces()

    def draw_learning_hint(self) -> None:
        if not self.learning_mode:
            return

        self.learning_hint, self.hint_reason = self.get_learning_hint()
        if self.learning_hint is None:
            return

        hint_x, hint_y = self.square_to_screen(self.learning_hint.to_square)
        overlay = pygame.Surface(
            (SQUARE_SIZE, SQUARE_SIZE),
            pygame.SRCALPHA,
        )
        overlay.fill((72, 151, 235, 105))
        self.screen.blit(overlay, (hint_x, hint_y))

    def draw_legal_move_marks(self) -> None:
        for move in self.legal_moves:
            x, y = self.square_to_screen(move.to_square)
            center = (
                x + SQUARE_SIZE // 2,
                y + SQUARE_SIZE // 2,
            )

            if self.board.is_capture(move):
                pygame.draw.circle(
                    self.screen,
                    CAPTURE_COLOR,
                    center,
                    SQUARE_SIZE // 2 - 7,
                    width=6,
                )
            else:
                pygame.draw.circle(
                    self.screen,
                    LEGAL_MOVE_COLOR,
                    center,
                    12,
                )

    def draw_coordinates(self) -> None:
        for col in range(8):
            if self.flipped:
                file_text = chr(ord("h") - col)
            else:
                file_text = chr(ord("a") + col)

            label = self.coord_font.render(
                file_text,
                True,
                (70, 55, 40),
            )
            self.screen.blit(
                label,
                (
                    col * SQUARE_SIZE + SQUARE_SIZE - 17,
                    BOARD_SIZE - 20,
                ),
            )

        for row in range(8):
            if self.flipped:
                rank_text = str(row + 1)
            else:
                rank_text = str(8 - row)

            label = self.coord_font.render(
                rank_text,
                True,
                (70, 55, 40),
            )
            self.screen.blit(
                label,
                (
                    5,
                    row * SQUARE_SIZE + 4,
                ),
            )

    def draw_pieces(self) -> None:
        for square, piece in self.board.piece_map().items():
            x, y = self.square_to_screen(square)
            color_name = "white" if piece.color == chess.WHITE else "black"
            symbol = PIECE_SYMBOLS[piece.piece_type][color_name]

            piece_color = WHITE_PIECE if piece.color else BLACK_PIECE
            rendered = self.piece_font.render(symbol, True, piece_color)

            # 흰색 말에 얇은 외곽선을 넣어 밝은 칸에서도 보이게 한다.
            if piece.color == chess.WHITE:
                outline = self.piece_font.render(
                    symbol,
                    True,
                    PIECE_OUTLINE,
                )
                outline_rect = outline.get_rect(
                    center=(
                        x + SQUARE_SIZE // 2,
                        y + SQUARE_SIZE // 2 + 1,
                    )
                )
                for offset_x, offset_y in (
                    (-1, 0),
                    (1, 0),
                    (0, -1),
                    (0, 1),
                ):
                    self.screen.blit(
                        outline,
                        outline_rect.move(offset_x, offset_y),
                    )

            rect = rendered.get_rect(
                center=(
                    x + SQUARE_SIZE // 2,
                    y + SQUARE_SIZE // 2 + 1,
                )
            )
            self.screen.blit(rendered, rect)

    def draw_wrapped_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
        line_spacing: int = 4,
    ) -> int:
        words = text.split()
        lines: list[str] = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= rect.width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        y = rect.top
        for line in lines:
            surface = font.render(line, True, color)
            self.screen.blit(surface, (rect.left, y))
            y += font.get_height() + line_spacing

        return y

    def draw_side_panel(self) -> None:
        pygame.draw.rect(
            self.screen,
            PANEL_BG,
            (BOARD_SIZE, 0, SIDE_PANEL_WIDTH, WINDOW_HEIGHT),
        )

        x = BOARD_SIZE + 22

        title = self.title_font.render(
            "사람 대 AI 체스",
            True,
            PANEL_TEXT,
        )
        self.screen.blit(title, (x, 22))

        subtitle = self.small_font.render(
            "당신: 백  |  컴퓨터: 흑",
            True,
            PANEL_MUTED,
        )
        self.screen.blit(subtitle, (x, 62))

        self.draw_wrapped_text(
            self.message,
            self.text_font,
            PANEL_TEXT,
            pygame.Rect(x, 96, 286, 70),
        )

        turn_text = (
            "현재 차례: 백"
            if self.board.turn == chess.WHITE
            else "현재 차례: 흑"
        )
        self.screen.blit(
            self.small_font.render(turn_text, True, PANEL_MUTED),
            (x, 172),
        )

        mode_text = "힌트: 켜짐" if self.learning_mode else "힌트: 꺼짐"
        self.screen.blit(
            self.small_font.render(mode_text, True, PANEL_MUTED),
            (x, 196),
        )

        if self.learning_hint is not None:
            hint_text = (
                "추천 수: "
                f"{chess.square_name(self.learning_hint.from_square)}→"
                f"{chess.square_name(self.learning_hint.to_square)}"
            )
            self.screen.blit(
                self.small_font.render(hint_text, True, PANEL_MUTED),
                (x, 220),
            )
            self.draw_wrapped_text(
                self.hint_reason,
                self.small_font,
                PANEL_MUTED,
                pygame.Rect(x, 244, 286, 52),
            )

        move_number = len(self.board.move_stack)
        self.screen.blit(
            self.small_font.render(
                f"진행된 수: {move_number}",
                True,
                PANEL_MUTED,
            ),
            (x, 310),
        )

        if self.ai_last_time > 0:
            ai_info = (
                f"AI 계산: {self.ai_last_time:.2f}초 / "
                f"{self.ai_last_nodes:,} 노드"
            )
            self.screen.blit(
                self.small_font.render(
                    ai_info,
                    True,
                    PANEL_MUTED,
                ),
                (x, 334),
            )

        difficulty_title = self.text_font.render(
            "AI 난이도",
            True,
            PANEL_TEXT,
        )
        self.screen.blit(difficulty_title, (x, 377))
        pygame.draw.rect(
            self.screen,
            PANEL_BG,
            dialog,
            border_radius=12,
        )
        pygame.draw.rect(
            self.screen,
            PANEL_TEXT,
            dialog,
            width=2,
            border_radius=12,
        )

        title = self.text_font.render(
            "승격할 말을 선택하세요",
            True,
            PANEL_TEXT,
        )
        self.screen.blit(
            title,
            title.get_rect(
                center=(dialog.centerx, dialog.top + 38)
            ),
        )

        choices = [
            chess.QUEEN,
            chess.ROOK,
            chess.BISHOP,
            chess.KNIGHT,
        ]

        for index, piece_type in enumerate(choices):
            button_rect = pygame.Rect(
                dialog.left + 25 + index * 112,
                dialog.top + 80,
                100,
                80,
            )
            mouse_over = button_rect.collidepoint(
                pygame.mouse.get_pos()
            )
            color = BUTTON_HOVER if mouse_over else BUTTON_BG
            pygame.draw.rect(
                self.screen,
                color,
                button_rect,
                border_radius=8,
            )

            symbol = PIECE_SYMBOLS[piece_type]["white"]
            piece_surface = self.piece_font.render(
                symbol,
                True,
                WHITE_PIECE,
            )
            self.screen.blit(
                piece_surface,
                piece_surface.get_rect(
                    center=(
                        button_rect.centerx,
                        button_rect.centery - 8,
                    )
                ),
            )

            name_surface = self.small_font.render(
                PROMOTION_NAMES[piece_type],
                True,
                PANEL_TEXT,
            )
            self.screen.blit(
                name_surface,
                name_surface.get_rect(
                    center=(
                        button_rect.centerx,
                        button_rect.bottom - 13,
                    )
                ),
            )

    def promotion_choice_at(
        self,
        position: tuple[int, int],
    ) -> chess.PieceType | None:
        if self.promotion_pending is None:
            return None

        dialog_left = BOARD_SIZE // 2 - 245
        dialog_top = WINDOW_HEIGHT // 2 - 100
        choices = [
            chess.QUEEN,
            chess.ROOK,
            chess.BISHOP,
            chess.KNIGHT,
        ]

        for index, piece_type in enumerate(choices):
            button_rect = pygame.Rect(
                dialog_left + 25 + index * 112,
                dialog_top + 80,
                100,
                80,
            )
            if button_rect.collidepoint(position):
                return piece_type

        return None

    def draw(self) -> None:
        self.draw_board()
        self.draw_side_panel()
        self.draw_promotion_dialog()

    def handle_button_click(self, position: tuple[int, int]) -> bool:
        for button in self.difficulty_buttons:
            if button.rect.collidepoint(position):
                level = int(button.action.split("_")[-1])
                self.set_difficulty(level)
                return True

        for button in self.action_buttons:
            if button.rect.collidepoint(position):
                if button.action == "undo":
                    self.undo_turn()
                elif button.action == "reset":
                    self.reset_game()
                elif button.action == "flip":
                    self.flipped = not self.flipped
                elif button.action == "toggle_learning":
                    self.toggle_learning_mode()
                return True

        return False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.USEREVENT + 1:
            self.make_ai_move()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.undo_turn()
            elif event.key == pygame.K_n:
                self.reset_game()
            elif event.key == pygame.K_f:
                self.flipped = not self.flipped
            elif event.key == pygame.K_l:
                self.toggle_learning_mode()
            elif pygame.K_1 <= event.key <= pygame.K_5:
                level = event.key - pygame.K_0
                self.set_difficulty(level)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            position = event.pos

            if self.promotion_pending is not None:
                piece_type = self.promotion_choice_at(position)
                if piece_type is not None:
                    self.choose_promotion(piece_type)
                return

            if position[0] >= BOARD_SIZE:
                self.handle_button_click(position)
                return

            square = self.screen_to_square(position)
            if square is not None:
                self.handle_board_click(square)

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    ChessGame().run()
'''

code = code.replace("\u00a0", " ").replace("\u202f", " ")
code = code.replace("\ufeff", "")

output_path.write_text(code, encoding="utf-8")

# 문법 검사
compile(code, str(output_path), "exec")

print(f"생성 완료: {output_path}")
print(f"코드 줄 수: {len(code.splitlines())}")

#학습 모드
