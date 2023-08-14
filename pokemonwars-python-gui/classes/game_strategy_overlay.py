import abc
from typing import List, Optional

import pygame

from classes.game_state import GameState
from classes.game_state_history import GameStateHistory
from classes.game_strategy import GameStrategy
from classes.state import State
from global_types import SURFACE, GAME_STRATEGY


class GameStrategyOverlay(GameStrategy):
    def __init__(self, overhead: GAME_STRATEGY, screen: SURFACE):
        if callable(overhead):
            overhead = overhead(screen)
        super().__init__(screen)
        self._history = GameStateHistory(screen)
        self._history.game_strategy = overhead

    @abc.abstractmethod
    def _inner_draw(self, events: List[pygame.event.Event], overhead_state: Optional[State],
                    delta_time_in_milliseconds: int) -> Optional[State]:
        return overhead_state

    @property
    def history(self) -> Optional["GameStateHistory"]:
        return self._history

    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        state = await self._history.game_strategy.draw(events, delta_time_in_milliseconds)
        state = self._inner_draw(events, state, delta_time_in_milliseconds)
        if state and not state.ignore_overlay and state.game_state in (GameState.SWITCH, GameState.BACK):
            self._history.process(state)
            state = None
        return state

    def on_init(self):
        self._history.game_strategy.on_init()
