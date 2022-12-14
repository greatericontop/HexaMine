"""Game class."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

from utils import FlagType, Tile, draw_hexagon, TileType, draw_centered_text, draw_right_align_text

if TYPE_CHECKING:
    from main import Main


NEARBY_TILES = [(1, -1), (-1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
MINE_COLOR = {1: 0xf9ffc1ff, 2: 0x82d48cff, 3: 0xff6565ff, 4: 0x6e44b0ff, 5: 0x005a88ff, 6: 0x340d0dff}
HEX_COLOR = {0: 0xffffff, 1: 0xeaff28, 2: 0x308d3c, 3: 0xff3232, 4: 0x352054, 5: 0x00273c, 6: 0x340d0d}

BORDER_BUFFER = 2.75


@dataclass
class CoreGame:
    main: Main
    canvas: pygame.Surface
    width: int
    height: int
    mine_count: int

    board: dict[tuple[int, int], Tile] = field(init=False, default_factory=dict)
    mines_set: bool = field(init=False, default=False)
    tick_start: int = field(init=False, default=None)
    frozen_timer_ticks: int = field(init=False, default=None)
    game_won: bool = field(init=False, default=False)  # managed by other classes

    font: pygame.font.Font = field(init=False)
    font_nerd_16: pygame.font.Font = field(init=False)
    font_nerd_20: pygame.font.Font = field(init=False)
    font_nerd: pygame.font.Font = field(init=False)
    font_nerd_28: pygame.font.Font = field(init=False)
    font_nerd_34: pygame.font.Font = field(init=False)

    def __post_init__(self):
        self.font = pygame.font.Font('assets/liberationserif.ttf', 24)
        self.font_nerd_16 = pygame.font.Font('assets/jetbrainsmononerd.ttf', 16)
        self.font_nerd_20 = pygame.font.Font('assets/jetbrainsmononerd.ttf', 20)
        self.font_nerd = pygame.font.Font('assets/jetbrainsmononerd.ttf', 24)
        self.font_nerd_28 = pygame.font.Font('assets/jetbrainsmononerd.ttf', 28)
        self.font_nerd_34 = pygame.font.Font('assets/jetbrainsmononerd.ttf', 34)

    @property
    def x_0(self) -> float:
        """Find the X location of the top-left hexagon to center the board."""
        # this one is more complicated
        # calculate the X using the J
        center_j = (self.width-1) // 2
        x_off = self.size * (0.8660254037844386 * center_j)
        return self.main.x_center - x_off

    @property
    def y_0(self) -> float:
        """Find the Y location of the top-left hexagon to center the board."""
        # the line through the middle will always have (self.height - 1) hexagons
        # distance to the edge of the middle (smaller column) == center point of big column
        return self.main.y_center - self.size * (self.height-1)/2

    @property
    def hexagon_radius(self) -> float:
        # need to subtract BORDER_BUFFER/2 because there's (approximately) 1 border buffer for each hexagon
        # both of these are approximations, but they get close enough that the difference is irrelevant
        x_limit = (self.main.x_size - 50) / ((self.width-1)*1.5 + 2) - BORDER_BUFFER/2
        y_limit = (self.main.y_size - 140) / (self.height * 1.7320508075688772) - BORDER_BUFFER/2
        return min(x_limit, y_limit)

    @property
    def size(self) -> float:
        return 1.7320508075688772*self.hexagon_radius + BORDER_BUFFER

    def _to_canvas(self, game_i: int, game_j: int) -> tuple[float, float]:
        """Convert game i,j to canvas x,y."""
        # Slightly larger than 2*apothem, so they're almost touching but not quite.
        # Since `i` is (0; 1) and `j` is (sqrt3/2; 1/2), we matrix multiply.
        x = self.x_0 + self.size * (0.8660254037844386*game_j)
        y = self.y_0 + self.size * (game_i + 0.5*game_j)
        return x, y

    def _to_game(self, canvas_x: int, canvas_y: int) -> tuple[float, float]:
        """Convert canvas x,y to game i,j."""
        x = (canvas_x - self.x_0) / self.size
        y = (canvas_y - self.y_0) / self.size
        # multiply by inverse (-1/sqrt3, 1 ; -2/sqrt3, 0)
        game_i = -0.5773502691896258*x + y
        game_j = 1.1547005383792517*x
        return game_i, game_j

    def _get_nearby_mines(self, i: int, j: int) -> int:
        """Get the nearby mines."""
        nearby_mine_count = 0
        for i_off, j_off in NEARBY_TILES:
            i1 = i + i_off
            j1 = j + j_off
            if (i1, j1) in self.board and self.board[(i1, j1)].mined:
                nearby_mine_count += 1
        return nearby_mine_count

    def _get_nearby_flagged(self, i: int, j: int) -> int:
        """Get the nearby flagged tiles."""
        nearby_flagged_count = 0
        for i_off, j_off in NEARBY_TILES:
            i1 = i + i_off
            j1 = j + j_off
            if (i1, j1) in self.board and self.board[(i1, j1)].flag == FlagType.FLAGGED:
                nearby_flagged_count += 1
        return nearby_flagged_count

    def _no_nearby_question(self, i: int, j: int) -> bool:
        """Get whether there are no nearby question flags."""
        for i_off, j_off in NEARBY_TILES:
            i1 = i + i_off
            j1 = j + j_off
            if (i1, j1) in self.board and self.board[(i1, j1)].flag == FlagType.QUESTION:
                return False
        return True

    def estimated_mines_remaining(self) -> tuple[int, int, int]:
        """Get the estimated (flags) count of mines left.
        Return a tuple of
            0. the mine count with only full flags
            1. the mine count also including question flags
            2. the number of incorrect full flags (NOT including questions)
        """
        strict_flags = 0
        questions = 0
        incorrect_strict_flags = 0
        for tile in self.board.values():
            if tile.flag == FlagType.FLAGGED:
                strict_flags += 1
                questions += 1
                if tile.safe:
                    incorrect_strict_flags += 1
            elif tile.flag == FlagType.QUESTION:
                questions += 1
        return self.mine_count - strict_flags, self.mine_count - questions, incorrect_strict_flags

    #
    #
    #

    def init(self) -> None:
        """Draw and initialize stuff, in-place."""
        MAIN_WIDTH = self.width - 1
        MAIN_HEIGHT = self.height - MAIN_WIDTH//2 - 1
        assert MAIN_WIDTH % 2 == 0
        # top section
        for i in range(-MAIN_WIDTH//2, 0):
            j_min = -2 * i
            j_max = MAIN_WIDTH
            for j in range(j_min, j_max+1):
                self.board[(i, j)] = Tile()
        # normal section
        for i in range(0, MAIN_HEIGHT+1):
            for j in range(0, MAIN_WIDTH+1):
                self.board[(i, j)] = Tile()
        # bottom section
        for i in range(MAIN_HEIGHT+1, MAIN_HEIGHT + MAIN_WIDTH//2 + 1):
            j_min = 0
            n = i - MAIN_HEIGHT
            j_max = MAIN_WIDTH - 2*n
            for j in range(j_min, j_max+1):
                self.board[(i, j)] = Tile()

    def set_mines(self, remove_this: tuple[int, int]) -> None:
        """Set the mines in the board.
        :remove: denotes what to NOT put a mine on, which is the first tile that was opened
        """
        tiles = list(self.board.keys())
        tiles.remove(remove_this)
        for i_off, j_off in NEARBY_TILES:
            i1 = remove_this[0] + i_off
            j1 = remove_this[1] + j_off
            if (i1, j1) in self.board:
                tiles.remove((i1, j1))
        random.shuffle(tiles)  # shuffle a copy and take the top few
        for i, coordinate in enumerate(tiles):
            assert self.board[coordinate].closed
            self.board[coordinate].tile = TileType.MINE if i < self.mine_count else TileType.SAFE

    #
    #
    #

    def show_all_mines_winning(self) -> None:
        """Shows all mines for a win. All mined locations are flagged."""
        for tile in self.board:
            if self.board[tile].mined:
                assert self.board[tile].closed
                self.board[tile].flag = FlagType.FLAGGED

    def show_all_mines_losing(self) -> None:
        """Shows all mines for a loss."""
        for tile in self.board:
            if self.board[tile].mined:
                if self.board[tile].flag == FlagType.QUESTION:
                    self.board[tile].flag = FlagType.FLAGGED
                elif self.board[tile].flag not in {FlagType.FLAGGED, FlagType.POST_GAME_LOSS_CAUSE}:
                    # POST_GAME_LOSS_CAUSE was set already, and correctly flagged mines keep their flags
                    self.board[tile].flag = FlagType.POST_GAME_LOSS

    def check_victory(self) -> bool:
        """Check if you win or not."""
        opened = len([None for tile in self.board if self.board[tile].open_safe])
        area = self.width*self.height - (self.width-1)//2
        return opened == area - self.mine_count

    def handle_victory(self) -> None:
        """Handle a win."""
        self.show_all_mines_winning()

    def handle_defeat(self) -> None:
        """Handle a loss."""
        self.show_all_mines_losing()

    #

    def draw_all(self, game_ended: bool = False) -> None:
        """Draw the tiles.
        :show_flagged_incorrect: After finishing the game, show incorrect flags.
        """
        # mine count
        strict_mines, question_mines, incorrectly_flagged = self.estimated_mines_remaining()
        if game_ended:
            # when winning, the win handler flags everything and this should be zero
            # when losing, this will display the number of undiscovered mines (how close you were to winning)
            mine_count_text = f'{strict_mines+incorrectly_flagged} \ufb8f'
        elif strict_mines == question_mines or strict_mines <= 0:
            mine_count_text = f'{strict_mines} \ufb8f'
        else:  # only show if different and if there are still mines left that weren't strict flagged
            mine_count_text = f'{strict_mines} ({question_mines}) \ufb8f'
        self.canvas.blit(self.font_nerd_20.render(mine_count_text, True, 0x11ff11ff), (5, 5))
        # timer
        if self.tick_start is None:
            draw_right_align_text(self.canvas, self.font_nerd_20.render('\uf64f', True, 0x5555ffff),
                                  self.main.x_size-5, 5)
        else:
            ticks_passed = self.main.number_tick - self.tick_start if self.frozen_timer_ticks is None  \
                           else self.frozen_timer_ticks
            seconds = ticks_passed // self.main.TPS
            time_text = f'\uf64f {seconds // 60:02d}:{seconds % 60:02d}'
            draw_right_align_text(self.canvas, self.font_nerd_20.render(time_text, True, 0x5555ffff),
                                  self.main.x_size-5, 5)

        for (i, j), state in self.board.items():
            x, y = self._to_canvas(i, j)
            if state.open_safe and state.mined:
                raise RuntimeError(f'open & mined tile found @ {i=} {j=}...')

            # post-game (check this first because these checks are more specific)

            if state.flag == FlagType.POST_GAME_LOSS:
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0xff5555)
                draw_centered_text(self.canvas, self.font_nerd.render('\ufb8f', True, 0xff5555ff), x, y)

            elif state.flag == FlagType.POST_GAME_LOSS_CAUSE:
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0xaa0000)
                draw_centered_text(self.canvas, self.font_nerd_34.render('\ufb8f', True, 0xaa0000ff), x, y)

            # during game

            elif state.flag == FlagType.QUESTION:
                # question flagged (& closed) tile
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0xffa2a2)
                draw_centered_text(self.canvas, self.font_nerd.render('\uf128', True, 0x00aaaaff), x, y)
                if state.safe and game_ended:
                    draw_centered_text(self.canvas, self.font_nerd_28.render('\u2717', True, 0xff3333ff), x, y)

            elif state.flag == FlagType.FLAGGED:
                # flagged (& closed) tile
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0xffa2a2)
                draw_centered_text(self.canvas, self.font_nerd.render('\uf73f', True, 0x55ffffff), x, y)
                if state.safe and game_ended:
                    draw_centered_text(self.canvas, self.font_nerd_28.render('\u2717', True, 0xff3333ff), x, y)

            elif state.closed:
                # closed (& unmarked) tile
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0x404040)

            elif state.open_safe:
                # safe & opened tile (the "normal" opened tile in game)
                nearby_mine_count = self._get_nearby_mines(i, j)
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, HEX_COLOR[nearby_mine_count])
                if nearby_mine_count != 0:
                    draw_centered_text(self.canvas,
                                       self.font.render(str(nearby_mine_count), True, MINE_COLOR[nearby_mine_count]),
                                       x, y)
                else:
                    draw_centered_text(self.canvas, self.font_nerd_16.render('\ueaab', True, 0x666666ff), x, y)

            else:
                raise RuntimeError(f'{i=}, {j=}  |  {state=}')

    def handle_click(self, event: pygame.event.Event) -> bool:
        """Handle a `MOUSEBUTTONDOWN` event. Return whether you're still alive."""
        # check radius (of apothem)
        for i1, j1 in self.board:
            x1, y1 = self._to_canvas(i1, j1)
            distance = math.sqrt((x1 - event.pos[0]) ** 2 + (y1 - event.pos[1]) ** 2)
            # Circle with radius of apothem. This restricts clicking on the edges/corners slightly but is more precise.
            if distance < 0.8660254037844386*self.hexagon_radius - 2:
                if event.button == 1:
                    return self.open_tile(i1, j1)
                if event.button == 3:
                    self.flag_tile(i1, j1)
                    return True
        return True

    def open_tile(self, i: int, j: int, clicked_by_user: bool = True) -> bool:
        """Handle when a player left-clicks a tile. Return whether you're still alive."""
        current_tile = self.board[(i, j)]
        if current_tile.flagged and clicked_by_user:
            # you can't open flags (but if they were auto-opened, they will still open)
            return True
        if current_tile.mined:
            self.board[(i, j)].flag = FlagType.POST_GAME_LOSS_CAUSE
            return False

        if current_tile.closed:  # closed & safe
            self.board[(i, j)].flag = FlagType.OPEN
            if not self.mines_set:  # first click
                self.set_mines(remove_this=(i, j))
                self.mines_set = True
                self.tick_start = self.main.number_tick
            if self._get_nearby_mines(i, j) == 0:
                # if there are no nearby mines, automatically open more
                for i_off, j_off in NEARBY_TILES:
                    i1 = i + i_off
                    j1 = j + j_off
                    if (i1, j1) in self.board:
                        result = self.open_tile(i1, j1, False)
                        if not result:
                            return False
            return True
        if current_tile.open_safe and clicked_by_user:  # chord (open nearby)
            if self._get_nearby_mines(i, j) == self._get_nearby_flagged(i, j) and self._no_nearby_question(i, j):
                for i_off, j_off in NEARBY_TILES:
                    i1 = i + i_off
                    j1 = j + j_off
                    if (i1, j1) in self.board:
                        if not self.board[(i1, j1)].flagged:
                            result = self.open_tile(i1, j1, False)
                            if not result:
                                return False
            return True
        return True

    def flag_tile(self, i: int, j: int):
        current_type = self.board[(i, j)]
        if current_type.flagged:
            self.board[(i, j)].flag = FlagType.NONE_CLOSED
        elif current_type.unmarked:
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                self.board[(i, j)].flag = FlagType.QUESTION
            else:
                self.board[(i, j)].flag = FlagType.FLAGGED
        else:
            assert current_type.open_safe
