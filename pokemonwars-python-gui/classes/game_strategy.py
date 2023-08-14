import abc
from typing import List, Optional, TYPE_CHECKING

import pygame

from classes.state import State
from global_types import SURFACE

if TYPE_CHECKING:
    from game_state_history import GameStateHistory


class GameStrategy(abc.ABC):
    """
    Абстрактный класс, необходимый для определения отрисовки меню в GameContext.

    :ivar screen: Экран на котором будет происходить вся отрисовка.
    """

    def __init__(self, screen: SURFACE):
        self.screen: SURFACE = screen

    @abc.abstractmethod
    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """

        :param events: Cписок событий
        :param delta_time_in_milliseconds: время прошедшее между кадрами для не зависимого от FPS, движения
        :return: Изменение в игре, см. :class:`classes.game_state.GameState`

        .. note::
            Если этот метод вернёт None, то ничего, в том числе и обновление экрана, не произойдёт.
            Для обновления экрана, верните State(GameState.flip)
        """
        ...

    @abc.abstractmethod
    def on_init(self):
        ...

    @property
    def history(self) -> Optional["GameStateHistory"]:
        return None
