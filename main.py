"""HexaMine is a game where you have to find the mines in a hexagonal grid."""

# <License to be added later.>

from __future__ import annotations

__version__ = 'beta-1.1.0-nightly'

from dataclasses import dataclass, field
from typing import ClassVar

import pygame

from game import Game


WINDOW_FLAGS = pygame.RESIZABLE


@dataclass
class Main:
    TPS: ClassVar[int] = 60
    x_size: int = 800
    y_size: int = 600

    number_tick: int = field(init=False, default=0)

    @property
    def x_center(self) -> int:
        return self.x_size // 2

    @property
    def y_center(self) -> int:
        return self.y_size // 2

    def main(self) -> None:
        pygame.init()
        logo = pygame.image.load('assets/logo.png')
        pygame.display.set_icon(logo)
        pygame.display.set_caption(f'HexaMine {__version__}')
        canvas = pygame.display.set_mode((self.x_size, self.y_size), WINDOW_FLAGS)
        clock = pygame.time.Clock()

        game = Game(self, canvas)
        game.run_menu()

        while True:
            self.number_tick += 1
            clock.tick(self.TPS)
            game.tick_loop()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.VIDEORESIZE:
                    self.x_size = event.w
                    self.y_size = event.h
                    # while we would love to have a minimum size, that literally does not work in pygame
                game.handle_event(event)


if __name__ == '__main__':
    Main().main()
