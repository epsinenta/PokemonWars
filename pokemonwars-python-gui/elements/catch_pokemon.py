from typing import List, Optional

import pygame

from classes.button import Button
from classes.input import Input
from classes.game_state import GameState
from classes.game_strategy import GameStrategy
from classes.state import State
from global_types import SURFACE
from elements.global_classes import sprite_manager, GuiSettings


class Catch_Pokemon(GameStrategy):
    def __init__(self, screen: SURFACE):
        super().__init__(screen)
        self._state: Optional[State] = None
        '''
        TODO: Баланс и количество покеболов брать с Game
        '''
        self.balance = 123
        self.pokebals_count = 123
        self.inputs = []
        self.res_inputs = [0, 0]
        self.warnings_input_flags = [False, False]
        self.timer_flag = False
        self.timer_warnings = 0
        self.flag_animation = False

    def catch(self):
        '''
        TODO: Рандомим id покемона, создаем экземпляр контракта покемона и вызываем catchPokemon у Player'a
        '''
        if self.pokebals_count > 0:
            self.pokebals_count -= 1
            self.flag_animation = True

    def buy_pokebals(self):
        '''
        TODO: Вызываем функцию buyPokeballs
        '''
        try:
            self.pokebals_count += int(self.res_inputs[0])
        except:
            self.warnings_input_flags[0] = True

    def deposit(self):
        '''
        TODO: Вызываем функцию donate
        '''
        try:
            self.balance += int(self.res_inputs[1])
        except:
            self.warnings_input_flags[1] = True

    def init_inputs(self):
        self.inputs = [
            Input(50, 100, 200, 40, (68, 68, 68), GuiSettings(), "Input"),
            Input(1250, 100, 200, 40, (68, 68, 68), GuiSettings(), "Input")
        ]

    def show_text(self):
        font = pygame.font.Font("fonts/ConsolateElf.ttf", 30)
        render_line = font.render(f"You have {self.pokebals_count} pokebals", True, (244, 244, 244))
        self.screen.blit(render_line, (50, 20))
        render_line = font.render(f"Your balance: {self.balance} RUB", True, (244, 244, 244))
        self.screen.blit(render_line, (1050, 20))

    def animation(self):
        pass

    def show_warnings(self):
        font = pygame.font.Font("fonts/ConsolateElf.ttf", 30)
        if self.warnings_input_flags[0]:
            render_line = font.render("enter a number", True, (244, 244, 244))
            self.screen.blit(render_line, (50, 200))
            if not self.timer_flag:
                self.timer_warnings = pygame.time.get_ticks()
                self.timer_flag = True
        elif self.warnings_input_flags[1]:
            render_line = font.render("enter a number", True, (244, 244, 244))
            self.screen.blit(render_line, (1050, 200))
            if not self.timer_flag:
                self.timer_warnings = pygame.time.get_ticks()
                self.timer_flag = True
        else:
            render_line = font.render("enter a number", True, (244, 244, 244))
            self.screen.blit(render_line, (1050, 200))
            render_line = font.render("enter a number", True, (244, 244, 244))
            self.screen.blit(render_line, (50, 200))
            if not self.timer_flag:
                self.timer_warnings = pygame.time.get_ticks()
                self.timer_flag = True

    async def draw(self, events: List[pygame.event.Event], delta_time_in_milliseconds: int) -> Optional[State]:
        """
        Отрисовывает ловлю покемонов

        :param events: События, собранные окном pygame
        :type events: List[pygame.event.Event]
        :param delta_time_in_milliseconds: Время между нынешним и предыдущим кадром (unused)
        :type delta_time_in_milliseconds: int
        :return: Возвращает состояние для правильной работы game_context
        """
        if not self.flag_animation:
            buttons = [
                Button(1250, 150, 200, 40, (68, 68, 68), GuiSettings(), f"Deposit", self.deposit),
                Button(50, 150, 200, 40, (68, 68, 68), GuiSettings(), f"Buy", self.buy_pokebals),
                Button(700, 825, 200, 50, (68, 68, 68), GuiSettings(), f"Catch", self.catch)
            ]

            if not len(self.inputs):
                self.init_inputs()
            self.screen.blit(pygame.transform.scale(sprite_manager.get("./sprites/img.jpg")
                                                    , (1600, 900)), (0, 0))
            self.screen.blit(pygame.transform.scale(sprite_manager.get("./sprites/pokebal.png")
                                                    , (500, 500)), (550, 200))
            self.show_text()
            self._state = None

            for index, input in enumerate(self.inputs):
                input.draw(self.screen)
                input.update(events)
                self.res_inputs[index] = input.__str__()

            for button in buttons:
                button.draw(self.screen)
                button.update(events)

            if self.warnings_input_flags[0] or self.warnings_input_flags[1]:
                self.show_warnings()
                if pygame.time.get_ticks() - self.timer_warnings > 200:
                    self.warnings_input_flags[0] = False
                    self.warnings_input_flags[1] = False
                    self.timer_flag = False
        else:
            self.screen.blit(pygame.transform.scale(sprite_manager.get("./sprites/catch_pokemons.jpg")
                                                    , (1600, 900)), (0, 0))
            self.animation()

        for event in events:
            if event.type == pygame.QUIT:
                self._state = State(GameState.BACK)
                '''
                TODO: Статус онлайна поменять на false
                '''
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    '''
                    TODO: Статус онлайна поменять на false
                    '''
                    self._state = State(GameState.BACK)

        if self._state is None:
            self._state = State(GameState.FLIP, None)
        return self._state

    def on_init(self):
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
