from typing import Union, Tuple, Callable

import pygame

COLOR = Union[pygame.Color, pygame.color.Color, int, Tuple[int, int, int], Tuple[int, int, int, int], str]
SURFACE = Union[pygame.surface.Surface, pygame.Surface]
GAME_STRATEGY = Union[Callable[[SURFACE], "GameStrategy"], "GameStrategy"]
