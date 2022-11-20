"""The actual game class."""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame
from pygame import draw

from core import CoreGame
from utils import clear_canvas, draw_centered_text


TITLE_W = 270
TITLE_H = 35
X_CENTER = 400
EASY_RECT = pygame.Rect(X_CENTER-TITLE_W, 250-TITLE_H, 2*TITLE_W, 2*TITLE_H)
MEDIUM_RECT = pygame.Rect(X_CENTER-TITLE_W, 375-TITLE_H, 2*TITLE_W, 2*TITLE_H)
HARD_RECT = pygame.Rect(X_CENTER-TITLE_W, 500-TITLE_H, 2*TITLE_W, 2*TITLE_H)

FPS = 60


@dataclass
class Game:
    canvas: pygame.Surface
    core: CoreGame = field(init=False, default=None)
    playing: bool = field(init=False, default=False)
    endpoint: int = field(init=False, default=0)

    def run_menu(self) -> None:
        self.playing = False
        clear_canvas(self.canvas)
        font = pygame.font.Font('assets/liberationserif.ttf', 50)
        draw_centered_text(self.canvas, font.render('HEXAMINE', True, 0xff55ffff), 400, 90)
        draw.rect(self.canvas, 0x00aa00, EASY_RECT)
        draw_centered_text(self.canvas, font.render('Easy Difficulty', True, 0xffffffff), X_CENTER, 250)
        draw.rect(self.canvas, 0xffaa00, MEDIUM_RECT)
        draw_centered_text(self.canvas, font.render('Medium Difficulty', True, 0xffffffff), X_CENTER, 375)
        draw.rect(self.canvas, 0xaa0000, HARD_RECT)
        draw_centered_text(self.canvas, font.render('Hard Difficulty', True, 0xffffffff), X_CENTER, 500)

    def run_easy_difficulty(self) -> None:
        self.playing = True
        clear_canvas(self.canvas)
        width, height = 11, 8
        mine_count = 14
        self.core = CoreGame(canvas=self.canvas, width=width, height=height, mine_count=mine_count)
        self.core.init()

    def run_medium_difficulty(self) -> None:
        self.playing = True
        clear_canvas(self.canvas)
        width, height = 21, 13
        mine_count = 48
        self.core = CoreGame(canvas=self.canvas, width=width, height=height, mine_count=mine_count)
        self.core.init()

    def run_hard_difficulty(self) -> None:
        self.playing = True
        clear_canvas(self.canvas)
        width, height = 31, 17
        mine_count = 110
        self.core = CoreGame(canvas=self.canvas, width=width, height=height, mine_count=mine_count)
        self.core.init()

    def tick_loop(self, number_tick: int) -> None:
        """Called every tick loop."""
        if self.playing:
            clear_canvas(self.canvas)
            self.core.draw_all()
            self.canvas.blit(self.core.font.render(str(int((number_tick - self.endpoint) / FPS)), True, 0x5555ffff), (750, 5))
        else:
            self.endpoint = number_tick

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle an event."""
        if self.playing:
            if event.type == pygame.MOUSEBUTTONDOWN:
                still_alive = self.core.handle_click(event)
                if not still_alive:
                    # game over
                    self.playing = False
                    self.core.show_all_mines()
                    self.core.draw_all()
                    self.core = None
                    font = pygame.font.Font('assets/liberationserif.ttf', 50)
                    draw_centered_text(self.canvas, font.render('GAME OVER', True, 0xff55ffff), 400, 40)
                    return
                game_won = self.core.check_victory()
                if game_won:
                    self.playing = False
                    self.core.show_all_mines()
                    self.core.draw_all()
                    self.core = None
                    font = pygame.font.Font('assets/liberationserif.ttf', 50)
                    draw_centered_text(self.canvas, font.render('YOU WON!', True, 0xff55ffff), 400, 40)

        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if EASY_RECT.collidepoint(mouse_pos):
                    self.run_easy_difficulty()
                elif MEDIUM_RECT.collidepoint(mouse_pos):
                    self.run_medium_difficulty()
                elif HARD_RECT.collidepoint(mouse_pos):
                    self.run_hard_difficulty()

