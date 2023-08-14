import asyncio
from asyncio import CancelledError
from typing import Final, TYPE_CHECKING, Callable, List, Union, Type

import pygame

import settings
from classes.game_state import GameState
from classes.game_state_history import GameStateHistory
from global_types import SURFACE, GAME_STRATEGY
from settings import FRAMES_PER_SECOND

if TYPE_CHECKING:
    from classes.game_strategy import GameStrategy


class GameContext:
    """
    Основной класс игры вокруг которого всё будет крутиться.

    :ivar screen: Экран на котором будет всё отрисовываться
    """

    def __init__(self, game_strategy: Union[Callable[[SURFACE], "GameStrategy"], Type["GameStrategy"]]):
        """
        Инициализация класса

        :param game_strategy: GameStrategy которая будет отрисовываться по умолчанию.
        """
        settings.RESOLUTION = (1600, 900)
        self.screen: Final[SURFACE] = pygame.display.set_mode(settings.RESOLUTION)
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.scrap.init()
        self._clock = pygame.time.Clock()
        self._running: bool = True
        self._history: GameStateHistory = GameStateHistory(self.screen)
        self._history.game_strategy = game_strategy

    @property
    def game_strategy(self) -> "GameStrategy":
        """
        :setter: Устанавливает :class:`classes.game_strategy.GameStrategy` в игру

        :getter: Возвращает текущую :class:`classes.game_strategy.GameStrategy`
        """
        return self._history.game_strategy

    @game_strategy.setter
    def game_strategy(self, game_strategy: GAME_STRATEGY):
        self._history.game_strategy = game_strategy

    @property
    def running(self) -> bool:
        """
        :setter: Устанавливает переменную в основном цикле игры. Если False игра выключится

        :return: Запущена ли игра?
        """
        return self._running

    @running.setter
    def running(self, value: bool):
        self._running = value

    async def _frame_process(self):
        """Функция отрисовки и обработки кадра"""
        loop = asyncio.get_event_loop()
        delta_time = (await asyncio.gather(loop.run_in_executor(None, self._clock.tick, FRAMES_PER_SECOND)))[0]
        pygame.display.set_caption(f"FPS: {round(self._clock.get_fps())} in "
                                   f"{self._history.nested_game_strategy.__class__.__name__} ")
        events = pygame.event.get()
        draw_state = await self.game_strategy.draw(events, delta_time)

        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.play()
            except pygame.error:
                pass

        if draw_state is not None:
            if draw_state.game_state is GameState.STOP:
                raise KeyboardInterrupt
            elif draw_state.game_state is GameState.FLIP:
                await loop.run_in_executor(None, pygame.display.flip)
            else:
                self._history.process(draw_state)

    async def run(self):
        """Функция запуска игры"""
        while self.running:
            try:
                await self._frame_process()
            except (KeyboardInterrupt, CancelledError):
                self.running = False
