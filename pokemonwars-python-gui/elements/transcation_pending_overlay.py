from typing import List, Optional

import pygame

import elements.global_classes
from classes.game_state import GameState
from classes.game_strategy_overlay import GameStrategyOverlay
from classes.state import State
from global_types import SURFACE, GAME_STRATEGY


class TransactionPendingOverlay(GameStrategyOverlay):
    def __init__(self, overhead: GAME_STRATEGY, screen: SURFACE):
        super().__init__(overhead, screen)
        self._image = pygame.transform.scale(elements.global_classes.sprite_manager.get("sprites/waiting.png"),
                                             (138, 96))
        self._angle: float = 0.0
        self._font = pygame.font.Font("fonts/ConsolateElf.ttf", 16)
        self._need_to_stop = False
        self._previous_angle: float = -1.0

    def _inner_draw(self, events: List[pygame.event.Event], overhead_state: Optional[State],
                    delta_time_in_milliseconds: int) -> Optional[State]:
        web3_initialized = elements.global_classes.web3_manager is not None
        if web3_initialized:
            calls_count = len(elements.global_classes.web3_manager.pending_calls)

            if overhead_state and overhead_state.game_state is GameState.STOP and calls_count > 0:
                self._need_to_stop = True
                overhead_state = None
            if not calls_count:
                return State(GameState.STOP) if self._need_to_stop else overhead_state

            text = self._font.render(f"{calls_count} transactions pending block", True, (64, 0, 0), (80, 100, 80))
            text_width, text_height = text.get_size()

            self._angle += 0.04*delta_time_in_milliseconds
            if self._angle > 359:
                self._angle = 0
            # Если поменялся угол и оверхед не поворачивает экран, мы его повернём
            if int(self._angle) != self._previous_angle and overhead_state is None:
                overhead_state = State(GameState.FLIP)
                self._previous_angle = True
            image = pygame.transform.rotate(self._image, self._angle)
            image_width, image_height = image.get_size()

            self.screen.blit(text, (20, self.screen.get_height() - 20))
            self.screen.blit(image,
                             (20 + text_width // 2 - image_width // 2,
                              self.screen.get_height() - image_height - text_height))
        return overhead_state

    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        if self._need_to_stop:
            return self._inner_draw(events, State(GameState.STOP), delta_time_in_milliseconds)
        return await super().draw(events, delta_time_in_milliseconds)
