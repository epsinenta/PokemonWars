import abc
from dataclasses import dataclass
from typing import Optional

from contracts_api import Web3Manager
from global_types import COLOR
from classes.sprite_manager import SpriteManager


class AbstractButtonSettings(abc.ABC):
    @property
    @abc.abstractmethod
    def text_size(self) -> int:
        ...

    @property
    @abc.abstractmethod
    def button_color(self) -> "COLOR":
        ...

    @property
    @abc.abstractmethod
    def button_color_hover(self) -> "COLOR":
        ...

    @property
    @abc.abstractmethod
    def text_color(self) -> "COLOR":
        ...


@dataclass
class GuiSettings(AbstractButtonSettings):
    text_size: int = 32
    text_color: "COLOR" = (16, 16, 16)
    button_color: "COLOR" = (255, 255, 255)
    button_color_hover: "COLOR" = (240, 240, 240)


sprite_manager = SpriteManager()
web3_manager: Optional[Web3Manager] = None
