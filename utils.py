"""Helper functions"""

from __future__ import annotations

import enum

import pygame
from pygame import draw


class TileState(enum.Enum):
    NOT_YET_GENERATED = 0
    CLOSED_SAFE = 1
    CLOSED_MINED = 2
    OPEN_SAFE = 3


def draw_hexagon(canvas: pygame.Surface,
                 center_x: float, center_y: float,
                 radius: float,
                 color: int | tuple[int, int, int],
                 filled: bool = False,
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
