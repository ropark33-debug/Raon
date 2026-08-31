
"""
Pygame 스도쿠

기능
- 9x9 스도쿠
- 난이도 1~4단계
- 자동 퍼즐 생성
- 숫자 입력
- 메모 모드
- 힌트
- 정답 검사
- 틀린 숫자 표시
- 새 게임
- 타이머
- 맥에서 실행 가능

설치:
    python3 -m pip install pygame

실행:
    python3 pygame_sudoku_mac.py
"""

from __future__ import annotations

import random
import sys
import time
from dataclasses import dataclass

import pygame


# ============================================================
# 화면 설정
# ============================================================

CELL_SIZE = 66
GRID_SIZE = CELL_SIZE * 9
SIDE_PANEL_WIDTH = 320

WINDOW_WIDTH = GRID_SIZE + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = GRID_SIZE

FPS = 60

BG_COLOR = (245, 245, 245)
GRID_COLOR = (45, 45, 45)
THIN_GRID = (145, 145, 145)
SELECTED_COLOR = (194, 224, 255)
RELATED_COLOR = (226, 239, 250)
SAME_NUMBER_COLOR = (214, 232, 255)
FIXED_NUMBER_COLOR = (30, 30, 30)
USER_NUMBER_COLOR = (42, 92, 170)
ERROR_COLOR = (205, 48, 48)
NOTE_COLOR = (95, 105, 120)

PANEL_BG = (35, 38, 45)
PANEL_TEXT = (245, 245, 245)
PANEL_MUTED = (175, 181, 191)
BUTTON_BG = (70, 76, 88)
BUTTON_HOVER = (91, 99, 115)
BUTTON_ACTIVE = (56, 120, 85)

DIFFICULTIES = {
    1: {"name": "쉬움", "remove": 36},
    2: {"name": "보통", "remove": 44},
    3: {"name": "어려움", "remove": 50},
    4: {"name": "매우 어려움", "remove": 55},
}


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    action: str

    def draw(self, screen, font, active=False):
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


# ============================================================
# 스도쿠 생성 및 풀이
# ============================================================

def is_valid(board, row, col, number):
    if number in board[row]:
        return False

    for r in range(9):
        if board[r][col] == number:
            return False

    box_row = (row // 3) * 3
    box_col = (col // 3) * 3

    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == number:
                return False

    return True


def find_empty(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col
    return None


def solve_board(board):
    empty = find_empty(board)

    if empty is None:
        return True

    row, col = empty
    numbers = list(range(1, 10))
    random.shuffle(numbers)

    for number in numbers:
        if is_valid(board, row, col, number):
            board[row][col] = number

            if solve_board(board):
                return True

            board[row][col] = 0

    return False


def count_solutions(board, limit=2):
    empty = find_empty(board)

    if empty is None:
        return 1

    row, col = empty
    count = 0

    for number in range(1, 10):
        if is_valid(board, row, col, number):
            board[row][col] = number
            count += count_solutions(board, limit)
            board[row][col] = 0

            if count >= limit:
                return count

    return count


def generate_complete_board():
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve_board(board)
    return board


def generate_puzzle(remove_count):
    solution = generate_complete_board()
    puzzle = [row[:] for row in solution]

    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0

    for row, col in cells:
        if removed >= remove_count:
            break

        backup = puzzle[row][col]
        puzzle[row][col] = 0

        test_board = [r[:] for r in puzzle]

        if count_solutions(test_board, limit=2) == 1:
            removed += 1
        else:
            puzzle[row][col] = backup

    return puzzle, solution


class SudokuGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pygame 스도쿠")

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        self.clock = pygame.time.Clock()

        self.title_font = self.create_font(30, bold=True)
        self.number_font = self.create_font(38, bold=True)
        self.text_font = self.create_font(21)
        self.small_font = self.create_font(16)
        self.button_font = self.create_font(18, bold=True)
        self.note_font = self.create_font(14)

        self.difficulty = 2
        self.selected = None
        self.note_mode = False
        self.message = ""
        self.completed = False
        self.start_time = time.time()
        self.elapsed_when_completed = 0

        self.puzzle = []
        self.solution = []
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.fixed = [[False for _ in range(9)] for _ in range(9)]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.errors = set()

        panel_x = GRID_SIZE + 20

        self.difficulty_buttons = []
        start_y = 138

        for level in range(1, 5):
            name = DIFFICULTIES[level]["name"]
            self.difficulty_buttons.append(
                Button(
                    pygame.Rect(
                        panel_x,
                        start_y + (level - 1) * 40,
                        280,
                        32,
                    ),
                    f"{level}. {name}",
                    f"difficulty_{level}",
                )
            )

        self.number_buttons = []
        number_start_y = 345

        for index, number in enumerate(range(1, 10)):
            row = index // 3
            col = index % 3

            self.number_buttons.append(
                Button(
                    pygame.Rect(
                        panel_x + col * 94,
                        number_start_y + row * 48,
                        86,
                        40,
                    ),
                    str(number),
                    f"number_{number}",
                )
            )

        self.action_buttons = [
            Button(
                pygame.Rect(panel_x, 500, 136, 42),
                "메모 [M]",
                "note",
            ),
            Button(
                pygame.Rect(panel_x + 144, 500, 136, 42),
                "지우기 [0]",
                "erase",
            ),
            Button(
                pygame.Rect(panel_x, 552, 136, 42),
                "힌트 [H]",
                "hint",
            ),
            Button(
                pygame.Rect(panel_x + 144, 552, 136, 42),
                "검사 [C]",
                "check",
            ),
            Button(
                pygame.Rect(panel_x, 604, 280, 42),
                "새 게임 [N]",
                "new",
            ),
        ]

        self.new_game()

    @staticmethod
    def create_font(size, bold=False):
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

    def new_game(self):
        remove_count = DIFFICULTIES[self.difficulty]["remove"]

        self.message = "퍼즐을 생성하고 있습니다..."

        self.puzzle, self.solution = generate_puzzle(remove_count)
        self.board = [row[:] for row in self.puzzle]
        self.fixed = [
            [self.puzzle[r][c] != 0 for c in range(9)]
            for r in range(9)
        ]
        self.notes = [
            [set() for _ in range(9)]
            for _ in range(9)
        ]
        self.errors = set()
        self.selected = None
        self.note_mode = False
        self.completed = False
        self.start_time = time.time()
        self.elapsed_when_completed = 0
        self.message = "빈칸을 선택하고 숫자를 입력하세요."

    def set_difficulty(self, level):
        if level not in DIFFICULTIES:
            return

        self.difficulty = level
        self.new_game()

    def can_edit_selected(self):
        if self.selected is None:
            return False

        row, col = self.selected
        return not self.fixed[row][col]

    def enter_number(self, number):
        if self.completed or not self.can_edit_selected():
            return

        row, col = self.selected

        if self.note_mode:
            if self.board[row][col] != 0:
                return

            if number in self.notes[row][col]:
                self.notes[row][col].remove(number)
            else:
                self.notes[row][col].add(number)

            self.message = "메모를 입력했습니다."
            return

        self.board[row][col] = number
        self.notes[row][col].clear()
        self.errors.discard((row, col))

        if number != self.solution[row][col]:
            self.message = "입력했습니다. 검사 버튼으로 확인할 수 있습니다."
        else:
            self.remove_note_from_related(row, col, number)
            self.message = "숫자를 입력했습니다."

        self.check_completion()

    def erase_selected(self):
        if self.completed or not self.can_edit_selected():
            return

        row, col = self.selected
        self.board[row][col] = 0
        self.notes[row][col].clear()
        self.errors.discard((row, col))
        self.message = "선택한 칸을 지웠습니다."

    def remove_note_from_related(self, row, col, number):
        for c in range(9):
            self.notes[row][c].discard(number)

        for r in range(9):
            self.notes[r][col].discard(number)

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3

        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                self.notes[r][c].discard(number)

    def give_hint(self):
        if self.completed:
            return

        candidates = [
            (r, c)
            for r in range(9)
            for c in range(9)
            if self.board[r][c] == 0
        ]

        if not candidates:
            self.message = "빈칸이 없습니다."
            return

        if self.selected in candidates:
            row, col = self.selected
        else:
            row, col = random.choice(candidates)

        value = self.solution[row][col]
        self.board[row][col] = value
        self.notes[row][col].clear()
        self.errors.discard((row, col))
        self.selected = (row, col)
        self.remove_note_from_related(row, col, value)
        self.message = f"힌트: 이 칸의 숫자는 {value}입니다."
        self.check_completion()

    def check_answers(self):
        self.errors.clear()
        filled_count = 0

        for row in range(9):
            for col in range(9):
                value = self.board[row][col]

                if value != 0:
                    filled_count += 1

                if value != 0 and value != self.solution[row][col]:
                    self.errors.add((row, col))

        if self.errors:
            self.message = f"틀린 칸이 {len(self.errors)}개 있습니다."
        elif filled_count < 81:
            self.message = "현재까지 입력한 숫자는 모두 맞습니다."
        else:
            self.check_completion()

    def check_completion(self):
        if self.board == self.solution:
            self.completed = True
            self.elapsed_when_completed = int(time.time() - self.start_time)
            self.errors.clear()
            self.message = "축하합니다! 스도쿠를 완성했습니다."

    def get_elapsed_time(self):
        if self.completed:
            elapsed = self.elapsed_when_completed
        else:
            elapsed = int(time.time() - self.start_time)

        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"

    def screen_to_cell(self, pos):
        x, y = pos

        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return None

        return y // CELL_SIZE, x // CELL_SIZE

    def related_to_selected(self, row, col):
        if self.selected is None:
            return False

        selected_row, selected_col = self.selected

        same_row = row == selected_row
        same_col = col == selected_col
        same_box = (
            row // 3 == selected_row // 3
            and col // 3 == selected_col // 3
        )

        return same_row or same_col or same_box

    def draw_grid_background(self):
        self.screen.fill(BG_COLOR)

        selected_value = 0

        if self.selected is not None:
            sr, sc = self.selected
            selected_value = self.board[sr][sc]

        for row in range(9):
            for col in range(9):
                rect = pygame.Rect(
                    col * CELL_SIZE,
                    row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )

                color = BG_COLOR

                if self.related_to_selected(row, col):
                    color = RELATED_COLOR

                if (
                    selected_value != 0
                    and self.board[row][col] == selected_value
                ):
                    color = SAME_NUMBER_COLOR

                if self.selected == (row, col):
                    color = SELECTED_COLOR

                pygame.draw.rect(self.screen, color, rect)

    def draw_grid_lines(self):
        for index in range(10):
            width = 4 if index % 3 == 0 else 1
            color = GRID_COLOR if width == 4 else THIN_GRID

            position = index * CELL_SIZE

            pygame.draw.line(
                self.screen,
                color,
                (position, 0),
                (position, GRID_SIZE),
                width,
            )

            pygame.draw.line(
                self.screen,
                color,
                (0, position),
                (GRID_SIZE, position),
                width,
            )

    def draw_numbers(self):
        for row in range(9):
            for col in range(9):
                value = self.board[row][col]
                center = (
                    col * CELL_SIZE + CELL_SIZE // 2,
                    row * CELL_SIZE + CELL_SIZE // 2,
                )

                if value != 0:
                    if (row, col) in self.errors:
                        color = ERROR_COLOR
                    elif self.fixed[row][col]:
                        color = FIXED_NUMBER_COLOR
                    else:
                        color = USER_NUMBER_COLOR

                    surface = self.number_font.render(
                        str(value),
                        True,
                        color,
                    )
                    self.screen.blit(
                        surface,
                        surface.get_rect(center=center),
                    )
                elif self.notes[row][col]:
                    self.draw_notes(row, col)

    def draw_notes(self, row, col):
        for number in self.notes[row][col]:
            note_row = (number - 1) // 3
            note_col = (number - 1) % 3

            x = (
                col * CELL_SIZE
                + note_col * (CELL_SIZE // 3)
                + CELL_SIZE // 6
            )
            y = (
                row * CELL_SIZE
                + note_row * (CELL_SIZE // 3)
                + CELL_SIZE // 6
            )

            surface = self.note_font.render(
                str(number),
                True,
                NOTE_COLOR,
            )
            self.screen.blit(
                surface,
                surface.get_rect(center=(x, y)),
            )

    def draw_side_panel(self):
        pygame.draw.rect(
            self.screen,
            PANEL_BG,
            (GRID_SIZE, 0, SIDE_PANEL_WIDTH, WINDOW_HEIGHT),
        )

        x = GRID_SIZE + 20

        title = self.title_font.render(
            "Pygame 스도쿠",
            True,
            PANEL_TEXT,
        )
        self.screen.blit(title, (x, 18))

        difficulty_name = DIFFICULTIES[self.difficulty]["name"]

        info = self.small_font.render(
            f"난이도: {difficulty_name}  |  시간: {self.get_elapsed_time()}",
            True,
            PANEL_MUTED,
        )
        self.screen.blit(info, (x, 58))

        self.draw_wrapped_text(
            self.message,
            self.text_font,
            PANEL_TEXT,
            pygame.Rect(x, 88, 280, 48),
        )

        for index, button in enumerate(
            self.difficulty_buttons,
            start=1,
        ):
            button.draw(
                self.screen,
                self.small_font,
                active=(index == self.difficulty),
            )

        mode_text = (
            "입력 모드: 메모"
            if self.note_mode
            else "입력 모드: 숫자"
        )
        mode_color = BUTTON_ACTIVE if self.note_mode else PANEL_MUTED

        self.screen.blit(
            self.text_font.render(mode_text, True, mode_color),
            (x, 311),
        )

        for button in self.number_buttons:
            button.draw(self.screen, self.button_font)

        for button in self.action_buttons:
            active = button.action == "note" and self.note_mode
            button.draw(
                self.screen,
                self.button_font,
                active=active,
            )

        help_lines = [
            "숫자 키 1~9: 입력",
            "0 또는 Backspace: 지우기",
            "M: 메모 모드",
            "H: 힌트  C: 검사  N: 새 게임",
        ]

        help_y = 660

        for line in help_lines:
            surface = self.small_font.render(
                line,
                True,
                PANEL_MUTED,
            )
            self.screen.blit(surface, (x, help_y))
            help_y += 22

    def draw_wrapped_text(self, text, font, color, rect):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            test = f"{current} {word}".strip()

            if font.size(test)[0] <= rect.width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        y = rect.top

        for line in lines:
            surface = font.render(line, True, color)
            self.screen.blit(surface, (rect.left, y))
            y += font.get_height() + 3

    def draw(self):
        self.draw_grid_background()
        self.draw_numbers()
        self.draw_grid_lines()
        self.draw_side_panel()

    def handle_panel_click(self, pos):
        for button in self.difficulty_buttons:
            if button.rect.collidepoint(pos):
                level = int(button.action.split("_")[-1])
                self.set_difficulty(level)
                return

        for button in self.number_buttons:
            if button.rect.collidepoint(pos):
                number = int(button.action.split("_")[-1])
                self.enter_number(number)
                return

        for button in self.action_buttons:
            if button.rect.collidepoint(pos):
                if button.action == "note":
                    self.note_mode = not self.note_mode
                    self.message = (
                        "메모 모드를 켰습니다."
                        if self.note_mode
                        else "숫자 입력 모드로 변경했습니다."
                    )
                elif button.action == "erase":
                    self.erase_selected()
                elif button.action == "hint":
                    self.give_hint()
                elif button.action == "check":
                    self.check_answers()
                elif button.action == "new":
                    self.new_game()
                return

    def handle_key(self, key):
        if pygame.K_1 <= key <= pygame.K_9:
            self.enter_number(key - pygame.K_0)
        elif key in (
            pygame.K_0,
            pygame.K_BACKSPACE,
            pygame.K_DELETE,
        ):
            self.erase_selected()
        elif key == pygame.K_m:
            self.note_mode = not self.note_mode
            self.message = (
                "메모 모드를 켰습니다."
                if self.note_mode
                else "숫자 입력 모드로 변경했습니다."
            )
        elif key == pygame.K_h:
            self.give_hint()
        elif key == pygame.K_c:
            self.check_answers()
        elif key == pygame.K_n:
            self.new_game()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            self.handle_key(event.key)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                return

            if event.pos[0] < GRID_SIZE:
                cell = self.screen_to_cell(event.pos)

                if cell is not None:
                    self.selected = cell
            else:
                self.handle_panel_click(event.pos)

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    SudokuGame().run()
