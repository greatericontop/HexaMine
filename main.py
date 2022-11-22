"""HexaMine is a game where you have to find the mines in a hexagonal grid."""

# <License to be added later.>

from __future__ import annotations

__version__ = 'beta-1.0.0'

from dataclasses import dataclass, field
from typing import ClassVar

import pygame

from game import Game


@dataclass
class Main:
    TPS: ClassVar[int] = 60

    number_tick: int = field(init=False, default=0)

    def main(self) -> None:
        pygame.init()
        logo = pygame.image.load('assets/logo.png')
        pygame.display.set_icon(logo)
        pygame.display.set_caption(f'HexaMine {__version__}')
        canvas = pygame.display.set_mode((800, 600))
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
                game.handle_event(event)


if __name__ == '__main__':
    Main().main()
