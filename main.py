"""HexaMine is a game where you have to find the mines in a hexagonal grid."""

# <License to be added later.>

from __future__ import annotations

__version__ = 'alpha-1.0.0'

import pygame

from game import Game
from utils import clear_canvas

FPS = 60


def main() -> None:
    pygame.init()
    pygame.display.set_caption(f'HexaMine {__version__}')
    canvas = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    game = Game(canvas)
    game.run_menu()

    number_tick: int = 0

    while True:
        number_tick += 1
        clock.tick(FPS)
        game.tick_loop(number_tick)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            game.handle_event(event)


if __name__ == '__main__':
    main()
