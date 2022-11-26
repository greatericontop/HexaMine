"""The actual game class."""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame
from pygame import draw

from core import CoreGame
from utils import clear_canvas, draw_centered_text, draw_hexagon

if TYPE_CHECKING:
    from main import Main


TITLE_W = 270
TITLE_H = 35
RESULT_W = 85
RESULT_H = 20
RESULT_X_OFFSET = 180

class Playing(enum.Enum):
    MENU = 0
    CORE_GAME = 1
    ENDING = 2


@dataclass
class Game:
    main: Main
    canvas: pygame.Surface

    core: CoreGame = field(init=False, default=None)
    playing: Playing = field(init=False, default=Playing.MENU)
    last_game_mode: str = field(init=False, default=None)
    endpoint: int = field(init=False, default=0)

    def __post_init__(self):
        self.easy_rect = pygame.Rect(self.main.x_center-TITLE_W, 250-TITLE_H, 2*TITLE_W, 2*TITLE_H)
        self.medium_rect = pygame.Rect(self.main.x_center-TITLE_W, 375-TITLE_H, 2*TITLE_W, 2*TITLE_H)
        self.hard_rect = pygame.Rect(self.main.x_center-TITLE_W, 500-TITLE_H, 2*TITLE_W, 2*TITLE_H)
        self.again_rect = pygame.Rect(self.main.x_center-RESULT_W, 575-RESULT_H, 2*RESULT_W, 2*RESULT_H)
        self.menu_rect = pygame.Rect(self.main.x_center-RESULT_X_OFFSET-RESULT_W, 575-RESULT_H, 2*RESULT_W, 2*RESULT_H)
        self.score_rect = pygame.Rect(self.main.x_center+RESULT_X_OFFSET-RESULT_W, 575-RESULT_H, 2*RESULT_W, 2*RESULT_H)

    def run_menu(self) -> None:
        self.playing = Playing.MENU
        clear_canvas(self.canvas)
        font = pygame.font.Font('assets/liberationserif.ttf', 50)
        # title
        draw_centered_text(self.canvas, font.render('HEXAMINE', True, 0xff55ffff),
                           self.main.x_center, 90)
        draw_hexagon(self.canvas, self.main.x_center-200, 90, 37.5, 0xff55ff)
        draw_hexagon(self.canvas, self.main.x_center+200, 90, 37.5, 0xff55ff)
        # difficulty buttons
        draw.rect(self.canvas, 0x00aa00, self.easy_rect)
        draw_centered_text(self.canvas, font.render('Easy Difficulty', True, 0xffffffff),
                           self.main.x_center, 250)
        draw.rect(self.canvas, 0xffaa00, self.medium_rect)
        draw_centered_text(self.canvas, font.render('Medium Difficulty', True, 0xffffffff),
                           self.main.x_center, 375)
        draw.rect(self.canvas, 0xaa0000, self.hard_rect)
        draw_centered_text(self.canvas, font.render('Hard Difficulty', True, 0xffffffff),
                           self.main.x_center, 500)

    def run_result_menu(self) -> None:
        font = pygame.font.Font('assets/liberationserif.ttf', 30)
        draw.rect(self.canvas, 0x00aa00, self.again_rect)
        draw_centered_text(self.canvas, font.render('Play Again', True, 0xffffffff),
                           self.main.x_center, 575)
        draw.rect(self.canvas, 0x00aa00, self.menu_rect)
        draw_centered_text(self.canvas, font.render('Main Menu', True, 0xffffffff),
                           self.main.x_center-RESULT_X_OFFSET, 575)
        draw.rect(self.canvas, 0x00aa00, self.score_rect)
        draw_centered_text(self.canvas, font.render('Leaderboards', True, 0xffffffff),
                           self.main.x_center+RESULT_X_OFFSET, 575)

    def run_easy_difficulty(self) -> None:
        self.playing = Playing.CORE_GAME
        self.last_game_mode = 'easy'
        clear_canvas(self.canvas)
        width, height = 11, 8
        mine_count = 14
        self.core = CoreGame(self.main, self.canvas, width, height, mine_count)
        self.core.init()

    def run_medium_difficulty(self) -> None:
        self.playing = Playing.CORE_GAME
        self.last_game_mode = 'medium'
        clear_canvas(self.canvas)
        width, height = 21, 13
        mine_count = 48
        self.core = CoreGame(self.main, self.canvas, width, height, mine_count)
        self.core.init()

    def run_hard_difficulty(self) -> None:
        self.playing = Playing.CORE_GAME
        self.last_game_mode = 'hard'
        clear_canvas(self.canvas)
        width, height = 31, 17
        mine_count = 110
        self.core = CoreGame(self.main, self.canvas, width, height, mine_count)
        self.core.init()

    #

    def tick_loop(self) -> None:
        """Called every tick/frame.
        Redrawing the canvas is mandatory here (otherwise funny things happen when resizing).
        """
        if self.playing == Playing.MENU:
            self.run_menu()
        elif self.playing == Playing.CORE_GAME:
            clear_canvas(self.canvas)
            self.core.draw_all()
        elif self.playing == Playing.ENDING:
            clear_canvas(self.canvas)
            self.core.draw_all()
            self.run_result_menu()
            font = pygame.font.Font('assets/liberationserif.ttf', 50)
            if self.core.game_won:
                draw_centered_text(self.canvas, font.render('YOU WON!', True, 0xff55ffff), self.main.x_center, 40)
            else:
                draw_centered_text(self.canvas, font.render('GAME OVER', True, 0xff55ffff), self.main.x_center, 40)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle an event."""
        if self.playing == Playing.MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.easy_rect.collidepoint(mouse_pos):
                    self.run_easy_difficulty()
                elif self.medium_rect.collidepoint(mouse_pos):
                    self.run_medium_difficulty()
                elif self.hard_rect.collidepoint(mouse_pos):
                    self.run_hard_difficulty()

        elif self.playing == Playing.CORE_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                still_alive = self.core.handle_click(event)
                if not still_alive:
                    # game over
                    self.playing = Playing.ENDING
                    clear_canvas(self.canvas)
                    self.core.handle_defeat()
                    self.core.game_won = False
                    return
                game_won = self.core.check_victory()
                if game_won:
                    self.playing = Playing.ENDING
                    clear_canvas(self.canvas)
                    self.core.handle_victory()
                    self.core.game_won = True

        elif self.playing == Playing.ENDING:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.again_rect.collidepoint(mouse_pos):
                    if self.last_game_mode == 'easy':
                        self.run_easy_difficulty()
                    elif self.last_game_mode == 'medium':
                        self.run_medium_difficulty()
                    elif self.last_game_mode == 'hard':
                        self.run_hard_difficulty()
                elif self.menu_rect.collidepoint(mouse_pos):
                    self.playing = Playing.MENU
                    self.run_menu()
