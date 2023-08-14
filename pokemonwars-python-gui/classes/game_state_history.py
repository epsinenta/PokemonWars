from typing import TYPE_CHECKING, List, Optional, Union

import pygame

import settings
from classes.game_state import GameState
from classes.state import State
from global_types import GAME_STRATEGY

if TYPE_CHECKING:
    from classes.game_strategy import GameStrategy


class GameStateHistory:
    """
    История состояний и стратегий
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._history: List["GameStrategy"] = []

    @property
    def game_strategy(self) -> "GameStrategy":
        """
        :setter: Устанавливает :class:`classes.game_strategy.GameStrategy` в игру

        :getter: Возвращает текущую :class:`classes.game_strategy.GameStrategy`
        """
        return self._history[-1]

    @property
    def nested_game_strategy(self) -> "GameStrategy":
        """:class:`classes.game_strategy.GameStrategy` которая в итоге и обрабатывается"""
        if self._history[-1].history is not None:
            strategy = self._history[-1].history.game_strategy
        else:
            strategy = self._history[-1]
        return strategy

    @game_strategy.setter
    def game_strategy(self, game_strategy: GAME_STRATEGY):
        if callable(game_strategy):
            game_strategy = game_strategy(self.screen)
        # Этот if нужен для корректной работы back
        if len(self._history) > 1 and self._history[-2] == game_strategy:
            del self._history[-1]
        else:
            self._history.append(game_strategy)
        self._init_game_strategy()
        if settings.DEBUG:
            print(f'Current game strategy is {game_strategy.__class__.__name__}; History: ', end="")
            print(self)

    def _init_game_strategy(self):
        pygame.event.set_blocked(pygame.SYSWMEVENT)
        # Unknown Windows 10 event that reduces performance

        self.game_strategy.on_init()

    def process(self, state: State):
        if state.game_state is GameState.SWITCH:
            self.game_strategy = state.switch_to
        elif state.game_state is GameState.BACK:
            if len(self._history) == 0:
                raise ValueError(
                    "Can't back; Use debug to show the history of strategies; ")
            self.game_strategy = self._history[-2]
        else:
            raise ValueError(f"Invalid state. GameStateHistory can't process this: {state}")

    def __str__(self):
        result = []
        stack = self._history.copy()
        for game_strategy in stack:
            if game_strategy.history is None:
                result.append(game_strategy.__class__.__name__)
            else:
                result.append(str(game_strategy.history))
        return str(result)
