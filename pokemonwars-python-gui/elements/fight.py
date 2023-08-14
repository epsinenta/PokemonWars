from typing import List, Optional
from random import randint

import pygame

from classes.button import Button
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.state import State
from global_types import SURFACE
from elements.global_classes import sprite_manager, GuiSettings
from classes.player_map import Player_Map
from classes.pokemon_map import Pokemon_Map


class Fight(GameStrategy):
    def __init__(self, screen: SURFACE, you: Player_Map, enemy: Player_Map):
        super().__init__(screen)
        self._state: Optional[State] = None
        self.you = you
        self.enemy = enemy
        self.your_flag_att = False
        self.enemy_flag_att = False
        self.timer_attack = 0
        self.flag_set_xy = True
        self.last_your_damage = 13
        self.flag_fly = False
        self.timer_fly = 0
        self.flag_you_can_attack = True
        self.y = randint(200, 400)
        self.x = randint(1000, 1200)

    def your_attack_animation(self):
        if pygame.time.get_ticks() - self.timer_attack < 300:
            self.screen.blit(
                pygame.transform.scale(sprite_manager.get(f"./sprites/att_enemy.png"), (200, 200)), (1000, 300))
            self.timer_fly = pygame.time.get_ticks()
        else:
            self.your_flag_att = False
            self.enemy_flag_att = True
            self.flag_set_xy = True
            self.timer_attack = pygame.time.get_ticks()

    def enemy_attack_animation(self):
        if pygame.time.get_ticks() - self.timer_attack < 300:
            self.screen.blit(
                pygame.transform.scale(sprite_manager.get(f"./sprites/att_you.png"), (200, 200)), (300, 300))
            self.timer_fly = pygame.time.get_ticks()
        else:
            self.enemy_flag_att = False
            self.flag_you_can_attack = True

    def flying_nums(self, x, y):
        font = pygame.font.Font("fonts/ConsolateElf.ttf", 30)
        render_line = font.render(f"-{self.last_your_damage}", True, (255, 0, 0))
        self.screen.blit(render_line, (x, y))

    def attack(self):
        self.your_flag_att = True
        self.flag_set_xy = True
        self.flag_fly = True
        self.flag_you_can_attack = False
        self.timer_attack = pygame.time.get_ticks()

    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """Отрисовывает бой
        :param events: События, собранные окном pygame
        :type events: List[pygame.event.Event]
        :param delta_time_in_milliseconds: Время между нынешним и предыдущим кадром (unused)
        :type delta_time_in_milliseconds: int
        :return: Возвращает состояние для правильной работы game_context
        """
        if self.flag_set_xy:
            self.y = randint(200, 400)
            self.x = randint(1000, 1200) if self.your_flag_att else randint(200, 400)
            self.flag_set_xy = False
        if pygame.time.get_ticks() - self.timer_fly < 1000:
            self.y -= 2
        else:
            self.flag_fly = False

        self.screen.blit(pygame.transform.scale(sprite_manager.get("./sprites/img_1.png"),
                                                (1600, 900)), (0, 0))
        self._state = None

        self.screen.blit(
            pygame.transform.scale(sprite_manager.get(f"./sprites/pokemons/1.png"), (600, 600)), (100, 100))
        self.screen.blit(
            pygame.transform.scale(sprite_manager.get(f"./sprites/pokemons/2.png"), (600, 600)), (800, 100))
        pygame.font.init()
        font = pygame.font.Font("fonts/ConsolateElf.ttf", 30)
        render_line = font.render("You", True, (244, 244, 244))
        self.screen.blit(render_line, (375, 70))
        render_line = font.render("Enemy", True, (244, 244, 244))
        self.screen.blit(render_line, (1050, 70))
        attack_btn = Button(1100, 800, 400, 50, (68, 68, 68), GuiSettings(), f"attack", self.attack)

        for event in events:
            if event.type == pygame.QUIT:
                self._state = State(GameState.BACK)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._state = State(GameState.BACK)

        attack_btn.draw(self.screen)
        if self.flag_you_can_attack:
            attack_btn.update(events)

        if self.enemy_flag_att:
            self.enemy_attack_animation()

        if self.your_flag_att:
            self.your_attack_animation()

        if self.flag_fly:
            self.flying_nums(self.x, self.y)

        if self._state is None:
            self._state = State(GameState.FLIP, None)
        return self._state

    def on_init(self):
        pass
