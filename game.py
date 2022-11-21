"""The actual game class."""

from __future__ import annotations

import math
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

RESULT_W = 80
RESULT_H = 20
AGAIN_RECT = pygame.Rect(X_CENTER-RESULT_W, 575-RESULT_H, 2*RESULT_W, 2*RESULT_H)
MENU_RECT = pygame.Rect(230-RESULT_W, 575-RESULT_H, 2*RESULT_W, 2*RESULT_H)

FPS = 60


@dataclass
class Game:
    canvas: pygame.Surface
    core: CoreGame = field(init=False, default=None)
    playing: bool = field(init=False, default=False)
    show_result_menu: bool = field(init=False, default=False)
    last_game_mode: str = field(init=False, default=None)
    endpoint: int = field(init=False, default=0)

    def _calculate_time(self, tick: int) -> str:
        minutes = int(math.floor(tick / 60))
        seconds = tick % 60
        return f'{minutes:02d}:{seconds:02d}'

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

    def run_result_menu(self) -> None:
        font = pygame.font.Font('assets/liberationserif.ttf', 30)
        draw.rect(self.canvas, 0x00aa00, AGAIN_RECT)
        draw_centered_text(self.canvas, font.render('Play Again', True, 0xffffffff), X_CENTER, 575)
        draw.rect(self.canvas, 0x00aa00, MENU_RECT)
        draw_centered_text(self.canvas, font.render('Main Menu', True, 0xffffffff), 230, 575)

    def run_easy_difficulty(self) -> None:
        self.playing = True
        self.last_game_mode = 'easy'
        clear_canvas(self.canvas)
        # width, height, mine_count = 5, 4, 4
        width, height = 11, 8
        mine_count = 14
        self.core = CoreGame(canvas=self.canvas, width=width, height=height, mine_count=mine_count)
        self.core.init()

    def run_medium_difficulty(self) -> None:
        self.playing = True
        self.last_game_mode = 'medium'
        clear_canvas(self.canvas)
        width, height = 21, 13
        mine_count = 48
        self.core = CoreGame(canvas=self.canvas, width=width, height=height, mine_count=mine_count)
        self.core.init()

    def run_hard_difficulty(self) -> None:
        self.playing = True
        self.last_game_mode = 'hard'
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
            self.canvas.blit(self.core.font.render(self._calculate_time(int((number_tick - self.endpoint) / FPS)), True, 0x5555ffff), (730, 5))
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
                    self.show_result_menu = True
                    self.core.show_all_mines()
                    clear_canvas(self.canvas)
                    self.core.draw_all(show_flagged_incorrect=True)
                    self.core = None
                    font = pygame.font.Font('assets/liberationserif.ttf', 50)
                    draw_centered_text(self.canvas, font.render('GAME OVER', True, 0xff55ffff), 400, 40)
                    return
                game_won = self.core.check_victory()
                if game_won:
                    self.playing = False
                    self.show_result_menu = True
                    self.core.show_all_mines(win=True)
                    clear_canvas(self.canvas)
                    self.core.draw_all()
                    self.core = None
                    font = pygame.font.Font('assets/liberationserif.ttf', 50)
                    draw_centered_text(self.canvas, font.render('YOU WON!', True, 0xff55ffff), 400, 40)
        elif self.show_result_menu:
            self.run_result_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if AGAIN_RECT.collidepoint(mouse_pos):
                    if self.last_game_mode == 'easy':
                        self.run_easy_difficulty()
                    elif self.last_game_mode == 'medium':
                        self.run_medium_difficulty()
                    elif self.last_game_mode == 'hard':
                        self.run_hard_difficulty()
                elif MENU_RECT.collidepoint(mouse_pos):
                    self.show_result_menu = False
                    self.run_menu()
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if EASY_RECT.collidepoint(mouse_pos):
                    self.run_easy_difficulty()
                elif MEDIUM_RECT.collidepoint(mouse_pos):
                    self.run_medium_difficulty()
                elif HARD_RECT.collidepoint(mouse_pos):
                    self.run_hard_difficulty()

