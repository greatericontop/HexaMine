"""Helper functions"""

from __future__ import annotations

import enum
from dataclasses import dataclass

import pygame
from pygame import draw


class FlagType(enum.Enum):
    OPEN = 0  # tile has been opened
    NONE_CLOSED = 1  # tile is closed and not marked
    FLAGGED = 2  # tile is flagged
    QUESTION = 3  # tile is question flagged
    POST_GAME_LOSS = 4  # shows mines post-game loss (does nothing to safe tiles)
    POST_GAME_LOSS_CAUSE = 5  # shows the mine you clicked on that made you lose


class TileType(enum.Enum):
    NOT_YET_GENERATED = 0
    SAFE = 1
    MINE = 2


@dataclass
class Tile:
    tile: TileType = TileType.NOT_YET_GENERATED
    flag: FlagType = FlagType.NONE_CLOSED

    @property
    def open_safe(self) -> bool:
        return self.flag == FlagType.OPEN

    @property
    def closed(self) -> bool:
        return not self.open_safe

    @property
    def safe(self) -> bool:
        return self.tile in {TileType.SAFE, TileType.NOT_YET_GENERATED}

    @property
    def mined(self) -> bool:
        return not self.safe

    @property
    def unmarked(self) -> bool:
        return self.flag == FlagType.NONE_CLOSED

    @property
    def flagged(self) -> bool:
        return self.flag in {FlagType.FLAGGED, FlagType.QUESTION}


def clear_canvas(canvas: pygame.Surface):
    canvas.fill(0x202020)


def draw_centered_text(canvas: pygame.Surface, text: pygame.Surface, x: float, y: float) -> None:
    text_rect = text.get_rect()
    canvas.blit(text, (x - text_rect.width/2, y - text_rect.height/2))


def draw_right_align_text(canvas: pygame.Surface, text: pygame.Surface, x: float, y: float) -> None:
    text_rect = text.get_rect()
    canvas.blit(text, (x - text_rect.width, y))


def draw_hexagon(canvas: pygame.Surface,
                 center_x: float, center_y: float,
                 radius: float,
                 color: int,
                 ) -> None:
    """Draws a hexagon with the given center and size"""
    apo = radius * 0.8660254037844386
    #   1   2
    # 6   .   3
    #   5   4
    point1 = (center_x - radius/2, center_y - apo)
    point2 = (center_x + radius/2, center_y - apo)
    point3 = (center_x + radius, center_y)
    point4 = (center_x + radius/2, center_y + apo)
    point5 = (center_x - radius/2, center_y + apo)
    point6 = (center_x - radius, center_y)
    draw.aalines(canvas, color, True, (point1, point2, point3, point4, point5, point6))
