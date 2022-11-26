"""HexaMine is a game where you have to find the mines in a hexagonal grid."""

# <License to be added later.>

from __future__ import annotations

__version__ = 'beta-1.1.0-nightly'

from dataclasses import dataclass, field
from typing import ClassVar

import pygame

from game import Game


WINDOW_FLAGS = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF


@dataclass
class Main:
    TPS: ClassVar[int] = 60
    display_width: int = 800  # TODO: make these resizable (with a minimum of 800x600) later
    display_height: int = 600

    number_tick: int = field(init=False, default=0)

    @property
    def x_center(self) -> int:
        return self.display_width // 2

    @property
    def y_center(self) -> int:
        return self.display_height // 2

    def main(self) -> None:
        pygame.init()
        logo = pygame.image.load('assets/logo.png')
        pygame.display.set_icon(logo)
        pygame.display.set_caption(f'HexaMine {__version__}')
        canvas = pygame.display.set_mode((self.display_width, self.display_height), WINDOW_FLAGS)
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
                    self.display_width = event.w
                    self.display_height = event.h
                    # while we would love to have a minimum size, that literally does not work in pygame
                game.handle_event(event)


if __name__ == '__main__':
    Main().main()
