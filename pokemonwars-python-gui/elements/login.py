from typing import List, Optional

import pygame

import elements.global_classes
import settings
from classes.button import Button
from classes.input import Input
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.state import State
from contracts_api import Web3Manager, AbiDownloader, Network
from elements.global_classes import GuiSettings, sprite_manager
from elements.main_menu import MainMenu
from global_types import SURFACE


class Login(GameStrategy):
    """
    Стратегия страницы авторизации
    """

    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        self.screen.set_alpha(None)
        self._state: Optional[State] = None
        self.inputs = []
        self.is_init = False

    def init_inputs(self):
        centered_x = settings.RESOLUTION[0] // 2 - 200
        centered_y = settings.RESOLUTION[1] // 2
        self.inputs = [
            Input(centered_x, centered_y - 180, 400, 50, (68, 68, 68), GuiSettings(), "?etherscan api key?"),
            Input(centered_x, centered_y - 120, 400, 50, (68, 68, 68), GuiSettings(), "!INFURA API KEY!"),
            Input(centered_x, centered_y - 60, 400, 50, (68, 68, 68), GuiSettings(), "!PLAYER ADDRESS!")
        ]

    def _main(self):
        '''
        TODO: сохранять введеный ардес игрока, для последущего вызова с него функций Player'a
        Ставить статус онлайн true
        '''
        self._state = State(GameState.SWITCH, MainMenu)
        elements.global_classes.web3_manager = Web3Manager(
            self.inputs[1].text, Network.GOERLI,
            AbiDownloader(self.inputs[0].text if self.inputs[0].text else None)
        )

    def _exit_the_game(self):
        self._state = State(GameState.STOP)

    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int):
        self.screen.blit(pygame.transform.scale(sprite_manager.get("./sprites/img.jpg")
                                                , (1600, 900)), (0, 0))
        self._state = State(GameState.FLIP) if not self.inputs or events else None
        centered_x = settings.RESOLUTION[0] // 2 - 200
        centered_y = settings.RESOLUTION[1] // 2

        buttons = [
            Button(centered_x,
                   centered_y + 30, 400, 50, (68, 68, 68), GuiSettings(), f"login",
                   self._main),
        ]

        for event in events:
            if event.type == pygame.QUIT:
                self._exit_the_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._exit_the_game()

        for input in self.inputs:
            input.draw(self.screen)
            input.update(events)
        for button in buttons:
            button.draw(self.screen)
            button.update(events)

        return self._state

    def on_init(self):
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONUP])
        self.init_inputs()
