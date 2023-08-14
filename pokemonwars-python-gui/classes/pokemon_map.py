from typing import Union, Sequence

import pygame

from elements.global_classes import GuiSettings, sprite_manager
from global_types import SURFACE

colors_id = {
    1: (156, 204, 196),
    2: (245, 176, 120),
    3: (173, 191, 218),
    4: (236, 186, 178),
    5: (228, 205, 137),
    6: (239, 229, 189),
    7: (231, 205, 195),
    8: (215, 194, 206),
    9: (250, 238, 196),
    10: (194, 220, 228),
    11: (212, 182, 215),
    12: (237, 214, 206),
    13: (240, 201, 210),
    14: (214, 158, 214),
    15: (163, 174, 197),
    16: (165, 161, 212),
    17: (197, 185, 198),
    18: (248, 240, 225),
    19: (243, 227, 215),
    20: (226, 229, 239),
}

border_id = {
    1: (88, 140, 129),
    2: (184, 93, 67),
    3: (125, 156, 193),
    4: (223, 132, 124),
    5: (144, 120, 59),
    6: (204, 119, 89),
    7: (213, 111, 109),
    8: (178, 163, 186),
    9: (238, 206, 120),
    10: (158, 190, 200),
    11: (158, 126, 162),
    12: (183, 142, 152),
    13: (204, 156, 173),
    14: (116, 76, 113),
    15: (95, 116, 148),
    16: (52, 52, 76),
    17: (117, 90, 88),
    18: (228, 189, 127),
    19: (188, 163, 147),
    20: (90, 126, 170),
}

text_id = {
    1: (34, 29, 31),
    2: (36, 29, 22),
    3: (19, 17, 20),
    4: (40, 40, 49),
    5: (41, 38, 42),
    6: (28, 22, 18),
    7: (20, 15, 14),
    8: (38, 33, 33),
    9: (26, 20, 15),
    10: (30, 43, 59),
    11: (20, 17, 20),
    12: (41, 35, 35),
    13: (26, 20, 15),
    14: (26, 30, 32),
    15: (26, 30, 32),
    16: (15, 13, 16),
    17: (17, 16, 15),
    18: (29, 27, 23),
    19: (25, 23, 23),
    20: (17, 16, 20)
}

over_id = {
    1: (140, 196, 196),
    2: (211, 150, 100),
    3: (149, 177, 219),
    4: (202, 160, 163),
    5: (214, 179, 88),
    6: (211, 193, 155),
    7: (221, 179, 180),
    8: (194, 183, 205),
    9: (243, 227, 170),
    10: (184, 228, 232),
    11: (196, 164, 199),
    12: (202, 172, 174),
    13: (224, 191, 198),
    14: (165, 114, 167),
    15: (114, 126, 155),
    16: (107, 102, 159),
    17: (171, 155, 162),
    18: (234, 210, 171),
    19: (228, 188, 164),
    20: (166, 189, 213),
}


class Pokemon_Map:
    def __init__(self, x: int, y: int, id: int, name: str, health: int, damage: int, defense: int,
                 alive: bool, typePokemon: str = "", typeAdvantages: str = "", typeWeaknesses: str = ""):
        self.x = x
        self.y = y
        self.id = id
        self.name = name
        self.health = health
        self.damage = damage
        self.defense = defense
        self.alive = alive
        self.typePokemon = typePokemon
        self.typeAdvantages = typeAdvantages
        self.typeWeaknesses = typeWeaknesses
        self.color = colors_id[id]
        self.border_color = border_id[id]
        self.color_for_text = (0, 0, 0)
        self.width = 230
        self.height = 330
        self.text_color = text_id[id]
        self.height_rect = self.height * 1 / 3 / 4 - 1

    def draw(self, screen: "SURFACE", pos):
        """
        Метод отрисовки карточки покемона

        :param screen: Surface, на котором будет происходить отрисовка
        :pos: Позиция указателя мыши
        """
        if self.is_over(pos):
            color = over_id[self.id]
        else:
            color = self.color
        pygame.font.init()
        pygame.draw.rect(screen, self.border_color, (self.x - 4,
                                                     self.y - 4, self.width + 8, self.height + 8), 0)
        pygame.draw.rect(screen, color, (self.x,
                                         self.y, self.width, self.height), 0)
        screen.blit(
            pygame.transform.scale(sprite_manager.get(f"./sprites/pokemons/{self.id}.png"),
                                   (self.width, self.height * 2 / 3)),
            (self.x, self.y))

        font = pygame.font.Font("fonts/ConsolateElf.ttf", 20)

        render_line = font.render(f"{self.name}", True, self.text_color)
        screen.blit(render_line, (self.x + (self.width - render_line.get_width()) / 2,
                                  self.y + self.height * 2 // 3 - 15))

        render_line = font.render(f"Type: {self.typePokemon}", True, self.text_color)
        screen.blit(render_line, (self.x + (self.width - render_line.get_width()) / 2, self.y + self.height * 2 // 3 +
                                  (self.height_rect + 1) - 2 - 15))

        pygame.draw.rect(screen, (255, 0, 0), (self.x + (self.width - int(self.width * self.health / 100) - 2) / 2 + 2,
                                               self.y + self.height * 2 / 3 + 2 * self.height_rect + 4 - 15,
                                               int(self.width * self.health / 100) - 2, self.height_rect - 2), 0)

        render_line = font.render(f"HP: {self.health}/100", True, self.text_color)
        screen.blit(render_line, (self.x + (self.width - render_line.get_width()) / 2,
                                  self.y + self.height * 2 / 3 + 2 * self.height_rect + 2 - 15))

        render_line = font.render(f"ATK: {self.damage}", True, self.text_color)
        screen.blit(render_line, (self.x + (self.width / 2 - render_line.get_width()) / 2,
                                  self.y + self.height * 2 // 3 + 3 * (self.height_rect + 1) - 15))

        render_line = font.render(f"DEF: {self.defense}", True, self.text_color)
        screen.blit(render_line, (self.x + self.width / + 2 + (self.width / 2 - render_line.get_width()) / 2,
                                  self.y + self.height * 2 // 3 + 3 * (self.height_rect + 1) - 15))

    def is_over(self, pos: Sequence[Union[int, float]]) -> bool:
        """
        Проверка координат на нахождение внутри области кнопки

        :param pos: Абсцисса и Ордината для проверки наведения

        :return: True, если Абсцисса и Ордината находится в области кнопки, иначе False.
        """

        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False
