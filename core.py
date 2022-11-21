"""Game class."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import pygame

from utils import *


NEARBY_TILES = [(1, -1), (-1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
MINE_COLOR = {1: 0xf9ffc1ff, 2: 0x82d48cff, 3: 0xb20000ff, 4: 0x6e44b0ff, 5: 0x005a88ff, 6: 0x340d0dff}
HEX_COLOR = {0: 0xffffff, 1: 0xf9ffc1, 2: 0x82d48c, 3: 0xb20000, 4: 0x6e44b0, 5: 0x005a88, 6: 0x340d0d}


@dataclass
class CoreGame:
    canvas: pygame.Surface
    width: int
    height: int
    mine_count: int
    board: dict[tuple[int, int], TileState] = field(init=False, default_factory=dict)
    font: pygame.font.SysFont = field(init=False)
    font_nerd: pygame.font.SysFont = field(init=False)
    mines_set: bool = field(init=False, default=False)

    def __post_init__(self):
        self.font = pygame.font.Font('assets/liberationserif.ttf', 24)
        self.font_nerd = pygame.font.Font('assets/jetbrainsmononerd.ttf', 24)

    @property
    def x_0(self) -> float:
        # TODO: -1.5 is slightly questionable
        return 400 - (self.width-1.5)/2 * 1.7320508075688772*self.hexagon_radius

    @property
    def y_0(self) -> float:
        return 300 - (self.height-0.5)/2 * 1.7320508075688772*self.hexagon_radius

    @property
    def hexagon_radius(self) -> float:
        return (600 - 120) / (self.height*2)

    @property
    def size(self) -> float:
        return 1.7320508075688772*self.hexagon_radius + 3

    def _to_canvas(self, game_i: int, game_j: int) -> tuple[float, float]:
        """Convert game i,j to canvas x,y."""
        # Slightly larger than 2*apothem, so they're almost touching but not quite.
        # Since `i` is (0; 1) and `j` is (sqrt3/2; 1/2), we matrix multiply.
        x = self.x_0 + self.size * (0.8660254037844386 * game_j)
        y = self.y_0 + self.size * (game_i + 0.5 * game_j)
        return x, y

    def _to_game(self, canvas_x: int, canvas_y: int) -> tuple[float, float]:
        """Convert canvas x,y to game i,j."""
        x = (canvas_x - self.x_0) / self.size
        y = (canvas_y - self.y_0) / self.size
        # multiply by inverse (-1/sqrt3, 1 ; -2/sqrt3, 0)
        game_i = -0.5773502691896258 * x + y
        game_j = 1.1547005383792517 * x
        return game_i, game_j

    def _get_nearby_mines(self, i: int, j: int) -> int:
        """Get the nearby"""
        nearby_mine_count = 0
        for i_off, j_off in NEARBY_TILES:
            i1 = i + i_off
            j1 = j + j_off
            if (i1, j1) in self.board and self.board[(i1, j1)] in {TileState.CLOSED_MINED, TileState.FLAG_MINED, TileState.DEAD}:
                nearby_mine_count += 1
        return nearby_mine_count

    def _get_nearby_flagged(self, i: int, j: int) -> int:
        """Get the nearby flagged"""
        nearby_flagged_count = 0
        for i_off, j_off in NEARBY_TILES:
            i1 = i + i_off
            j1 = j + j_off
            if (i1, j1) in self.board and self.board[(i1, j1)] in {TileState.FLAG_MINED, TileState.FLAG_SAFE}:
                nearby_flagged_count += 1
        return nearby_flagged_count

    def _estimated_mines_remaining(self) -> int:
        """Get the estimated (flags) count of mines left."""
        flags = len([None for tile in self.board if self.board[tile] in {TileState.FLAG_SAFE, TileState.FLAG_MINED}])
        return self.mine_count - flags

    def show_all_mines(self, win: bool = False) -> None:
        """Shows all mines"""
        for i, j in self.board:
            if self.board[(i, j)] == TileState.CLOSED_MINED:
                if win:
                    self.board[(i, j)] = TileState.FLAG_MINED
                else:
                    self.board[(i, j)] = TileState.DEAD

    def check_victory(self) -> bool:
        """Check if you win or not."""
        opened = len([None for tile in self.board if self.board[tile] == TileState.OPEN_SAFE])
        area = self.width*self.height - (self.width-1)//2
        return opened == area - self.mine_count

    #

    def init(self) -> None:
        """Draw and initialize stuff, in-place."""
        MAIN_WIDTH = self.width - 1
        MAIN_HEIGHT = self.height - MAIN_WIDTH // 2 - 1
        assert MAIN_WIDTH % 2 == 0
        # top section
        for i in range(-MAIN_WIDTH // 2, 0):
            j_min = -2 * i
            j_max = MAIN_WIDTH
            for j in range(j_min, j_max + 1):
                self.board[(i, j)] = TileState.NOT_YET_GENERATED  # placeholder
                # TODO: draw these in the main tick loop????
                x, y = self._to_canvas(i, j)
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0xff5555)
        # normal section
        for i in range(0, MAIN_HEIGHT + 1):
            for j in range(0, MAIN_WIDTH + 1):
                self.board[(i, j)] = TileState.NOT_YET_GENERATED
        # bottom section
        for i in range(MAIN_HEIGHT + 1, MAIN_HEIGHT + MAIN_WIDTH // 2 + 1):
            j_min = 0
            n = i - MAIN_HEIGHT
            j_max = MAIN_WIDTH - 2 * n
            for j in range(j_min, j_max + 1):
                self.board[(i, j)] = TileState.NOT_YET_GENERATED

    def set_mines(self, remove_this: tuple[int, int]) -> None:
        """Set the mines in the board.
        :remove: denotes what to NOT put a mine on, which is the first tile that was opened
        """
        tiles = list(self.board.keys())
        tiles.remove(remove_this)
        random.shuffle(tiles)  # shuffle a copy and take the top few
        for i, coordinate in enumerate(tiles):
            self.board[coordinate] = TileState.CLOSED_MINED if i < self.mine_count else TileState.CLOSED_SAFE

    def draw_all(self) -> None:
        """Draw the tiles."""
        if self._estimated_mines_remaining() != 0:
            self.canvas.blit(self.font.render(str(self._estimated_mines_remaining()), True, 0x00ff00ff), (5, 5))

        for (i, j), state in self.board.items():
            x, y = self._to_canvas(i, j)
            if state in {TileState.NOT_YET_GENERATED, TileState.CLOSED_SAFE, TileState.CLOSED_MINED}:
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0x666666)
            elif state in {TileState.OPEN_SAFE}:
                nearby_mine_count = self._get_nearby_mines(i, j)
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, HEX_COLOR[nearby_mine_count])
                if nearby_mine_count != 0:
                    draw_centered_text(self.canvas, self.font.render(str(nearby_mine_count), True, MINE_COLOR[nearby_mine_count]), x, y)
            elif state in {TileState.FLAG_SAFE, TileState.FLAG_MINED}:
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0xff5555)
                draw_centered_text(self.canvas, self.font_nerd.render('\uf73f', True, 0xffffff), x, y)
            elif state == TileState.DEAD:
                draw_hexagon(self.canvas, x, y, self.hexagon_radius, 0xff5555)
                draw_centered_text(self.canvas, self.font_nerd.render('\ufb8f', True, 0xff5555ff), x, y)

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
        current_type = self.board[(i, j)]
        if current_type == TileState.CLOSED_MINED:
            self.board[(i, j)] = TileState.DEAD
            return False
        if current_type in {TileState.NOT_YET_GENERATED, TileState.CLOSED_SAFE}:
            self.board[(i, j)] = TileState.OPEN_SAFE
            if not self.mines_set:  # first click
                self.set_mines(remove_this=(i, j))
                self.mines_set = True
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
        if current_type == TileState.OPEN_SAFE and clicked_by_user:  # chord (open nearby)
            if self._get_nearby_mines(i, j) == self._get_nearby_flagged(i, j):
                for i_off, j_off in NEARBY_TILES:
                    i1 = i + i_off
                    j1 = j + j_off
                    if (i1, j1) in self.board:
                        if self.board[(i1, j1)] not in {TileState.FLAG_SAFE, TileState.FLAG_MINED}:
                            result = self.open_tile(i1, j1, False)
                            if not result:
                                return False
            return True
        return True

    def flag_tile(self, i: int, j: int):
        current_type = self.board[(i, j)]
        if current_type in {TileState.CLOSED_MINED, TileState.CLOSED_SAFE}:
            change_state = {TileState.CLOSED_MINED: TileState.FLAG_MINED, TileState.CLOSED_SAFE: TileState.FLAG_SAFE}
            self.board[(i, j)] = change_state[current_type]
        if current_type in {TileState.FLAG_SAFE, TileState.FLAG_MINED}:
            change_state = {TileState.FLAG_MINED: TileState.CLOSED_MINED, TileState.FLAG_SAFE: TileState.CLOSED_SAFE}
            self.board[(i, j)] = change_state[current_type]
