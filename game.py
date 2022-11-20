"""The actual game class."""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from core import CoreGame


@dataclass
class Game:
    canvas: pygame.Surface

    core: CoreGame = field(init=False)

    def run_easy_difficulty(self) -> None:
        width, height = 11, 8
        mine_count = 10
        self.core = CoreGame(canvas=self.canvas, width=width, height=height, mine_count=mine_count)
        self.core.init()

    def tick_loop(self) -> None:
        """Called every tick loop."""
        self.core.draw_all()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle an event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.core.handle_click(event)
