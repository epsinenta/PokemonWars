from typing import List, Optional

import pygame

import settings
from classes.button import Button
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.state import State
from elements.global_classes import GuiSettings, sprite_manager
from elements.profile import Profile
from elements.fight_menu import Fight_Menu
from elements.catch_pokemon import Catch_Pokemon
from global_types import SURFACE


class MainMenu(GameStrategy):
    """
    Стратегия главного меню
    """

    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        self.screen.set_alpha(None)
        self._state: Optional[State] = None

    def _fight(self):
        self._state = State(GameState.SWITCH, Fight_Menu)

    def _catch_pokemon(self):
        self._state = State(GameState.SWITCH, Catch_Pokemon)

    def _profile(self):
        self._state = State(GameState.SWITCH, Profile)

    def _set_settings(self):
        pass

    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int):
        centered_x = settings.RESOLUTION[0] // 2 - 200
        centered_y = settings.RESOLUTION[1] // 2
        buttons = [
            Button(centered_x,
                   centered_y - 60, 400, 50, (0, 0, 0), GuiSettings(), f"Catch Pokemon",
                   self._catch_pokemon),
            Button(centered_x,
                   centered_y - 150, 400, 50, (0, 0, 0), GuiSettings(), f"Fight",
                   self._fight),
            Button(1200,
                   20, 300, 50, (0, 0, 0), GuiSettings(), f"Profile",
                   self._profile),
            Button(1525,
                   20, 50, 50, (0, 0, 0), GuiSettings(), f"",
                   self._set_settings),
        ]
        self._state = None

        self.screen.blit(pygame.transform.scale(sprite_manager.get("./sprites/main_background.png"),
                                                (1600, 900)), (0, 0))

        for event in events:
            if event.type == pygame.QUIT:
                self._exit_the_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._exit_the_game()
        for button in buttons:
            button.draw(self.screen)
            button.update(events)
        self.screen.blit(
            pygame.transform.scale(sprite_manager.get("./sprites/gear.png"), (50,) * 2),
            (1525, 20))
        if self._state is None:
            self._state = State(GameState.FLIP, None)
        else:
            pygame.event.set_allowed(None)

        return self._state

    def on_init(self):
        '''
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        '''
        pygame.event.set_allowed(
            [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONUP])
        print("QUIT, KEYDOWN, MOUSEBUTTONUP")
